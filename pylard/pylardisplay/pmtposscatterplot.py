import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from pylard.config.pmt_chmap import getPMTID, getChannel, getPMTIDList, getPaddleIDList
from pylard.config.pmtpos import getPosFromID 

# class to hold all PMT scatter points
class PMTScatterPlot(pg.ScatterPlotItem):

    def __init__(self):
        super(PMTScatterPlot,self).__init__()
        self.setAcceptHoverEvents(True)
        
        # define PMT and Paddle location
        # beam goes right to left!
        # note that pmt pos are in larsoft coordinates with origin moved such that drawing is in center of detector
        # we have to invert the z!
        self.pmtspot = []
        brush = (0,0,0,0)
        for pid in getPMTIDList():
            bordercol = (255,255,255,255)
            pos = getPosFromID( pid, origin_at_detcenter=True )
            self.pmtspot.append( {"pos":(-pos[2],pos[1]), "size":30, 'pen':{'color':bordercol,'width':2}, 'brush':brush, 'symbol':'o', 'data':{"id":pid,"highlight":False}} )
        for pid in getPaddleIDList():
            bordercol = (0,0,255,255)
            pos = getPosFromID( pid, origin_at_detcenter=True )
            self.pmtspot.append( {"pos":(-pos[2],pos[1]), "size":30, 'pen':{'color':bordercol,'width':2}, 'brush':brush, 'symbol':'s', 'data':{"id":pid,"highlight":False}} )

        self.addPoints( self.pmtspot )
        
    def hoverEnterEvent(self, e):
        print 'entering!'
