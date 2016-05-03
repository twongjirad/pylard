import os,sys
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
from pylard.core.tpcimageview import TPCImageView

# This is the window where we will house the TPC View of the data
# It contains widgets to change the view of the windows
# Also a buttom to the navigator of user data

# The TPC image is stored in the TPCImageView class (in core.tpcimageview)

class TPCWindow(QtGui.QWidget):
    def __init__(self):
        super(TPCWindow,self).__init__()
        self.resize( 1200, 700 )

        self.layout = QtGui.QGridLayout()
        # TPC View
        self.tpcview = TPCImageView()

        #self._gendummydata()

        # Buttons
        # later


        self.layout.addWidget( self.tpcview, 0, 0 )
        
        # set the layout
        self.setLayout( self.layout )

    def _gendummydata(self):
        # Generate image data
        d = 600
        data = np.random.normal(size=(d, d,3))
        data[20:80, 20:80,0] += 2.
        data += np.random.normal(size=(d, d,3)) * 0.1
        self.tpcview.setImage( data )
        
    
    
