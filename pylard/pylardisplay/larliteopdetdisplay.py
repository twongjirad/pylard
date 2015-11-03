import os,sys,copy
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict

from pylard.config.pmt_chmap import getPMTID, getChannel, getPMTIDList, getPaddleIDList
from pylard.config.pmtpos import getPosFromID 
from pylard.pylardisplay.pmtposscatterplot import PMTScatterPlot
from pylard.pylardisplay.cosmicwindow import CosmicWindow
import pylard.pylardata.pedestal as pedestal

from opdetdisplay import OpDetDisplay

NSPERTICK = 15.625

class LArLiteOpDetDisplay(OpDetDisplay) :

    def __init__(self, opdata):
        OpDetDisplay.__init__(self,opdata)

        #super(OpDetDisplay,self).__init__()
        self.resize( 1200, 700 )


        # Set the data
        self.opdata = opdata

        # ---------------
        # Display Widgets
        # ---------------

        # OPDIGIT PRODUCER
        # producer name selection boxes
        self.opwf_prod = QtGui.QComboBox()
        # get list of possible producers for opdigit:
        if 'opdigit' not in self.opdata.dataproduct_dict:
            self.opwf_prod.addItems(['NONE'])
        else:
            producers = self.opdata.dataproduct_dict['opdigit']
            #producers.insert(0,'NONE')
            self.opwf_prod.addItems(producers)


        self.lay_inputs.addWidget( QtGui.QLabel('opdigit'), 1, 0 )
        self.lay_inputs.addWidget( self.opwf_prod, 1, 1 )

        # TRIGGER PRODUCER
        self.trig_prod = QtGui.QComboBox()
        # get list of possible producers for opdigit:
        if 'trigger' not in self.opdata.dataproduct_dict:
            self.trig_prod.addItems(['NONE'])
        else:
            producers = self.opdata.dataproduct_dict['trigger']
            #producers.insert(0,'NONE')
            self.trig_prod.addItems(producers)


        self.lay_inputs.addWidget( QtGui.QLabel('trigger'), 1, 2 )
        self.lay_inputs.addWidget( self.trig_prod, 1, 3 )

        

    def plotData( self ):

        newproducer = False
        # check for critical producers
        if (self.opdata.dataproduct_producer['opdigit'] != self.opwf_prod.currentText()):
            self.newevent = True
            print 'OPWF PRODUCER : ',self.opwf_prod.currentText()
            self.opdata.dataproduct_producer['opdigit'] = self.opwf_prod.currentText()
            newproducer = True
        if (self.opdata.dataproduct_producer['trigger'] != self.trig_prod.currentText()):
            self.newevent = True
            print 'TRIG PRODUCER : ',self.trig_prod.currentText()
            self.opdata.dataproduct_producer['trigger'] = self.trig_prod.currentText()
            newproducer = True
        if newproducer:
            # have to reconfigure data interface
            self.opdata.configure()

        OpDetDisplay.plotData(self)

