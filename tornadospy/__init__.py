
"""
Type "help", "copyright", "credits" or "license" for more information.
>>> import tornadospy
>>> tornadospy.run_in_thread()
>>> tornadospy.run_in_thread(11111)
>>> tornadospy.run_in_thread(11112)
>>> tornadospy.run_in_thread(11113)

"""

from .web import listen, run_in_thread, stop
