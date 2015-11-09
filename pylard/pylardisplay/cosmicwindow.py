import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict


samplesPerFrame = 102400
NSPERTICK = 15.625
USPERTICK = NSPERTICK/1000.
NPMTS = 32
NDETS = 36
NCHAN = 48

class CosmicWindow(pg.PlotItem):

    def __init__(self,name="Cosmic Readout Windows"):
        
        super(CosmicWindow,self).__init__()

        self.beambox = pg.PlotDataItem( x=[0,0,samplesPerFrame*USPERTICK,samplesPerFrame*USPERTICK,0], y=[-5, 32, 32, -5, -5] )

        self.tick_range = [-200,1550]

        self.time_range = pg.LinearRegionItem(values=[self.tick_range[0]*USPERTICK , self.tick_range[1]*USPERTICK ] , orientation=pg.LinearRegionItem.Vertical)

        self.addItem(self.time_range)

        self.setLabel( "bottom", text="time from trigger", units="seconds", unitPrefix="micro" )

        # data
        self.cosmicwindowvector = None

    # --------------------------
    # reset time-window
    def setTickWindow( self, tick_bounds ):
        self.tick_range = tick_bounds
        self.time_range = pg.LinearRegionItem(values=[self.tick_range[0]*USPERTICK , self.tick_range[1]*USPERTICK ] , orientation=pg.LinearRegionItem.Vertical)


    # --------------------------
    # Get time-range window
    def setRange(self):
        self.tick_range[0] = int(self.time_range.getRegion()[0]/USPERTICK)
        self.tick_range[1] = int(self.time_range.getRegion()[1]/USPERTICK)

    def getTickRange(self):
        self.setRange()
        return self.tick_range
    
    def getTimeRangeNS( self ):
        self.setRange()
        return [self.tick_range[0]*NSPERTICK , self.tick_range[1]*NSPERTICK ]

    def getTimeRangeUS( self ):
        self.setRange()
        return [self.tick_range[0]*USPERTICK , self.tick_range[1]*USPERTICK ]

    # -----------------------------------------------
    # PLOT Time-Window
    def plotCosmicWindows( self, cosmicwindows, event_time_range=[-1600., 4800.], drawslot=None ):

        self.clear()

        self.spots = []
        brush = (255,0,0,100)

        self.cosmicwindowvector = cosmicwindows
        cwv = cosmicwindows

        self.spots = []
        for (slot,ch),windows in cwv.chwindows.items():
            #if slot is not None and slot!=drawslot:
            #    continue
            for t,win in windows.items():
                # time in ns
                #print " cosmic window: ",ch,t
                #if t<-2*samplesPerFrame or t>3*samplesPerFrame:
                #    print t,"<-",samplesPerFrame,">",3*samplesPerFrame
                #    continue
                if win.slot==5:
                    brush = (255,0,0,100)
                else:
                    brush = (0,0,255,100)
                self.spots.append( {"pos":(t*0.001,win.ch),"size":2,"pen":{'color':'w','width':1},'brush':brush, 'symbol':'s'} )

        self.windowplot = pg.ScatterPlotItem(pxMode=False)
        self.windowplot.addPoints( self.spots )
        self.addItem( self.windowplot )
        self.addItem( self.beambox )
        self.addItem( self.time_range )

        # axis
        ax = self.getAxis('bottom')
        ax.setHeight(30)
        xStyle = {'color':'#FFFFFF','font-size':'14pt'}
        ax.setLabel('us relative to readout trigger',**xStyle)
        ay = self.getAxis('left')
        yStyle = {'color':'#FFFFFF','font-size':'14pt'}
        ay.setLabel('FEM CH Number (PMTID-1)',**yStyle)

        # set the axis range
        #self.setXRange(event_time_range[0], event_time_range[1])
