# -*- coding: utf-8 -*-

import socket
import sys
import zlib
import urllib

import tornado.httpclient
import tornado.gen
import tornado.web

from settings import PROXY_HOST, PROXY_PORT, logger
import utils

sys.path.append('../../')
from aosenserver.crossfire.handledata import encode_data, decode_data 
from aosenserver.crossfire.basehandler import BaseHandler
from aosenserver.conf import VHOST, VHOSTURL, KEY
from aosenserver.conf import HEADERS
from aosenserver.conf import GET, POST, CONNECT

class ProxyHandler(BaseHandler):

    def initialize(self):
        super(ProxyHandler, self).initialize()  
        self.proxy_host = PROXY_HOST
        self.proxy_port = PROXY_PORT
        self.key = KEY
        self.m = self.get_query_argument('m')
        self.h = decode_data(KEY,self.get_query_argument('h'))
        self.v = decode_data(KEY,self.get_query_argument('v'))

    @utils.checkIp
    def prepare(self):
        #将https伪装的GET方法更改回CONNECT
        super(ProxyHandler, self).prepare()  
        if self.m == CONNECT:
            self.request.method = 'CONNECT'
        logger.info(self.request.method+' '+VHOSTURL % (self.m, self.h, self.v))

    def http_request_header(self):
        """解密request header"""
        #解密url
        self.uri = self.v
        if self.headers.has_key('Host'):
            self.headers['Host'] = self.h
        #解密header中的敏感字段
        for h in HEADERS:
            if self.headers.has_key(h):
                self.headers[h] = decode_data(self.key, self.request.headers[h])

    def http_response_body(self, response):
        """加密response.body"""
        if response.body:
            try:
                return encode_data(self.key, response.body)
            except Exception as e:
                return response.body

    def https_request_header(self):
        """解密self.request.url"""
        self.uri = self.v
        self.method = 'CONNECT'
