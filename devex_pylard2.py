import os,sys

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pylard as pylard
from pylard.display.mainwindow import PyLArD as mainwindow
from pylard.eventprocessor.processmanager import ProcessManager

app = QtGui.QApplication([])

# get the pylard window
mw = mainwindow()
mw.show()

man = ProcessManager()


print "[ENTER TO EXIT]"
raw_input()
