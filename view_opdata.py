#!/usr/bin/env python

import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

# pylard
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.rawdigitsopdata import RawDigitsOpData


fname = sys.argv[1]

opdata = RawDigitsOpData( fname )

app = QtGui.QApplication([])
opdisplay = OpDetDisplay( opdata )
opdisplay.show()

if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    print "exec called ..."
    opdisplay.show()
    QtGui.QApplication.instance().exec_()

