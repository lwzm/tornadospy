#!/usr/bin/env python3

import code
import io
import shlex
import sys

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
        line = line.rstrip()
        if line == "#":
            line = ""
        elif line.startswith("#"):
            line = """___({!r})""".format(line[1:])
        buf.append(line)
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

    run("import " + ",".join(set(map(
        lambda s: s.split(".")[0], filter(
            lambda s: not s.startswith("_"), sys.modules)))))
    run("del __builtins__['input']")
    run("del __builtins__['exit']")
    run("del __builtins__['quit']")
    run("del sys.exit")
    run("def ___(s):                                               ")
    run("    c, *a = shlex.split(s)                                ")
    run("    return getattr(sh, c)(*map(sh.glob, a), _timeout=4)   ")
    run("")

    return run


if __name__ == "__main__":
    import doctest
    doctest.testmod()
else:
    sys.modules[__name__] = shell
