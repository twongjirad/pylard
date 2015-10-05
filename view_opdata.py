import os,sys
from pyqtgraph.Qt import QtGui, QtCore

# requires pyqtgraph, pandas, ROOT, rootpy
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.wfopdata import WFOpData
from pylard.pylardata.opdata import OpticalData

print 'loading QtGui.QApplication'



opdata = OpticalData( sys.argv )

app = QtGui.QApplication([])
opdisplay = OpDetDisplay( opdata )
opdisplay.setGeometry(500,300,1200,800)
opdisplay.setFocus()


print 'call main'
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        print "exec called ..."
        opdisplay.show()
        QtGui.QApplication.instance().exec_()
