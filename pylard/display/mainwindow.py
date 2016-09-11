import sys,os
from pyqtgraph.Qt import QtCore, QtGui
from pylard.display.opdetwindow import OpDetWindow
from pylard.display.rgbdisplay import RGBDisplay
from pylard.display.eventcontrol import EventControl

class PyLArD( QtGui.QMainWindow ):
    def __init__(self, config_yaml="", use_cache=True, cache_dir="./cache"):
        super( PyLArD, self ).__init__()
        self.resize(1400,800)
        self.centraltab = QtGui.QTabWidget()
        self.setCentralWidget(self.centraltab)

        self.pmtwindow    = OpDetWindow()
        self.rgbdisplay   = RGBDisplay()
        self.controlpanel = EventControl()
        
        self.centraltab.resize(250,150)

        # The control panel features three main items:
        # 1) the text edit control panel to program process manager
        # 2) the checkbox panel to control that to display in the diagrams [what ran and what didn't]
        # 3) file choosing dialog
        # 4) near future: place to dump errors caught in process loop
        
        self.centraltab.addTab(self.controlpanel,"EventLoop Panel")
        self.centraltab.addTab(self.pmtwindow,"OpDet View")
        self.centraltab.addTab(self.rgbdisplay,"RGB display")
        

