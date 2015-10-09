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

        #self.beambox = pg.PlotDataItem( x=[0,0,samplesPerFrame,samplesPerFrame,0], y=[-5, 32, 32, -5, -5] )

        self.tick_range = [0,1500]

        self.time_range = pg.LinearRegionItem(values=[self.tick_range[0]*USPERTICK , self.tick_range[1]*USPERTICK ] , orientation=pg.LinearRegionItem.Vertical)

        self.addItem(self.time_range)

        # data
        self.cosmicwindowvector = None

    # -----------------------------------------------
    # PLOT Time-Window
    def plotCosmicWindows( self, event_time_range=[-1600., 4800.] ):

        #self.clear()
        #self.beambox = pg.PlotDataItem( x=[0,0,samplesPerFrame,samplesPerFrame,0], y=[-5, 32, 32, -5, -5] )
        #self.time_range = pg.LinearRegionItem(values=[0,1000], orientation=pg.LinearRegionItem.Vertical)
        self.spots = []
        brush = (255,0,0,100)

        '''
        for pmt in pulses:

            # vectror of times, amp of pulses for this given pmt
            pulse_list = pulses[pmt]

            for pulse in pulse_list:
                self.spots.append( {"pos":(pulse[0]*USPERTICK ,pmt),"size":2,"pen":{'color':'w','width':1},'brush':brush, 'symbol':'s'} )

        '''

        self.windowplot = pg.ScatterPlotItem(pxMode=False)
        self.windowplot.addPoints( self.spots )
        self.addItem( self.windowplot )
        #self.diagram.addItem( self.beambox )
        self.addItem( self.time_range )

        # set the axis range
        self.setXRange(event_time_range[0], event_time_range[1])

        # axis
        ax = self.getAxis('bottom')
        ax.setHeight(30)
        xStyle = {'color':'#FFFFFF','font-size':'14pt'}
        ax.setLabel('us from readout start',**xStyle)
        ay = self.getAxis('left')
        yStyle = {'color':'#FFFFFF','font-size':'14pt'}
        ay.setLabel('PMT Ch',**yStyle)


            
