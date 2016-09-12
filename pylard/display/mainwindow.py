import sys,os
from pyqtgraph.Qt import QtCore, QtGui
from pylard.display.opdetwindow import OpDetWindow
from pylard.display.rgbdisplay import RGBDisplay
from pylard.display.eventcontrol import EventControl
from pylard.display.masterconfigpanel import MasterConfigPanel
from pylard.eventprocessor.filemanager import FileManager
from pylard.eventprocessor.processmanager import ProcessManager

class PyLArD( QtGui.QMainWindow ):
    def __init__(self, config_yaml="", use_cache=True, cache_dir="./cache"):
        super( PyLArD, self ).__init__()
        self.resize(1400,800)
        self.centraltab = QtGui.QTabWidget()
        self.setCentralWidget(self.centraltab)

        self.pmtwindow    = OpDetWindow()
        self.rgbdisplay   = RGBDisplay()
        self.controlpanel = EventControl()
        self.masterconfig = MasterConfigPanel()
        
        self.centraltab.resize(250,150)
        self.tabs = {}

        # Built in widgets. User can add their own.
        self.addPanel( "masterconfig", "PyLArD Config Panel", self.masterconfig )
        self.addPanel( "eventcontrol", "EventLoop Panel", self.controlpanel )
        self.addPanel( "rgbdisplay", "RGB Display", self.rgbdisplay )
        self.addPanel( "opdetdisplay", "OpDet Display", self.pmtwindow )

        # filemanager
        self.filemanager = FileManager()

        # event processor

    def getPanel(self,name):
        """ get one of the panels """
        if name in self.tabs.keys():
            return self.tabs[name]
        return None

    def addPanel(self,name,title,widget):
        """ add a widget """
        self.centraltab.addTab( widget, title )
        self.tabs[name] = widget
        widget.setMainWindow(self)

    
