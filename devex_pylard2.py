import os,sys

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pylard as pylard
from pylard.display.mainwindow import PyLArD as mainwindow
from pylard.eventprocessor.processmanager import ProcessManager
from pylard.eventprocessor.filemanager import FileManager

app = QtGui.QApplication([])

# get the pylard window
mw = mainwindow()
mw.show()

man = ProcessManager()

fman = FileManager( "myfiles.txt" )
fman_missing = FileManager( "myfiles_missing.txt" )


print "[ENTER TO EXIT]"
raw_input()
