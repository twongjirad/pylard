import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg

import numpy as np
import pandas as pd
from root_numpy import root2array, root2rec, tree2rec, array2root
import ROOT

from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.wfopdata import WFOpData

app = QtGui.QApplication([])

event = 770
fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run005.root'
#numpy_rec_array = root2array(fname,'raw_wf_tree')
#wf_df=pd.DataFrame(numpy_rec_array)

opdata = WFOpData( fname )
wf_df = opdata.wf_df
q = wf_df.query('event==%d and slot==5'%(event))
nsamples = len(q['wf'][q.first_valid_index()])
print "NSAMPLES: ",nsamples

opdisplay = OpDetDisplay( opdata )
opdisplay.show()

print "NSAMPLES: ",nsamples

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
