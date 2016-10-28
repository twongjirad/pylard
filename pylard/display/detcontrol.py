import os,sys

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from pylard.display.detectordisplay import DetectorDisplay

# Widget that controls what is drawn by the 3D detecor panel
# separated from DetectorDisplay panel because 3D won't draw if it shares a panel with another widget

class DetControlWindow(QtGui.QWidget):
    
    def __init__(self,detdisplay):
        super(DetControlWindow,self).__init__()
        self.detdisplay = detdisplay
        self.solidstree = self.detdisplay.solidswidget
        self.user_items = self.detdisplay.user_item_tree
        self.userframe  = self._makeUserItemTreeFrame()
        
        layout = QtGui.QGridLayout()
        layout.addWidget( self.userframe,  0, 0, 1, 4)
        layout.addWidget( self.solidstree, 0, 4, 1, 1)
        self.setLayout(layout)

        self.detdisplay.setControlWidget( self )
        
    def setMainWindow( self, window ):
        self.themainwindow = window


    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # User Item Handling

    def _makeUserItemTreeFrame(self):
        user_frame = QtGui.QFrame()
        user_frame.setLineWidth(1)
        user_frame.setFrameShape( QtGui.QFrame.Box )
        user_layout = QtGui.QGridLayout()

        user_layout.addWidget( QtGui.QLabel("user items"), 0, 0 )
        user_layout.addWidget( self.user_items, 1, 0 )
        user_frame.setLayout( user_layout )
        return user_frame

    
