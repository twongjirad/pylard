import os,sys
from pyqtgraph.Qt import QtGui, QtCore

app = QtGui.QApplication([])

from pylard.core.mainwindow import PyLArD

# Dev Script. For expert only. Expect this file to disappear.

if __name__ == "__main__":

    mw = PyLArD()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        print "exec called ..."
        mw.show()
        QtGui.QApplication.instance().exec_()

