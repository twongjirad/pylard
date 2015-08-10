import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict

from pylard.config.pmt_chmap import getPMTID, getChannel, getPMTIDList, getPaddleIDList
from pylard.config.pmtpos import getPosFromID 

class OpDetDisplay(QtGui.QWidget) :
    def __init__(self, opdata):
        super(OpDetDisplay,self).__init__()
        self.opdata = opdata

        # Plots
        self.graphics = pg.GraphicsLayoutWidget()
        self.plot = pg.PlotItem(name='Plot1')
        #self.diagram = pg.ViewBox()
        self.diagram = pg.PlotItem(name="plot2")
        self.pmtscale =  pg.GradientEditorItem(orientation='bottom')


        # main layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        #self.layout.addWidget( self.diagram, 0, 0 )
        #self.layout.addWidget( self.plot, 1, 0 )
        self.layout.addWidget( self.graphics, 0, 0 )
        self.graphics.addItem( self.diagram, 0, 0 )
        self.graphics.addItem( self.pmtscale, 1, 0 )
        self.graphics.addItem( self.plot, 2, 0 )
        self.lay_inputs = QtGui.QGridLayout()
        self.layout.addLayout( self.lay_inputs, 1, 0 )
        
        # inputs layout
        # widgets
        self.first_frame = 0
        self.last_frame = 0
        self.ticsperframe = opdata.nsamples
        
        # Plot options
        self.event = QtGui.QLineEdit("0")     # event number
        self.slot  = QtGui.QLineEdit("5")     # slot number
        self.collapse = QtGui.QRadioButton()  # collapse onto one another
        self.collapse.setChecked(False)
        self.prev_event = QtGui.QPushButton("Previous")
        self.next_event = QtGui.QPushButton("Next")
        self.adc_scaledown = QtGui.QLineEdit("100.0")
        self.lay_inputs.addWidget( QtGui.QLabel("Event"), 0, 0 )
        self.lay_inputs.addWidget( self.event, 0, 1 )
        self.lay_inputs.addWidget( QtGui.QLabel("FEM Slot"), 0, 2 )
        self.lay_inputs.addWidget( self.slot, 0, 3 )
        self.lay_inputs.addWidget( QtGui.QLabel("Overlay Mode"), 0, 4 )
        self.lay_inputs.addWidget( self.collapse, 0, 5 )
        self.lay_inputs.addWidget( QtGui.QLabel("ADC scale-down"), 0, 6 )
        self.lay_inputs.addWidget( self.adc_scaledown, 0, 7 )
        self.lay_inputs.addWidget( self.prev_event, 0, 10 )
        self.lay_inputs.addWidget( self.next_event, 0, 11 )

        # axis options
        self.start_frame  =  QtGui.QLineEdit("%d"%(self.first_frame))
        self.start_sample = QtGui.QLineEdit("0")
        self.end_frame  =  QtGui.QLineEdit("%d"%(self.first_frame))
        self.end_sample = QtGui.QLineEdit("1000")
        self.set_xaxis = QtGui.QPushButton("Re-plot!")

        self.lay_inputs.addWidget( QtGui.QLabel("Min. Frame"), 1, 0 )
        self.lay_inputs.addWidget( self.start_frame, 1, 1 )
        self.lay_inputs.addWidget( QtGui.QLabel("Min. Sample"), 1, 2 )
        self.lay_inputs.addWidget( self.start_sample,1,3)
        self.lay_inputs.addWidget( QtGui.QLabel("Max. Frame"), 1, 4 )
        self.lay_inputs.addWidget( self.end_frame, 1, 5 )
        self.lay_inputs.addWidget( QtGui.QLabel("Max. Sample"), 1, 6 )
        self.lay_inputs.addWidget( self.end_sample, 1, 10 )
        self.lay_inputs.addWidget( self.set_xaxis, 1, 11 )


        # range selections
        self.time_range = pg.LinearRegionItem(values=[50,150], orientation=pg.LinearRegionItem.Vertical)
        self.plot.addItem( self.time_range )

        # diagram objects
        self.definePMTdiagram()

        # connect
        self.set_xaxis.clicked.connect( self.plotData )
        self.next_event.clicked.connect( self.nextEvent )
        self.prev_event.clicked.connect( self.prevEvent )
        
    def plotData( self ):

        evt = int(self.event.text())
        slot = int(self.slot.text())
        self.opdata.getEvent( evt, slot=slot )
        
        sframe = int(self.start_frame.text())
        eframe = int(self.end_frame.text())
        ssample = int(self.start_sample.text())
        esample = int(self.end_sample.text())
        if sframe<self.first_frame:
            sframe = self.first_frame
            ssample = 0
        if eframe>self.last_frame:
            eframe = self.last_frame
            esample = self.ticsperframe-1

        for s in [ssample,esample]:
            if s<0:
                s = 0
            if s>=self.ticsperframe:
                s = self.ticsperframe-1

        xmin = (sframe-self.first_frame)*self.ticsperframe + ssample
        xmax = (eframe-self.first_frame)*self.ticsperframe + esample

        scaledown = float( self.adc_scaledown.text() )
        

        self.plot.clear()
        offset = 1.0
        if self.collapse.isChecked():
            offset = 0.0
            scaledown = 1.0
            
        for ipmt in xrange(0,self.opdata.opdetdigi.shape[1]):
            if ipmt in getPMTIDList():
                # PMT
                self.plot.plot( (self.opdata.opdetdigi[:,ipmt]-2048.0)/scaledown+ipmt*offset, pen=(255,255,255), name="PMT%d"%(ipmt))
            elif ipmt in getPaddleIDList():
                # PADDLE
                self.plot.plot( (self.opdata.opdetdigi[:,ipmt]-2048.0)/scaledown+ipmt*offset, pen=(0,0,255), name="Paddle%d"%(ipmt))
            else:
                # LOGIC
                self.plot.plot( (self.opdata.opdetdigi[:,ipmt]-2048.0)/scaledown+ipmt*offset, pen=(0,255,0), name="Logic%d"%(ipmt))
        self.plot.setXRange(xmin,xmax,update=True)
        self.plot.addItem( self.time_range )

        # ----------------------------------------------------
        # diagram object
        bnds = self.time_range.getRegion()
        if bnds[0]>bnds[1]:
            tmp = bnds[0]
            bnds[0] = bnds[1]
            bnds[1] = tmp

        self.pmtspot = []
        for ich in xrange(self.opdata.opdetdigi.shape[1],-1,-1):
            if ich>=36:
                continue
            maxamp = np.max( self.opdata.opdetdigi[bnds[0]:bnds[1],ich] )-2048.0
            ipmt = getPMTID( ich )-1
            #print "maxamp: id=",ipmt,' max=',maxamp
            col = self.pmtscale.colorMap().map( (maxamp)/2048.0 )
            if ipmt in getPMTIDList():
                pos = getPosFromID(ipmt )
                self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":30, 'pen':{'color':'w','width':2}, 'brush':col, 'symbol':'o'} )
            elif ipmt in getPaddleIDList():
                pos = getPosFromID( ipmt )
                self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":25, 'pen':{'color':(0,0,255),'width':2}, 'brush':col, 'symbol':'s'} )
        self.pmtdiagram.setData( self.pmtspot )

        # axis!
        ax = self.plot.getAxis('bottom')
        ax.setHeight(30)
        xStyle = {'color':'#FFFFFF','font-size':'12pt'}
        ax.setLabel('64 MHz Sample Tick',**xStyle)
        ay = self.plot.getAxis('left')
        yStyle = {'color':'#FFFFFF','font-size':'12pt'}
        if self.collapse.isChecked():
            ay.setLabel('ADC counts - 2048',**yStyle)
        else:
            ay.setLabel('PMT Channel Number',**yStyle)


    def definePMTdiagram(self):
        self.pmtspot = []
        for pid in getPMTIDList():
            pos = getPosFromID( pid )
            self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":30, 'pen':{'color':'w','width':2}, 'brush':(255,255,255,255), 'symbol':'o'} )
        for pid in getPaddleIDList():
            pos = getPosFromID( pid )
            self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":25, 'pen':{'color':(0,0,255,1.0),'width':2}, 'brush':(255,255,255,255), 'symbol':'s'} )
        self.pmtdiagram = pg.ScatterPlotItem(pxMode=False)
        self.pmtdiagram.addPoints( self.pmtspot )
        self.diagram.addItem( self.pmtdiagram ) 


        
    def nextEvent(self):
        evt = int(self.event.text())
        slot = int(self.slot.text())
        try:
            self.opdata.getEvent( evt+1, slot=slot )
            self.event.setText("%d"%(evt+1))
        except:
            self.opdata.getEvent( evt, slot=slot )
        self.plotData()

    def prevEvent(self):
        evt = int(self.event.text())
        slot = int(self.slot.text())
        try:
            self.opdata.getEvent( evt-1, slot=slot )
            self.event.setText("%d"%(evt-1))
        except:
            self.opdata.getEvent( evt, slot=slot )
        self.plotData()
            
            
            
