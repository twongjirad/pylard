import sys,os
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from pylard.config.defaultprocessor import getDefaultProcessorConfig
import json

class MasterConfiguration:
    """ just an object to define/hold configuration parameters """
    def __init__(self):
        self.larlite_process_cfg = "default_larlite.cfg"
        self.larcv_process_cfg = "default_larcv.cfg"
        self.larlite_filelist = ""
        self.larcv_filelist = ""
        self.load_files_on_start = "no"
        self.default_filetype_driver = ""
        self.varnames = ["larlite_process_cfg",
                         "larcv_process_cfg",
                         "larlite_filelist",
                         "larcv_filelist",
                         "load_files_on_start",
                         "default_filetype_driver"]
    
    def makeJson(self):
        data = {}
        for var in self.varnames:
            exec("data[\"%s\"] = self.%s"%(var,var))
        return json.dumps(data)

    def loadJson(self,sdata):
        data = json.loads(sdata)
        for var in self.varnames:
            if var in data:
                exec("self.%s=\"%s\""%(var,data[var]))
            else:
                exec("self.%s=\"\"")
    def dump(self):
        print "[MasterConfiguration]"
        for var in self.varnames:
            val = getattr(self,var)
            print "  ",var,": ",val
        

class MasterConfigPanel(QtGui.QWidget):
    """ this panel can load or define the master configuration file."""
    def __init__(self,pylardconfig=None):
        super(MasterConfigPanel,self).__init__()
        self.config = MasterConfiguration()
        configpanel = self._makeConfigPanelFrame()
        configpanel_layout = QtGui.QGridLayout()
        configpanel_layout.addWidget( configpanel, 0, 0)
        self.setLayout(configpanel_layout)
        self.themainwindow = None

        # load config
        if pylardconfig is None:
            config_filepath = self.config_filepath.text()
        else:
            config_filepath = pylardconfig
        self.loadConfigFile(config_filepath)


    def setMainWindow(self,window):
        """ mainwindow provides access to all the other components of pylard 
            this should probably become something that is inherited...
        """
        self.themainwindow = window

    def _makeConfigPanelFrame(self):
        """ frame containing text edit for master config file."""

        self.codeview_frame = QtGui.QFrame()
        self.codeview_frame.setLineWidth(2)
        self.codeview_frame.setFrameShape( QtGui.QFrame.Box )

        config_fileselect_frame = self._makeConfigFileDialogFrame()
        
        codeview_layout = QtGui.QGridLayout()

        self.codeView = QtGui.QPlainTextEdit()
        
        temp  = QtGui.QLabel("Ick. Will develop better configuration interface than this.")
        codeview_layout.addWidget(temp, 0, 0, 1, 1)
        codeview_layout.addWidget(self.codeView, 1, 0, 10, 1)
        codeview_layout.addWidget(config_fileselect_frame, 11, 0, 2, 1 )

        self.codeview_frame.setLayout( codeview_layout )
        
        # default config
        config_filepath = self.config_filepath.text()
        if not os.path.exists(config_filepath):
            os.system( "cp "+os.path.dirname(__file__)+"/../config/default.pylardcfg ." )
            config_filepath = "default.pylardcfg"

        return self.codeview_frame

    def _makeConfigFileDialogFrame(self):
        """ for control panel """

        # components of frame
        label = QtGui.QLabel("PyLArD Config File:")
        label.setFixedWidth(150)
        self.config_filepath = QtGui.QLineEdit()
        self.config_filepath.setText("default.pylardcfg")
        self.config_filediag_choose = QtGui.QPushButton("choose file")
        self.config_filediag_choose.clicked.connect( self._getConfigFilenameFromFileDialog )
        self.config_filediag_savefile = QtGui.QPushButton("Save File")
        self.config_filediag_savefile.clicked.connect( self.saveConfigFileButton )
        self.config_filediag_openfile = QtGui.QPushButton("Load PyLArD Config")

        # assemble frame and layout
        self.filediag_frame = QtGui.QFrame()
        self.filediag_frame.setLineWidth(1)
        self.filediag_frame.setFrameShape( QtGui.QFrame.Box )
        self.filediag_frame.setFixedHeight(80)

        filediag_layout = QtGui.QGridLayout()
        filediag_layout.addWidget( label, 0, 0 )
        filediag_layout.addWidget( self.config_filepath, 0, 1, 1, 3 )
        filediag_layout.addWidget( self.config_filediag_choose, 0, 4, 1, 1 )
        filediag_layout.addWidget( self.config_filediag_savefile, 0, 5, 1, 1 )
        filediag_layout.addWidget( self.config_filediag_openfile, 1, 5, 1, 1 )
        self.filediag_frame.setLayout( filediag_layout )

        return self.filediag_frame

    def _getConfigFilenameFromFileDialog(self):
        """ for master config configuration """

        filter = "PYLARDCFG (*.pylardcfg);;JSON (*.json)"
        fnames,ftype = QtGui.QFileDialog.getOpenFileNamesAndFilter(self, 'Open file', '.', filter)
        fname = ""
        print fnames
        if len(fnames)>1:
            for f in fnames:
                fname += f
                if f!=fnames[-1]:
                    fname += ";"
        else:
            fname = fnames[0]
        self.config_filepath.setText(fname)


    def _saveConfigFile(self):
        out = self.codeView.toPlainText()
        fpath = self.config_filepath.text()
        if fpath=="":
            return
        fout = open( fpath, 'w' )
        print >> fout, out
        fout.close()


    def saveConfigFileButton(self):
        self._saveConfigFile()

    def loadConfigFile(self,configfilepath):
        print "[pylard] master config loading: ",configfilepath
        fin = open( configfilepath, 'r' )
        flines = fin.readlines()
        self.codeView.clear()
        for l in flines:
            self.codeView.appendPlainText( l[:-1] )
        fin.close()
        fin = open(configfilepath,'r')
        sdata = fin.read()
        self.config.loadJson( sdata )
        fin.close()
        self.config.dump()

