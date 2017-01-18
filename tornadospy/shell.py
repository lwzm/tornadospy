#!/usr/bin/env python3

from __future__ import division, print_function, unicode_literals

import code
import io
import shlex
import sys

try:
    import sh
    sh
except ImportError:
    pass


def instance():
    r"""
    >>> sh = instance()
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

    IO = io.StringIO if sys.version_info.major >= 3 else io.BytesIO

    def run(line):
        line = line.rstrip()
        if line == "#":  # single # is special
            line = ""
        elif len(line) > 1 and line[0] in "#$" and line[1].isalnum():
            line = """___({!r})""".format(line[1:])
        buf.append(line)
        source = "\n".join(buf)
        more = False
        stdout, stderr = sys.stdout, sys.stderr
        output = sys.stdout = sys.stderr = IO()

        try:
            more = sh.runsource(source)
        finally:
            sys.stdout, sys.stderr = stdout, stderr

        if more:
            return None
        else:
            del buf[:]
            return output.getvalue()

    run("import __main__")
    run("import " + ",".join(set(map(
        lambda s: s.split(".")[0], filter(
            lambda s: not s.startswith("_"), sys.modules)))))
    run("del __builtins__['input']")
    run("del __builtins__['exit']")
    run("del __builtins__['quit']")
    run("def ___(s):                                                         ")
    run("    l = shlex.split(s)                                              ")
    run("    c, a = l[0], l[1:]                                              ")
    run("    try:                                                            ")
    run("        cmd = getattr(sh, c)                                        ")
    run("        args = map(sh.glob, a)                                      ")
    run("        return cmd(*args, _tty_out=False, _timeout=3.3)             ")
    run("    except sh.CommandNotFound:                                      ")
    run("        print('not found')                                          ")
    run("    except sh.TimeoutException:                                     ")
    run("        print('timeout')                                            ")
    run("")

    return run


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    sh = instance()
    print(sh("print(dir())"))
