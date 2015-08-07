import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict

class OpDetDisplay(QtGui.QWidget) :
    def __init__(self, opdata):
        super(OpDetDisplay,self).__init__()
        self.opdata = opdata
        self.plot = pg.PlotWidget(name='Plot1')
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

        # main layout
        self.layout.addWidget( self.plot, 0, 0 )
        self.lay_inputs = QtGui.QGridLayout()
        self.layout.addLayout( self.lay_inputs, 1, 0 )
        
        # inputs layout
        # widgets
        self.first_frame = 0
        self.last_frame = 0
        self.ticsperframe = opdata.nsamples
        
        self.event = QtGui.QLineEdit("0")
        self.slot  = QtGui.QLineEdit("5")
        self.start_frame  =  QtGui.QLineEdit("%d"%(self.first_frame))
        self.start_sample = QtGui.QLineEdit("0")
        self.end_frame  =  QtGui.QLineEdit("%d"%(self.first_frame))
        self.end_sample = QtGui.QLineEdit("1000")
        self.set_xaxis = QtGui.QPushButton("Set X-axis")

        self.lay_inputs.addWidget( QtGui.QLabel("Event"), 0, 0 )
        self.lay_inputs.addWidget( self.event, 0, 1 )
        self.lay_inputs.addWidget( QtGui.QLabel("FEM Slot"), 0, 2 )
        self.lay_inputs.addWidget( self.slot, 0, 3 )
        
        self.lay_inputs.addWidget( QtGui.QLabel("X Range: min"), 0, 4 )
        self.lay_inputs.addWidget( QtGui.QLabel("Frame"), 0, 5 )
        self.lay_inputs.addWidget( self.start_frame, 0, 6 )
        self.lay_inputs.addWidget( QtGui.QLabel("Sample"), 0, 7 )
        self.lay_inputs.addWidget( self.start_sample,0,8)
        self.lay_inputs.addWidget( QtGui.QLabel("max"), 0, 9 )
        self.lay_inputs.addWidget( QtGui.QLabel("Frame"), 0, 10 )
        self.lay_inputs.addWidget( self.end_frame, 0, 11 )
        self.lay_inputs.addWidget( QtGui.QLabel("Sample"), 0, 12 )
        self.lay_inputs.addWidget( self.end_sample, 0, 13 )
        self.lay_inputs.addWidget( self.set_xaxis, 0, 14 )

        # connect
        self.set_xaxis.clicked.connect( self.plotData )
        
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

        self.plot.getPlotItem().clear()
        for ipmt in xrange(0,self.opdata.opdetdigi.shape[1]):
            self.plot.plot( self.opdata.opdetdigi[:,ipmt]-2045.0+ipmt*1000, pen=(255,255,255), name="PMT%d"%(ipmt))
        self.plot.setXRange(xmin,xmax,update=True)


