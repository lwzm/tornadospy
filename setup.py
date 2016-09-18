#!/usr/bin/env python3

import sys
from setuptools import setup, find_packages

setup(name="tornadospy",
      packages=find_packages(),
      package_data={"tornadospy": ["static/*", "templates/*"]},
     )

