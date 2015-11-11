#!/usr/bin/env python

import os,sys
from pyqtgraph.Qt import QtGui, QtCore

# requires pyqtgraph, pandas, ROOT, rootpy
from pylard.pylardisplay.larliteopdetdisplay import LArLiteOpDetDisplay
from pylard.larlite_interface.larliteopdata import LArLiteOpticalData

print 'loading QtGui.QApplication'



#  expects 'raw_wf_tree'
flist = []
for i in xrange(len(sys.argv)-1):
    flist.append(sys.argv[i+1])
opdata = LArLiteOpticalData( flist )

app = QtGui.QApplication([])
print 'call OpDetDisplay()'
opdisplay = LArLiteOpDetDisplay( opdata )
print opdisplay
print type(opdisplay)
print 'call show()'
opdisplay.setGeometry(500,300,1200,800)
opdisplay.setFocus()


#opdisplay.show()

print 'call main'
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        print "exec called ..."
        opdisplay.show()
        QtGui.QApplication.instance().exec_()
        #opdisplay.show()
