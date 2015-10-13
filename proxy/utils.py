# -*- coding: utf-8 -*-

from settings import ALLOW_IP, logger

def checkIp(func):
    """验证是否为转发服务器发过来的消息，如果不是直接拒绝"""
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.request.remote_ip not in ALLOW_IP:
            self.set_status(500)
            self.finish()
            logger.warning("该IP请求不合法"+self.request.remote_ip)
        else:
            return func(*args, **kwargs)
    return wrapper

