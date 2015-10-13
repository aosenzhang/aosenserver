# -*- coding: utf-8 -*-

import os
import logging
import socket


TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")
STATIC_PATH = static_path=os.path.join(os.path.dirname(__file__), "static")

logger = logging.getLogger('tornado_proxy')

if socket.gethostname() == 'zhangzhen':
    DATABASES = {
            'NAME': 'crossfire',
            'USER': 'root',
            'PASSWORD': 'zhangzhen',
            'HOST': '127.0.0.1',
            'PORT': '3307',
            }
else:
    DATABASES = {
            'NAME': 'crossfire',
            'USER': 'root',
            'PASSWORD': 'zhangzhen',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            }
