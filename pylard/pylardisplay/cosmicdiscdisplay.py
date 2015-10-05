import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict


samplesPerFrame = 102400
NSPERTICK = 15.625
NPMTS = 32
NDETS = 36
NCHAN = 48

class CosmicDiscDisplay(QtGui.QWidget) :
    def __init__(self, opdetdisplay=None):
        """
        Class that makes a pop up plot of cosmic discrimintor fires
        optional constructor variable is instance of OpDetDisplay.
        """
        super(CosmicDiscDisplay,self).__init__()
        if opdetdisplay is not None:
            self.connectOpDetDisplay( opdetdisplay )

        # layout
        self.layout = QtGui.QGridLayout()
        self.setLayout( self.layout )

        # main scatter plot
        self.graphics = pg.GraphicsLayoutWidget() # graphics canvas
        self.diagram = pg.PlotItem(name="Cosmic Readout Windows")
        self.beambox = pg.PlotDataItem( x=[0,0,samplesPerFrame,samplesPerFrame,0], y=[-5, 32, 32, -5, -5] )
        self.time_range = pg.LinearRegionItem(values=[0,1000], orientation=pg.LinearRegionItem.Vertical)

        self.layout.addWidget( self.graphics, 0, 0 )
        self.graphics.addItem( self.diagram, 0, 0 )
        self.diagram.addItem( self.time_range )
        
        # buttons
        self.layout_inputs = QtGui.QGridLayout()
        self.changerange = QtGui.QPushButton("Apply Range!")
        self.layout_inputs.addWidget( self.changerange, 0, 0 )
        self.layout.addLayout( self.layout_inputs, 1, 0 )

        # data
        self.cosmicwindowvector = None

        self.changerange.clicked.connect( self.applyCosmicDiscRange )
        

    def connectOpDetDisplay( self, opdetdisplay ):
        self.opdetdisplay = opdetdisplay
        
    def plotCosmicWindows( self, cosmicwindowvector ):
        self.diagram.clear()
        self.beambox = pg.PlotDataItem( x=[0,0,samplesPerFrame,samplesPerFrame,0], y=[-5, 32, 32, -5, -5] )
        #self.time_range = pg.LinearRegionItem(values=[0,1000], orientation=pg.LinearRegionItem.Vertical)
        self.cosmicwindowvector = cosmicwindowvector
        cwv = cosmicwindowvector
        print "Number of cosmics: ",cwv.getNumWindows()
        self.spots = []
        for ch,windows in cwv.chwindows.items():
            for t,win in windows.items():
                if t<-2*samplesPerFrame or t>3*samplesPerFrame:
                    print t,"<-",samplesPerFrame,">",3*samplesPerFrame
                    continue
                if win.slot==5:
                    brush = (255,0,0,100)
                else:
                    brush = (0,0,255,100)
                self.spots.append( {"pos":(t,win.ch),"size":2,"pen":{'color':'w','width':1},'brush':brush, 'symbol':'s'} )
        self.windowplot = pg.ScatterPlotItem(pxMode=False)
        self.windowplot.addPoints( self.spots )
        self.diagram.addItem( self.windowplot )
        #self.diagram.addItem( self.beambox )
        self.diagram.addItem( self.time_range )

        # axis
        ax = self.diagram.getAxis('bottom')
        ax.setHeight(30)
        xStyle = {'color':'#FFFFFF','font-size':'14pt'}
        ax.setLabel('ns relative to readout trigger',**xStyle)
        ay = self.diagram.getAxis('left')
        yStyle = {'color':'#FFFFFF','font-size':'14pt'}
        ay.setLabel('FEM CH Number (PMTID-1)',**yStyle)

        
    def applyCosmicDiscRange( self ):
        if self.opdetdisplay is None:
            print "Need to connect CosmicDiscDisplay to an OpdetDisplay"
            return
        if self.cosmicwindowvector is None:
            print "Need to give the widget some cosmic window data"
            return

        bnds = self.time_range.getRegion()
        if bnds[0]>bnds[1]:
            temp = bnds[0]
            bnds[0] = bnds[1]
            bnds[1] = temp
        
        start = int(bnds[0])-1
        end = int(bnds[1])+1
        
        slot = int(self.opdetdisplay.slot.text())
        
        self.opdetdisplay.plot.clear()
        offset = 1.0
        scaledown = float( self.opdetdisplay.adc_scaledown.text() )
        if self.opdetdisplay.collapse.isChecked():
            offset = 0.0
            scaledown = 1.0

        data = np.ones( ( end-start,NCHAN), dtype=np.float )*2048.0
        
        cosmics = self.cosmicwindowvector.getWindowsBetweenTimes( start, end )
        for win in cosmics:
            if win.slot!=slot:
                continue
            ipmt = win.ch
            wfm = win.wfm
            fillstart = win.time-start
            fillend   = win.time-start+len(wfm)
            data[fillstart:fillend,ipmt] = wfm[:]

        x = np.linspace( start*NSPERTICK, end*NSPERTICK, num=int(end-start) )
        for ch in range(0,NCHAN):
            ipmt = ch
            if len(self.opdetdisplay.channellist)>0 and ipmt not in self.opdetdisplay.channellist and not self.opdetdisplay.draw_all.isChecked():
                continue
            pencolor = self.opdetdisplay.getChanColor( ipmt )
            if self.opdetdisplay.last_clicked_channel is not None and ipmt==self.opdetdisplay.last_clicked_channel:
                pencolor = (0, 255, 255 )
            y = (data[:,ipmt]-2048.0)/scaledown + ipmt*offset
            self.opdetdisplay.plot.plot( x=x, y=y, pen=pencolor, name="PMT%d"%(ipmt))


        self.opdetdisplay.plot.autoRange()
            
