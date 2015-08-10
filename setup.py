#!/usr/bin/env python
from distutils.core import setup

setup(name='pylard',
      version='0.1',
      description='Python Liquid Argon (Event) Display',
      author='Taritree Wongjirad',
      author_email='taritree@mit.edu',
      url='https://github.com/twongjirad/pylard',
      packages=['pylard','pylard.pylardata','pylard.pylardisplay','pylard.pylarsoftzmq','pylard.config'],
      install_requires=['root_numpy','pandas','numpy','pyqtgraph'],
     )
