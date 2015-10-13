# -*- coding: utf-8 -*-

from django.contrib import admin
from models import Customer, Record, Whitelist, Config, Dns

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone', 'flow', 'createtime']
    search_fields = ['username', 'phone']
    ordering = ['-id']
admin.site.register(Customer, CustomerAdmin)

class RecordAdmin(admin.ModelAdmin):
    list_display = ['username', 'costflow', 'today']
    search_fields = ['username', 'today']
    ordering = ['-today']
admin.site.register(Record, RecordAdmin)

class WhitelistAdmin(admin.ModelAdmin):
    list_display = ['domain', 'createtime']
    search_fields = ['domain',]
    ordering = ['-id']
admin.site.register(Whitelist, WhitelistAdmin)

class ConfigAdmin(admin.ModelAdmin):
    list_display = ['transpond', 'proxy_host', 'proxy_port', 'encode']
    search_fields = ['transpond',]
    ordering = ['-id']
admin.site.register(Config, ConfigAdmin)

class DnsAdmin(admin.ModelAdmin):
    list_display = ['src', 'des', 'createtime']
    search_fields = ['src', 'des']
    ordering = ['-id']
admin.site.register(Dns, DnsAdmin)
