import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

# pylard
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.wfopdata import WFOpData
from pylard.pylardata.rawdigitsopdata import RawDigitsOpData


# using output of LArLite wftree
#fname="/Users/twongjirad/working/uboone/data/20150909_CosmicDiscTuning/wf_run007.root"
#opdata = WFOpData( fname )

# using output of larsfot's RawData/util/RawDigitsWriter: 'raw_wf_tree'
fname='/Users/twongjirad/working/uboone/data/pmtratedata/run2499_filterreconnect_subrun1.root'

opdata = RawDigitsOpData( fname )

app = QtGui.QApplication([])
opdisplay = OpDetDisplay( opdata )
opdisplay.show()

