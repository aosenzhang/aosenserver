# -*- coding: utf-8 -*-

from django.db import models

class Customer(models.Model):
    """客户信息"""
    username = models.CharField(verbose_name="用户名", unique=True, max_length=50)
    password = models.CharField(verbose_name="密码", max_length=50)
    phone = models.CharField(verbose_name="电话", unique=True, max_length=11)
    flow = models.BigIntegerField(verbose_name="流量", default=10485760) #单位是B
    code = models.CharField(verbose_name="验证码", max_length=4, blank=True)
    createtime = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = u"客户信息"
        verbose_name_plural = u"客户信息"
        db_table = 'customer'

    def __unicode__(self):
        return self.username

class Record(models.Model):
    """消费记录"""
    username = models.CharField(verbose_name="用户名", max_length=50)
    costflow = models.BigIntegerField(verbose_name="消耗流量")
    today = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = u"消费日志"
        verbose_name_plural = u"消费日志"
        db_table = 'record'

    def __unicode__(self):
        return self.username

class Whitelist(models.Model):
    """网站白名单，只有在白名单里的网站才能转发到proxy服务器"""
    domain = models.CharField(verbose_name="域名", unique=True, max_length=200)
    createtime = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = u"白名单"
        verbose_name_plural = u"白名单"
        db_table = 'whitelist'

    def __unicode__(self):
        return self.domain

class Config(models.Model):
    """crossfire配置表"""
    c = (
            (1, u'是'),
            (0, u'否'),
            )
    transpond = models.IntegerField(verbose_name="转发服务器ID", unique=True)
    proxy_host = models.CharField(verbose_name="代理服务器地址", max_length=200)
    proxy_port = models.IntegerField(verbose_name="代理服务器端口")
    encode = models.IntegerField(verbose_name="加密状态", choices=c, default=1)

    class Meta:
        verbose_name = u"配置表"
        verbose_name_plural = u"配置表"
        db_table = 'config'

    def __unicode__(self):
        return self.proxy_host

class Dns(models.Model):
    """域名解析"""
    src = models.CharField(verbose_name="源地址", unique=True, max_length=200)
    des = models.CharField(verbose_name="目的地", max_length=200)
    createtime = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = u"域名解析"
        verbose_name_plural = u"域名解析"
        db_table = 'dns'

    def __unicode__(self):
        return self.src
