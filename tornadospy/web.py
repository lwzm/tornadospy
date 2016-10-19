#!/usr/bin/env python3

import code
import functools
import io
import json
import os.path
import shlex
import sys
import threading
import urllib.parse

import tornado.ioloop
import tornado.options
import tornado.util
import tornado.web

try:
    import sh
    sh
except ImportError:
    pass


def shell():
    r"""
    >>> sh = shell()
    >>> sh("1 + 1")
    '2\n'
    >>> sh("if True:")
    >>> sh("    1")
    >>> sh("    2")
    >>> sh("")
    '1\n2\n'
    """

    sh = code.InteractiveInterpreter()
    buf = []

    def run(line):
        buf.append(line.rstrip())
        source = "\n".join(buf)
        more = False
        stdout, stderr = sys.stdout, sys.stderr
        output = sys.stdout = sys.stderr = io.StringIO()

        try:
            more = sh.runsource(source)
        finally:
            sys.stdout, sys.stderr = stdout, stderr

        if more:
            return None
        else:
            del buf[:]
            return output.getvalue()

    return run


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

    def write_json(self, obj):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(obj, default=str, ensure_ascii=False,
                              separators=(",", ":")))

    def write_octet(self, bs, filename):
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition",
                        'attachment; filename="{}"'.format(filename))
        self.finish(bs)

    @property
    def query_s(self):
        if not hasattr(self, "_query_s"):
            self._query_s = urllib.parse.unquote(self.request.query)
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
                urllib.parse.parse_qsl((self.request.query)))
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
    _sh = shell()
    _sh("import " + ",".join(set(map(
        lambda s: s.split(".")[0], filter(
            lambda s: not s.startswith("_"), sys.modules)))))
    _sh("del __builtins__['input']")
    _sh("del __builtins__['exit']")
    _sh("del __builtins__['quit']")
    _sh("def q(s):                                                 ")
    _sh("    c, *a = shlex.split(s)                                ")
    _sh("    return getattr(sh, c)(*map(sh.glob, a))               ")
    _sh("")

    sh = staticmethod(_sh)

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
            l = sorted(sys.modules)
        self.render("object.html", s=s, v=v, l=l)

    def post(self):
        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        self.write(repr(eval(self.body_s, None, sys.modules)))


HANDLERS = [
    (r"/_spy/object", ObjectHandler, None, "object"),
    (r"/_spy/shell", ShellHandler, None, "shell"),
    (r"/_spy", MainHandler, None, "main"),
    (r"/", tornado.web.RedirectHandler, {"url": "/_spy"}),
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
