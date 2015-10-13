# -*- coding: utf-8 -*-

import logging

import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

from handler import TranspondHandler
from settings import TEMPLATE_PATH, STATIC_PATH, logger

define("port", default=8000, help="run on the given port", type=int)
define("id", default=0, help="server id", type=int)
define("debug", default=False, help="Debug Mode", type=bool)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r'.*', TranspondHandler),]
        settings = dict(
                template_path=TEMPLATE_PATH,
                static_path=STATIC_PATH,
                debug=options.debug,
                gzip=True,
                )
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    logger.setLevel(logging.DEBUG) if options.debug else logger.setLevel(logging.ERROR)
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
