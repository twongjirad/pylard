import sys,os
from pyqtgraph.Qt import QtCore, QtGui
from pylard.display.detectordisplay import DetectorDisplay

class DetWindow(QtGui.QWidget):
    
    def __init__(self):
        super(DetWindow,self).__init__()
        self.detdisplay = DetectorDisplay()
        
        # load the geometry
        self.daefile = os.path.dirname(__file__)+"/../config/microboone_32pmts_nowires_cryostat.dae"
        print "loading daefile: ",self.daefile
        self.detdisplay.load_geometry( self.daefile )

        layout = QtGui.QGridLayout()
        layout.addWidget( self.detdisplay, 0, 0 )
        self.setLayout(layout)
        
    def setMainWindow( self, window ):
        self.themainwindow = window
