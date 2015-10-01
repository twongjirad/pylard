import os,sys
from pyqtgraph.Qt import QtGui, QtCore

# requires pyqtgraph, pandas, ROOT, rootpy
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.wfopdata import WFOpData
from pylard.pylardata.rawdigitsopdata import RawDigitsOpData
from pylard.pylardata.rawdigitlarlite import RawDigitsOpData

print 'loading QtGui.QApplication'



#  expects 'raw_wf_tree'
#fname='~/uBooNE/data/PMTCommissioning/wf_000.root'
fname= '~/uBooNE/data/PMTCommissioning/run007.root'
#fname = sys.argv[1]
print 'call WFOpData()'
#opdata = WFOpData( fname )
opdata = RawDigitsOpData( fname )
#opdata = RawDigitsOpData(fname)

app = QtGui.QApplication([])
print 'call OpDetDisplay()'
opdisplay = OpDetDisplay( opdata )
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

