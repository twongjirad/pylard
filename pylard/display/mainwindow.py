import sys,os
from pyqtgraph.Qt import QtCore, QtGui
from pylard.display.opdetwindow import OpDetWindow
from pylard.display.rgbdisplay import RGBDisplay
from pylard.display.eventcontrol import EventControl
from pylard.display.masterconfigpanel import MasterConfigPanel
from pylard.eventprocessor.processmanager import ProcessManager

class PyLArD( QtGui.QMainWindow ):
    def __init__(self, config_yaml="", use_cache=True, cache_dir="./cache", pylardconfig=None):
        super( PyLArD, self ).__init__()
        self.resize(1400,800)
        self.centraltab = QtGui.QTabWidget()
        self.setCentralWidget(self.centraltab)

        self.pmtwindow    = OpDetWindow()
        self.rgbdisplay   = RGBDisplay()
        self.eventcontrol = EventControl()
        self.masterconfig = MasterConfigPanel(pylardconfig)
        
        # pass the larlite filelist path to the event control
        flist = ""
        if self.masterconfig.config.larlite_filelist!="":
            flist = self.masterconfig.config.larlite_filelist.strip()
        if self.masterconfig.config.larcv_filelist!="":
            if flist!="":
                flist+=";"
            flist += self.masterconfig.config.larcv_filelist
        if flist!="":
            self.eventcontrol.filelist_filepath.setText( flist )

        # pass processor config defaults to event control
        if self.masterconfig.config.larlite_process_cfg!="":
            self.eventcontrol.processor_filepath.setText( self.masterconfig.config.larlite_process_cfg.strip() )
        if self.masterconfig.config.larcv_process_cfg!="":
            self.eventcontrol.larcv_processor_filepath.setText( self.masterconfig.config.larcv_process_cfg.strip() )

        self.centraltab.resize(250,150)
        self.tabs = {}

        # Built in widgets. User can add their own.
        self.addPanel( "masterconfig", "PyLArD Config Panel", self.masterconfig )
        self.addPanel( "eventcontrol", "EventLoop Panel", self.eventcontrol )
        self.addPanel( "rgbdisplay", "RGB Display", self.rgbdisplay )
        self.addPanel( "opdetdisplay", "OpDet Display", self.pmtwindow )

        self.centraltab.setCurrentWidget( self.eventcontrol )

        # filemanagers
        self.filemanagers = {"LARLITE":None,"LARCV":None,"RAWDIGITS":None}

        # event processor

        # on start-up, do we open files
        if self.masterconfig.config.larlite_filelist!="" and self.masterconfig.config.load_files_on_start.lower() in ["yes","y"]:
            self.eventcontrol.loadFilelistButton()
        # set the default file type event driver
        if self.masterconfig.config.default_filetype_driver!="":
            if self.masterconfig.config.default_filetype_driver.upper()=="LARLITE":
                self.eventcontrol.codeview_ftype_combo.setCurrentIndex(0)
            elif self.masterconfig.config.default_filetype_driver.upper()=="LARCV":
                self.eventcontrol.codeview_ftype_combo.setCurrentIndex(1)
            

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

    
