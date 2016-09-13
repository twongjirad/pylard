import sys,os
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from pylard.config.defaultprocessor import getDefaultProcessorConfig
from pylard.eventprocessor.filemanager import FileManager

class EventControl(QtGui.QWidget):
    """ 
    This Tab is responsible for configuring event loop.
    widget elements:
    1) event processor configuration panel.
    2) filelist dialog 
    3) event trees
    4) global configuration
    """
    
    def __init__(self):
        super(EventControl,self).__init__()

        codeview  = self._makeCodeViewFrame()
        evtree    = self._makeEventTreeFrame()

        controlpanel_layout = QtGui.QGridLayout()
        controlpanel_layout.addWidget( codeview, 0, 0, 5, 3 )
        controlpanel_layout.addWidget( evtree,   0, 3, 5, 1 )
 
        self.setLayout( controlpanel_layout )

        self.themainwindow = None # will be set later

    def setMainWindow( self, window ):
        self.themainwindow = window

    ## ========================================================================================
    ## ========================================================================================
    ## Processor Configuration file frames
    def _makeProcessorFileDialogFrame(self):
        """ for control panel """

        # components of frame
        label = QtGui.QLabel("Ana Config File:")
        label.setFixedWidth(100)
        self.processor_filepath = QtGui.QLineEdit()
        self.processor_filepath.setText("default.cfg")
        self.processor_filediag_choose = QtGui.QPushButton("choose file")
        self.processor_filediag_choose.clicked.connect( self._getControlFilenameFromFileDialog )
        self.processor_filediag_openfile = QtGui.QPushButton("Load File")
        self.processor_filediag_savefile = QtGui.QPushButton("Save File")
        self.processor_filediag_savefile.clicked.connect( self.saveProcessorFileButton )

        # assemble frame and layout
        self.filediag_frame = QtGui.QFrame()
        self.filediag_frame.setLineWidth(1)
        self.filediag_frame.setFrameShape( QtGui.QFrame.Box )
        self.filediag_frame.setFixedHeight(80)

        filediag_layout = QtGui.QGridLayout()
        filediag_layout.addWidget( label, 0, 0 )
        filediag_layout.addWidget( self.processor_filepath, 0, 1, 1, 3 )
        filediag_layout.addWidget( self.processor_filediag_choose, 0, 4, 1, 1 )
        filediag_layout.addWidget( self.processor_filediag_openfile, 0, 5, 1, 1 )
        filediag_layout.addWidget( self.processor_filediag_savefile, 0, 6, 1, 1 )
        self.filediag_frame.setLayout( filediag_layout )

        return self.filediag_frame

    def _getControlFilenameFromFileDialog(self):
        """ for event processor configuration """

        filter = "FHICL (*.fcl);;CFG (*.cfg)"
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
        self.processor_filepath.setText(fname)

    def _getFileNameFromFileDialog(self):
        """ for event processor """

        filter = "ROOT (*.root);;UBdaq (*.ubdaq)"
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
        self.filepath.setText(fname)


    def _makeCodeViewFrame(self):
        """ frame containing text edit for process driver file."""

        self.codeview_frame = QtGui.QFrame()
        self.codeview_frame.setLineWidth(2)
        self.codeview_frame.setFrameShape( QtGui.QFrame.Box )

        processor_fileselect_frame = self._makeProcessorFileDialogFrame()
        
        codeview_layout = QtGui.QGridLayout()

        self.codeView = QtGui.QPlainTextEdit()
        
        codeview_layout.addWidget(self.codeView, 0, 0, 10, 1)
        codeview_layout.addWidget(processor_fileselect_frame, 10, 0, 2, 1 )

        self.codeview_frame.setLayout( codeview_layout )
        
        # default processor
        processor_filepath = self.processor_filepath.text()
        if not os.path.exists(processor_filepath):
            str_defaultprocessor = getDefaultProcessorConfig()
            # write to file
            defaultfile = open( processor_filepath, 'w' )
            print >> defaultfile, str_defaultprocessor
            defaultfile.close()            

        # write to codeview
        self.loadProcessorFile(processor_filepath)

        return self.codeview_frame

    def _saveProcessorFile(self):
        out = self.codeView.toPlainText()
        fpath = self.processor_filepath.text()
        if fpath=="":
            return
        fout = open( fpath, 'w' )
        print >> fout, out
        fout.close()

    def saveProcessorFileButton(self):
        self._saveProcessorFile()

    def loadProcessorFile(self,processorfilepath):
        fin = open( processorfilepath, 'r' )
        flines = fin.readlines()
        self.codeView.clear()
        for l in flines:
            self.codeView.appendPlainText( l[:-1] )
        fin.close()


    ## end of larlite processor config 
    ## ========================================================================================
    ## ========================================================================================
    ## Event Tree Frame
    def _makeEventTreeFrame(self):
        """ tree frame """
        self.eventtree_frame = QtGui.QFrame()
        self.eventtree_frame.setLineWidth(2)
        self.eventtree_frame.setFrameShape( QtGui.QFrame.Box )

        # event tree widget
        self.eventtree = pg.TreeWidget()
        self.eventtree.setColumnCount(4)

        # filelist dialog
        label = QtGui.QLabel("Input File List")
        #label.setFixedWidth(80)
        self.filelist_filepath = QtGui.QLineEdit()
        self.filelist_filediag_choose = QtGui.QPushButton("Select")  # opens dialog to choose file
        self.filelist_filediag_choose.clicked.connect( self._getFilelistFromFileDialog )
        self.filelist_filediag_openfile = QtGui.QPushButton("Load File") # passes filelist to filemanager
        self.filelist_filediag_openfile.clicked.connect( self.loadFilelistButton )
        flistlayout = QtGui.QGridLayout()
        flistlayout.addWidget( label, 0, 0, 1, 4 )
        flistlayout.addWidget( self.filelist_filepath,          1, 0, 1, 3 )
        flistlayout.addWidget( self.filelist_filediag_choose,   1, 3, 1, 1 )
        flistlayout.addWidget( self.filelist_filediag_openfile, 2, 0, 1, 4 )

        # setup layout
        eventtree_layout = QtGui.QGridLayout()
        eventtree_layout.addWidget( self.eventtree, 0, 0, 15, 2 )
        eventtree_layout.addLayout( flistlayout,   15, 0,  3, 2 )

        # hand to the frame
        self.eventtree_frame.setLayout( eventtree_layout )
        
        return self.eventtree_frame

    def _getFilelistFromFileDialog(self):
        fnames,ftype = QtGui.QFileDialog.getOpenFileNamesAndFilter(self, 'Open file', '.')
        fname = ""
        if len(fnames)>1:
            for f in fnames:
                fname += f
                if f!=fnames[-1]:
                    fname += ";"
        else:
            fname = fnames[0]
        self.filelist_filepath.setText(fname)

    def loadFilelistButton(self):
        """ we take the filelist and pass it onto the mainwindow's filemanager """
        if self.themainwindow is None:
            print "[EventControl] the mainwindow has not been set yet."
            return
        flist = self.filelist_filepath.text()
        # we pass the filelist to the file manager
        print "Loading Filemanager, building event index: this could take a second at first."
        fileman = FileManager()
        fileman.setFilelist( flist )
        # pass it to the main window
        self.themainwindow.filemanagers[fileman.filetype] = fileman

        # Top level is file type
        ftypekeys = self.themainwindow.filemanagers.keys()
        ftypekeys.sort()
        topitems = {}
        self.eventlistitems = {}
        for ftype in ftypekeys:
            nevents = 0
            fman = self.themainwindow.filemanagers[ftype]
            if fman is not None:
                nevents = len(fman.rse_dict)

            topitem = QtGui.QTreeWidgetItem([ftype,"%d"%(nevents)])
            self.eventtree.addTopLevelItem( topitem )
            topitems[ftype] = topitem
            self.eventlistitems[ftype] = {}

            # now we get the event list and add it to the event tree
            if fman is not None:
                for ientry,rse in fman.entry_dict.items():
                    self.eventlistitems[ftype][ientry] = QtGui.QTreeWidgetItem(["%d"%(ientry),"%d"%rse[0],"%d"%(rse[1]),"%d"%(rse[2]) ])
                    topitems[ ftype ].addChild( self.eventlistitems[ftype][ientry] )
        

    ## ========================================================================================

