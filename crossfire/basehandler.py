# -*- coding: utf-8 -*-
import socket
import traceback
import logging
import collections

import tornado.httpclient
import tornado.gen
import tornado.web
import utils
from tornado.iostream import StreamClosedError

logger = logging.getLogger('tornado_proxy')

class BaseHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'OPTIONS', 'CONNECT']
    RESPONSE_HEADERS = ('Content-Length', 'Transfer-Encoding', 'Content-Encoding')

    def initialize(self):
        #流量系数
        self.N = 4
        self._traffic = (len(self.request.uri) + len(str(self.request.headers)) + len(str(self.request.files)) + len(str(self.request.body)))
        self.username = None
        #用于存储加密或者解密后的头信息
        self.headers = self.request.headers
        self.uri = self.request.uri
        self.host = self.request.host
        self.method = self.request.method
        self.body = self.request.body if self.request.body else None
        self.files = self.request.files if self.request.files else None
        #是否被墙标志位 False表示没有 True表示被墙
        self.wall = False

    def prepare(self):
        pass

    @tornado.gen.coroutine
    def base(self):
        try:
            resp = yield self._handle_http_request()
        except tornado.httpclient.HTTPError as e:
            if hasattr(e, 'response') and e.response:
                data = self._handle_http_response(e.response)
                if data:
                    self.write(data)
                self.finish()
            else:
                if e.code == 599:
                    logger.debug("[gfw] 以下网址可能被墙了...:" + self.request.uri)
                    self.wall=True
                logger.error(self.request.method+" "+self.request.uri+" "+str(e))
                logger.error(self.request.method+" "+self.uri+" "+str(e))
        except Exception as e:
            #logger.error(self.request.method+" "+self.request.uri+" "+str(e))
            #logger.error(self.request.method+" "+self.uri+" "+str(e))
            pass
        else:
            data = self._handle_http_response(resp)
            if data:
                self._traffic += len(data)
                self.write(data)
            self.finish()
        #流量监控
        self.sum_traffic(self._traffic * self.N)
        logger.debug("本次请求消耗流量：%d" % (self._traffic * self.N))

    def get(self):
        return self.base()

    def post(self):
        return self.base()

    def options(self):
        return self.base()

    @tornado.gen.coroutine
    def _handle_http_request(self):
        """处理请求数据"""
        self.http_request_body()
        self.http_request_header()
        kwargs = {}
        if self.proxy_host and self.proxy_port:
            kwargs['proxy_host'] = self.proxy_host
            kwargs['proxy_port'] = self.proxy_port
            tornado.httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')
        req = tornado.httpclient.HTTPRequest(
                self.uri, 
                method=self.request.method, 
                body=self.body, 
                headers=self.headers, 
                follow_redirects=False, 
                allow_nonstandard_methods=True,
                **kwargs)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield client.fetch(req)
        raise tornado.gen.Return(resp)

    def _handle_http_response(self,response):
        """处理请求结果数据"""
        if (response.error and not isinstance(response.error, tornado.httpclient.HTTPError)):
            self.set_status(500)
            logger.error(self.request.method+":"+self.request.uri+":"+str(response.error))
        else:
            self.set_status(response.code)
            for header, value in response.headers.items():
                if header not in self.RESPONSE_HEADERS and header != 'Set-Cookie':
                    self.set_header(header, value)
            v = response.headers.get_list('Set-Cookie')
            if v:
                for i in v:
                    self.add_header('Set-Cookie', i)
            if response.body:
                return self.http_response_body(response)
            else:
                return None

    @tornado.gen.coroutine
    def connect(self):
        def client_close_callback():
            #客户端关闭才停止流量计算
            self.sum_traffic(self._traffic * self.N)
            logger.info("本次请求消耗流量：%d" % (self._traffic * self.N))
            self.on_finish()

        def upstream_close_callback():
            pass

        #解析https的url
        self.https_request_header()
        client = self.request.connection.stream
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = tornado.iostream.IOStream(s)
        #流量监控
        #下面写给转发服务器的也要进行加密
        client.set_close_callback(client_close_callback)
        upstream.set_close_callback(upstream_close_callback)
        if self.proxy_host and self.proxy_port:
            try:
                yield upstream.connect((self.proxy_host, self.proxy_port))
            except Exception as e:
                self.set_status(500)
                logger.error(self.method+" "+self.uri+" "+str(e))
            resp = yield self._handle_https_request(upstream)
            self._handle_https_response(client, upstream, resp)
        else:
            host, port = self._host_port
            try:
                yield upstream.connect((host, port))
            except Exception as e:
                self.set_status(500)
                logger.debug("[gfw] 以下网址可能被墙了...:" + self.request.uri)
                self.wall = True
                logger.error(self.request.method+" "+self.uri+" "+str(e))
                self.finish()
            else:
                self._start_tunnel(client, upstream)

    @property
    def _host_port(self):
        """解密host port 只有在proxy的https下会用到"""
        host, port = self.uri.split(':')
        return host, int(port)

    @tornado.gen.coroutine
    def _handle_https_request(self, upstream):
        data = "%s %s HTTP/1.1\r\nHost: %s\r\nConnection: Keep-Alive\r\n\r\n" % (self.method, self.uri, self.uri)
        try:
            yield upstream.write(data)
        except StreamClosedError:
            logger.debug("[gfw] 以下网址可能被墙了...:" + self.request.uri)
        else:
            logger.info("write upstream Connect:" + self.request.uri)
        try:
            #读取上游服务器类似这类的信息：'HTTP/1.0 200 Connection established\r\n\r\n'
            resp = yield upstream.read_until('\r\n\r\n')
        except StreamClosedError:
            logger.error("[gfw] 以下网址可能被墙了:" + self.request.uri)
        else:
            raise tornado.gen.Return(resp)

    @tornado.gen.coroutine
    def _handle_https_response(self, client, upstream, response=None):
        if response:
            first_line = response.splitlines()[0]
            http_v, status, text = first_line.split(None, 2)
            if int(status) == 200:
                self._start_tunnel(client, upstream)
            else:
                client.close()
                upstream.close()
        else:
            client.close()
            upstream.close()


    @tornado.web.asynchronous
    def _start_tunnel(self, client, upstream):

        def read_from_client(data):
            if data:
                self._traffic += len(data)
                upstream.write(data)

        def read_from_upstream(data):
            if data:
                self._traffic += len(data)
                client.write(data)

        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                self._traffic += len(data)
                upstream.write(data)
            upstream.close()

        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                self._traffic += len(data)
                client.write(data)
            client.close()

        client.read_until_close(client_close, read_from_client)
        upstream.read_until_close(upstream_close, read_from_upstream)
        try:
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')
        except StreamClosedError:
            logger.warning("客户端关闭了连接:" + self.request.uri)
        else:
            logger.debug(self.request.method+' '+"client.write HTTP/1.0 200 Connection established")

    def sum_traffic(self, traffic):
        """处理流量统计"""
        pass

    def http_request_header(self):
        """处理request header"""
        pass

    def http_request_body(self):
        """处理request body"""
        pass

    def http_response_body(self, response):
        """处理response.body"""
        return response.body

    def https_request_url(self):
        """处理self.request.url"""
        pass
