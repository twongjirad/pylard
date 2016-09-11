import sys,os
from pyqtgraph.Qt import QtCore, QtGui

class EventControl(QtGui.QWidget):
    """ This Tab is responsible for configuring event loop."""

    def __init__(self):
        super(EventControl,self).__init__()
        
        filediag = self._makeFileDialogFrame()  # widgets for loading a file
        codeview = self._makeCodeViewFrame()

        controlpanel_layout = QtGui.QGridLayout()
        controlpanel_layout.addWidget( codeview, 0, 0, 5, 3 )
        controlpanel_layout.addWidget( filediag, 5, 0, 1, 3 )

        self.setLayout( controlpanel_layout )

    def _makeFileDialogFrame(self):
        # components of frame
        label = QtGui.QLabel("Input File(s):")
        label.setFixedWidth(80)
        self.filepath = QtGui.QLineEdit()
        self.filediag_choose = QtGui.QPushButton("choose file")
        self.filediag_choose.clicked.connect( self._getFileNameFromFileDialog )
        self.filediag_openfile = QtGui.QPushButton("Load File")

        # assemble frame and layout
        self.filediag_frame = QtGui.QFrame()
        self.filediag_frame.setLineWidth(2)
        self.filediag_frame.setFrameShape( QtGui.QFrame.Box )
        self.filediag_frame.setFixedHeight(80)

        filediag_layout = QtGui.QGridLayout()
        filediag_layout.addWidget( label, 0, 0 )
        filediag_layout.addWidget( self.filepath, 0, 1, 1, 3 )
        filediag_layout.addWidget( self.filediag_choose, 0, 4, 1, 1 )
        filediag_layout.addWidget( self.filediag_openfile, 0, 5, 1, 1 )
        self.filediag_frame.setLayout( filediag_layout )

        return self.filediag_frame


    def _getFileNameFromFileDialog(self):
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

        codeview_layout = QtGui.QGridLayout()

        self.codeView = QtGui.QPlainTextEdit()
        
        codeview_layout.addWidget(self.codeView)

        self.codeview_frame.setLayout( codeview_layout )

        return self.codeview_frame


    
