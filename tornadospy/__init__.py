
"""
Type "help", "copyright", "credits" or "license" for more information.
>>> import tornadospy
>>> tornadospy.run_in_thread()
>>> tornadospy.run_in_thread(11111)
>>> tornadospy.run_in_thread(11112)
>>> tornadospy.run_in_thread(11113)

"""

from . import shell
from .web import make_app, make_wsgi_app, listen, run_in_thread, stop
