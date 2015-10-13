# -*- coding: utf-8 -*-

from hashlib import md5

from models import CustomerModel, SystemModel
from settings import logger

realm = 'Registered address: www.doubi.so'
fail = 'The user name or password error'
no_money = 'You have no traffic!'

def basicAuth(func):
    """用户验证"""
    def wrapper(*args, **kwargs):
        self = args[0]
        auth_header = self.request.headers.get('Proxy-Authorization', None)
        if auth_header is not None:
            customer = CustomerModel()
            auth_mode, auth_base64 = auth_header.split(' ', 1)
            assert auth_mode == 'Basic'
            username, password = auth_base64.decode('base64').split(':', 1)
            self.username = username
            if customer.checkPassword(username, password):
                if customer.checkTraffic(username):
                    return func(*args, **kwargs)
                else:
                    if self.request.headers.has_key('Proxy-Authorization'):
                        del self.request.headers['Proxy-Authorization']
                    self.set_status(407)
                    self.set_header('Proxy-Authenticate', 'Basic realm="%s"' % no_money)
                    logger.info(username + ':' + no_money)
                    self.write("请交钱")
                    self.finish()
            else:
                self.set_status(407)
                self.set_header('Proxy-Authenticate', 'Basic realm="%s"' % fail)
                logger.info(username + ':' + fail)
                self.finish()

        else:
            self.set_status(407)
            self.set_header('Proxy-Authenticate', 'Basic realm="%s"' % realm)
            logger.info(realm)
            self.finish()
    return wrapper


def checkDomainInWhiteList(func):
    """查看请求地址是否在白名单中，如果不在白名单，将proxy_host， proxy_port改为None"""
    def wrapper(*args, **kwargs):
        self = args[0]
        #customer = CustomerModel()
        #if not customer.checkDomain(self.request.host):
        #    self.proxy_host = None
        #    self.proxy_port = None
        return func(*args, **kwargs)
    return wrapper


def go(func):
    """运行装饰起下的程序，根据proxyhost 和proxyport是否为None"""
    def wrapper(*args, **kwargs):
        self = args[0]
        handle, common = func(*args, **kwargs)
        if self.proxy_host and self.proxy_port and self.encode:
            return handle()
        else:
            return common()
    return wrapper

def checkWall(func):
    """如果地址不能访问，如果不在白名单就加入白名单，在白名单就从白名单中删除"""
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.wall:
            SystemModel().alertWhiteList(self.request.host)
        return func(*args, **kwargs)
    return wrapper
