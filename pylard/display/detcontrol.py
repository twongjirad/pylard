import os,sys

from pyqtgraph.Qt import QtCore, QtGui
from pylard.display.detectordisplay import DetectorDisplay

class DetControlWindow(QtGui.QWidget):
    
    def __init__(self,detwin):
        super(DetControlWindow,self).__init__()
        self.detwin = detwin
        self.detdisplay = self.detwin.detdisplay
        
        
        layout = QtGui.QGridLayout()
        layout.addWidget( self.detdisplay.solidswidget, 0, 0)
        self.setLayout(layout)
        
    def setMainWindow( self, window ):
        self.themainwindow = window
