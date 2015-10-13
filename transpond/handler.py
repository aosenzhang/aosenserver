# -*- coding: utf-8 -*-

import socket
import sys
import zlib
import urllib
from urlparse import urlparse


import tornado.httpclient
import tornado.gen
import tornado.web

sys.path.append('../../')
from aosenserver.crossfire.handledata import encode_data, decode_data 
from aosenserver.crossfire.basehandler import BaseHandler
from aosenserver.conf import VHOST, VHOSTURL, KEY
from aosenserver.conf import HEADERS
from aosenserver.conf import GET, POST, CONNECT

from models import SystemModel, CustomerModel
from settings import logger
import utils

class TranspondHandler(BaseHandler):

    def initialize(self):
        super(TranspondHandler, self).initialize()  
        system = SystemModel().loadConfig()
        if system:
            self.proxy_host = system['proxy_host']
            self.proxy_port = system['proxy_port']
            self.encode = system['encode']
        else:
            self.proxy_host = None
            self.proxy_port = None
            self.encode = False
        self.key = KEY
        self.switch = {
                'GET': GET,
                'POST': POST,
                'CONNECT': CONNECT,
                }

    #@utils.basicAuth
    @utils.checkDomainInWhiteList
    def prepare(self):
        super(TranspondHandler, self).prepare()  
        #进行域名解析
        self.dns()

    @utils.checkWall
    def on_finish(self):
        pass


    @utils.go
    def http_request_header(self):
        def handleProxy():
            #将proxy-connection更改为connection
            if self.headers.has_key('Proxy-Connection'):
                del self.headers['Proxy-Connection']
            if not self.headers.has_key('Connection'):
                self.headers.add('Connection', 'keep-alive')
            if self.headers.has_key('Proxy-Authorization'):
                del self.headers['Proxy-Authorization']
            for k in ['If-None-Match', 'If-Modified-Since']:
                if self.headers.has_key(k):
                    del self.headers[k]

        def handle():
            """如果url在白名单 加密request header"""
            #加密url
            self.uri = VHOSTURL % (
                    self.switch.get(self.request.method, None),
                    encode_data(KEY, self.request.host), 
                    encode_data(KEY, self.request.uri)
                    )
            #更改Host
            self.host = VHOST
            #加密header中的敏感字段
            if self.headers.has_key('Host'):
                self.headers['Host'] = VHOST
            for h in HEADERS:
                if self.headers.has_key(h):
                    self.headers[h] = encode_data(self.key, self.request.headers[h])
            handleProxy()

        def common():
            """如果不在白名单 正常处理request header"""
            handleProxy()
        return handle, common

    @utils.go
    def http_response_body(self, response):
        def handle():
            """解密response.body"""
            if response.body:
                try:
                    return decode_data(self.key, response.body)
                except Exception as e:
                    return response.body
        def common():
            if response.body:
                return response.body
        return handle, common

    @utils.go
    def https_request_header(self):
        def handle():
            """加密connect request url 并更改请求方法"""
            self.uri = VHOSTURL % (
                    self.switch.get(self.request.method, None),
                    encode_data(KEY, self.request.host), 
                    encode_data(KEY, self.request.uri)
                    )
            self.method = 'GET'
        
        def common():
            pass
        return handle, common

    def sum_traffic(self, traffic):
        """重写父累流量统计"""
        customer = CustomerModel()
        return customer.computeTraffic(self.username, -traffic)

    def dns(self):
        """域名解析 不支持https"""
        d = SystemModel()
        url = urlparse(self.request.uri)
        if url.scheme == 'http':
            ret = d.searchDns(url.netloc)
            if ret:
                self.redirect(ret['des'])
