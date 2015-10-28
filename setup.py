#!/usr/bin/env python
import os,sys
from setuptools import setup

# We need to determine if ROOT is installed first before we do anything!

try:
    import ROOT
    print "Can import pyROOT. Good."
except:
    print "ROOT and pyROOT not detected. Need this."
    sys.exit(-1)

try:
    import PyQt4
    print "Can import PyQt4. Good."
except:
    print "PyQt4 could not be imported. Need this."
    sys.exit(-1)

setup(name='pylard',
      version='0.1',
      description='Python Liquid Argon (Event) Display',
      author='Taritree Wongjirad',
      author_email='taritree@mit.edu',
      url='https://github.com/twongjirad/pylard',
      packages=['pylard','pylard.pylardata','pylard.pylardisplay','pylard.pylarsoftzmq','pylard.config','pylard.larlite_interface'],
      #install_requires=['lz4','pycollada','PyOpenGL','numpy>=1.9.1','pyqtgraph','pandas','numexpr','root_numpy','pyzmq','pexpect'],
      install_requires=['lz4','PyOpenGL','numpy>=1.9.1','pyqtgraph','numexpr','root_numpy','pyzmq','pexpect','pandas'],
     )
