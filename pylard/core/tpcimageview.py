import os,sys
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

# This is the TPC Viewer Window

class TPCImageView(pg.ImageView):
    def __init__(self):
        super(TPCImageView,self).__init__()


