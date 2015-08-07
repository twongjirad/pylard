import os,sys
from pyqtgraph.Qt import QtGui, QtCore

# requires pyqtgraph, pandas, ROOT, rootpy
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.wfopdata import WFOpData

app = QtGui.QApplication([])

#  expects 'raw_wf_tree'
fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run005.root'

opdata = WFOpData( fname )

opdisplay = OpDetDisplay( opdata )
opdisplay.show()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
