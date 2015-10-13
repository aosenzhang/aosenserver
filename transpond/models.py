# -*- coding: utf-8 -*-

#models基类

import datetime

from tornado.options import options

import torndb

from settings import DATABASES

class BaseModel(object):
    """models基类"""

    def __init__(self):
        pass

    @property
    def db(self):
        return torndb.Connection(
                DATABASES['HOST']+':'+DATABASES['PORT'], 
                DATABASES['NAME'],
                user=DATABASES['USER'], 
                password=DATABASES['PASSWORD']
                )

class SystemModel(BaseModel):
    """系统模块模型"""
    def loadConfig(self):
        """从数据库加载系统配置文件"""
        transpond = options.id
        sql = "SELECT * FROM config WHERE transpond=%s"
        return self.db.get(sql, transpond)

    def alertWhiteList(self, host):
        sql_insert = "INSERT INTO whitelist (domain, createtime) VALUES (%s, %s)"
        sql_delete = "DELETE FROM whitelist WHERE domain=%s"
        try:
            self.db.insert(sql_insert, host, datetime.date.today())
        except Exception as e:
            pass

    def searchDns(self, url):
        """查询DNS"""
        sql = "SELECT * FROM dns WHERE src=%s"
        return self.db.get(sql, url)

class CustomerModel(BaseModel):
    """用户验证模型"""
    def getCustomer(self, username):
        sql = "SELECT * FROM customer WHERE username=%s"
        return self.db.get(sql, username)

    def checkPassword(self, username, password):
        customer = self.getCustomer(username)
        if customer:
            if customer['password'] == password:
                return True
            else:
                return False
        else:
            return False

    def checkDomain(self, host):
        "检测域名是否在白名单中，在返回False:不走proxy, 反之True:走代理"
        sql = "SELECT * FROM whitelist WHERE domain=%s"
        if self.db.get(sql, host):
            return True
        else:
            for domain in ['.'.join(host.split('.')[-i:]) for i in [2, 3, 4,]]:
                if self.db.get(sql, domain):
                    return True
        return False

    def checkTraffic(self, username):
        customer = self.getCustomer(username)
        if customer['flow'] <= 0:
            return False
        else:
            return True

    def computeTraffic(self, username, traffic):
        sql = "UPDATE customer SET flow=flow+%s WHERE username=%s"
        self.db.execute(sql, traffic, username)
