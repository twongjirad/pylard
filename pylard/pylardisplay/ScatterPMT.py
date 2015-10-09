import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg


# class to hold all PMT scatter points
class ScatterPMT(pg.ScatterPlotItem):

    def __init__(self):
        super(ScatterPMT,self).__init__()
        self.setAcceptHoverEvents(True)
        
    def hoverEnterEvent(self, e):
        print 'entering!'

        
