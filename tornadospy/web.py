#!/usr/bin/env python3

from __future__ import division, print_function, unicode_literals

import functools
import json
import os.path
import sys
import threading

try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib as urllib_parse

import tornado.ioloop
import tornado.options
import tornado.util
import tornado.web

from . import shell


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        """Set cross domain policies, expect all people like me

        Set HTTP headers: Access-Control-Allow-*
        """

        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Origin", "*")

    def options(self, obj):
        """Set cross domain policies, OPTIONS method
        """

        self.set_header("Access-Control-Allow-Headers",
                        "accept, content-type")
        self.set_header("Access-Control-Allow-Methods",
                        "GET, POST, PUT, DELETE, PATCH, OPTIONS")
        self.set_header("Access-Control-Max-Age", "3600")

    def compute_etag(self):
        return None

    def write_json(self, obj, default=str):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(obj, default=default, ensure_ascii=False,
                              separators=(",", ":")))

    def write_octet(self, bs, filename):
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition",
                        'attachment; filename="{}"'.format(filename))
        self.finish(bs)

    @property
    def query_s(self):
        if not hasattr(self, "_query_s"):
            self._query_s = urllib_parse.unquote(self.request.query)
        return self._query_s

    @property
    def body_s(self):
        if not hasattr(self, "_body_s"):
            self._body_s = self.request.body.decode()
        return self._body_s

    @property
    def kwargs(self):
        if not hasattr(self, "_kwargs"):
            self._kwargs = tornado.util.ObjectDict(
                urllib_parse.parse_qsl((self.request.query)))
        return self._kwargs

    @property
    def json(self):
        if not hasattr(self, "_json"):
            self._json = json.loads(self.request.body.decode())
        return self._json


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html")


class ShellHandler(BaseHandler):
    sh = staticmethod(shell.instance())

    def get(self):
        self.render("shell.html")

    def post(self):
        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        output = self.sh(self.body_s)
        if output is not None:
            self.write(output or "\n")


class ObjectHandler(BaseHandler):
    def get(self):
        s = self.query_s
        if s:
            v = eval(s, None, sys.modules)
            l = dir(v)
        else:
            v = None
            l = sorted(i for i in sys.modules if "." not in i)
        self.render("object.html", s=s, v=v, l=l)

    def post(self):
        type = self.get_query_argument("type", "repr")
        response = eval(self.body_s, None, sys.modules)
        if type == "repr":
            self.set_header("Content-Type", "text/plain; charset=UTF-8")
            self.write(repr(response))
        elif type == "json":
            self.write_json(response)


HANDLERS = [
    (r"/_spy/object", ObjectHandler, None, "object"),
    (r"/_spy/shell", ShellHandler, None, "shell"),
    (r"/_spy", MainHandler, None, "main"),
    (r"/", tornado.web.RedirectHandler, {"url": "/_spy"}),
    (r"/(.+)", tornado.web.StaticFileHandler, {"path": "."}),
]


def make_app():
    complete_path = functools.partial(os.path.join, os.path.dirname(__file__))
    return tornado.web.Application(
        HANDLERS,
        static_path=complete_path("static"),
        template_path=complete_path("templates"),
        #debug=__debug__,
    )


def listen(port=36553):
    app = make_app()
    app.listen(port, xheaders=True)


def test():
    tornado.options.parse_command_line()
    listen()
    tornado.ioloop.IOLoop.instance().start()


def run_in_thread(port=36553):
    tornado.options.parse_command_line()

    def run():
        io_loop = tornado.ioloop.IOLoop()
        io_loop.make_current()
        assert io_loop is tornado.ioloop.IOLoop.current()
        listen(port)  # after make_current
        io_loop.start()

    th = threading.Thread(target=run)
    th.start()

    return th


def stop():
    io_loop = tornado.ioloop.IOLoop.current(False)
    assert io_loop is not None
    io_loop.close(True)
    io_loop.stop()


if __name__ == "__main__":
    test()
