from pyqtgraph.Qt import QtGui, QtCore 
import os,sys
import display.mainwindow

def run(configfile=""):
    print "Starting PyLArD2"
    from pyqtgraph.Qt import QtGui, QtCore
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication([])
        mw = display.mainwindow.PyLArD()
        mw.show()
        QtGui.QApplication.instance().exec_()
