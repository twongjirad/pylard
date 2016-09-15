import sys,os
from pyqtgraph.Qt import QtCore, QtGui
from pylard.display.opdetwindow import OpDetWindow
from pylard.display.rgbdisplay import RGBDisplay
from pylard.display.eventcontrol import EventControl
from pylard.display.masterconfigpanel import MasterConfigPanel
from pylard.eventprocessor.processmanager import ProcessManager
from pylard.eventprocessor.visprocessor import VisProcessor
from pylard.eventprocessor.datacoordinator import DataCoordinator

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
        self.mergeddata = None
        
        # pass the larlite filelist path to the event control
        flist = ""
        if self.masterconfig.config.larlite_filelist!="":
            flist = self.masterconfig.config.larlite_filelist.strip()
        if self.masterconfig.config.larcv_filelist!="":
            if flist!="":
                flist+=";"
            flist += self.masterconfig.config.larcv_filelist
        if self.masterconfig.config.rawdigits_filelist!="":
            if flist!="":
                flist+=";"
            flist += self.masterconfig.config.rawdigits_filelist
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

        # vis processors
        self.visprocessor = VisProcessor()

        # on start-up, do we open files
        if flist!="" and self.masterconfig.config.load_files_on_start.lower() in ["yes","y"]:
            self.eventcontrol.loadFilelistButton()
        # set the default file type event driver
        if self.masterconfig.config.default_filetype_driver!="":
            if self.masterconfig.config.default_filetype_driver.upper()=="LARLITE":
                self.eventcontrol.codeview_ftype_combo.setCurrentIndex(0)
                self.eventcontrol.codeview_type_larlite.setChecked(True)
                self.eventcontrol.selectProcessorConfig( self.eventcontrol.codeview_type_larlite )
            elif self.masterconfig.config.default_filetype_driver.upper()=="LARCV":
                self.eventcontrol.codeview_ftype_combo.setCurrentIndex(1)
                self.eventcontrol.codeview_type_larcv.setChecked(True)
                self.eventcontrol.selectProcessorConfig( self.eventcontrol.codeview_type_larcv )
            elif self.masterconfig.config.default_filetype_driver.upper()=="RAWDIGITS":
                self.eventcontrol.codeview_ftype_combo.setCurrentIndex(2)
                self.eventcontrol.codeview_type_rawdigits.setChecked(True)
                self.eventcontrol.selectProcessorConfig( self.eventcontrol.codeview_type_rawdigits )
            

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

    
    # ================================================================
    # global event control

    def configureDataManagers(self):
        # setup mergeddata
        if self.mergeddata is None:
            self.mergeddata = DataCoordinator()
            for ftype,fman in self.filemanagers.items():
                if fman is not None:
                    self.mergeddata.addManager( ftype, fman )

        # save processor configuration files
        self.eventcontrol.saveProcessorFileButton() # save current file
        cfg = { "LARLITE":self.eventcontrol.processor_filepath.text(),
                "LARCV":self.eventcontrol.larcv_processor_filepath.text(),
                "RAWDIGITS":self.eventcontrol.rawdigits_processor_filepath.text()}
        # pass file managers and configureations to data coordinator
        for ftype,fman in self.filemanagers.items():
            if fman is not None:
                self.mergeddata.configure( ftype, str(cfg[ftype]) )
                self.configureVisProcessor( str(cfg[ftype]) )

    def configureVisProcessor(self,cfg):
        """ configure the visualizer """
        self.visprocessor.configure( cfg )

    def getEntry(self,entry, driver=None):
        self.configureDataManagers()
        if driver is None:
            # need to pick a filetype that is driving the event loop
            # for now, we go with the one whose processor window is open
            driver = self.mergeddata.getCurrentDrivingManager()

        # get event data
        status = self.mergeddata.getEntry( entry, driver )
        print "tried to get entry ",entry,": ",status
        if status:
            entry = self.mergeddata.getCurrentEntry()
            rse   = self.mergeddata.getCurrentRSE()
            self.eventcontrol.setEntryShown( entry, driver )
            self.pmtwindow.setEntryNumbers( entry, rse[0], rse[1], rse[2] )
        
        # pass to visualization processor
        self.visprocessor.execute( self.mergeddata )

        # pass vis products to panels
        self.pmtwindow.clearVisItems()
        for key,visproduct in self.visprocessor.products.items():
            destination = self.visprocessor.destination[key]
            print "vis product=",key," dest=",destination
            if destination in self.tabs:
                self.tabs[destination].addVisItem( "opdata", self.visprocessor.products[key] )

        self.tabs["opdetdisplay"].plotData()
        #self.tabs["rgbdisplay"].plotData()
            
        return status
    
    def nextEntry(self,driver=None):
        if self.mergeddata is None:
            return False
        entry = self.mergeddata.getCurrentEntry()+1
        return self.getEntry( entry, driver )

    def prevEntry(self,driver=None):
        if self.mergeddata is None:
            return False
        entry = self.mergeddata.getCurrentEntry()-1
        return self.getEntry( entry, driver )
        
    def getRSE( self, run, subrun, event, driver=None ):
        if driver is None:
            # need to pick a filetype that is driving the event loop
            # for now, we go with the one whose processor window is open
            driver = self.mergeddata.getCurrentDrivingManager()
            rse = (run,subrun,event)
            if driver in self.mergeddata.filemans and rse in self.mergeddata.filemans[driver].rse_dict:
                entry = self.mergeddata.filemans[driver].rse_dict[rse]
                return self.getEntry( entry, driver )
        return False
            
