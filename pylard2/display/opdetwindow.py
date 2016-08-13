import os,sys,copy
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict

from pylard2.config.pmt_chmap import getPMTID, getChannel, getPMTIDList, getPaddleIDList
from pylard2.config.pmtpos import getPosFromID 
from pylard2.display.pmtposscatterplot import PMTScatterPlot
from pylard2.display.cosmicwindow import CosmicWindow

# The opdet window is composed of three subwindows.
# The first is a displah of the waveforms, controlled by this class
# Another is the diagram of PMTs, showing intensity via a color sale
# The last shows the location of all cosmic discriminator windows

class OpDetWindow(QtGui.QWidget) :

    NSPERTICK = 15.625
    NTICKS    = 1500

    def __init__(self):
        super(OpDetWindow,self).__init__()

        # ---------------
        # Display Widgets
        # ---------------

        # Mother canvas for plots
        self.graphics = pg.GraphicsLayoutWidget()

        # 1) waveform plotting region
        self.wfplot = pg.PlotItem(name="Waveform Plot")
        self.wf_time_range = pg.LinearRegionItem(values=[50,1500], orientation=pg.LinearRegionItem.Vertical)
        self.wfplot.addItem( self.wf_time_range )
        
        # 2) pmt plotting diagram
        self.pmt_map = pg.PlotItem(name="PMT map")
        # PMT scatter points
        self.pmtdiagram   = PMTScatterPlot()
        self.pmt_map.addItem( self.pmtdiagram ) 
        self.pmtscale =  pg.GradientEditorItem(orientation='bottom')

        # 3) time-range selction window
        self.time_window = CosmicWindow()

        self.lastevent = None
        self.newevent = True

        # Main Layout
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget( self.graphics, 0, 0, 1, 10 )
        self.graphics.addItem( self.pmt_map, 0, 0, rowspan=2 )
        self.graphics.addItem( self.pmtscale, 2, 0, rowspan=1 )
        self.graphics.addItem( self.wfplot, 3, 0, rowspan=3 )
        self.graphics.addItem( self.time_window, 6, 0, rowspan=1 )
        self.setLayout(self.layout)

        # -------------
        # Input Widgets
        # -------------
        
        # Layouts
        self.lay_inputs = QtGui.QGridLayout()
        self.layout.addLayout( self.lay_inputs, 7, 0 )
        
        # Navigation
        opdata = None # Temp hack
        if opdata is not None:
            self.event = QtGui.QLineEdit("%d"%(opdata.first_event))     # event number
        else:
            self.event = QtGui.QLineEdit("0") # event number
        self.slot  = QtGui.QLineEdit("5")     # slot number
        self.prev_event = QtGui.QPushButton("Previous")
        self.next_event = QtGui.QPushButton("Next")

        # control the waveform viewer
        self.collapse = QtGui.QCheckBox("Overlay Mode")  # collapse onto one another
        self.collapse.setChecked(False)
        self.adc_scaledown = QtGui.QLineEdit("100.0")
        # options
        self.draw_diag = QtGui.QCheckBox("draw diagram")  # collapse onto one another
        self.draw_diag.setChecked(True)
        self.draw_cosmics = QtGui.QCheckBox("draw disc. windows")
        self.draw_cosmics.setChecked(True)

        # add to layout
        self.lay_inputs.addWidget( QtGui.QLabel("Event"), 0, 0 )
        self.lay_inputs.addWidget( self.event, 0, 1 )
        self.lay_inputs.addWidget( QtGui.QLabel("FEM Slot"), 0, 2 )
        self.lay_inputs.addWidget( self.slot, 0, 3 )
        self.lay_inputs.addWidget( QtGui.QLabel("ADC scale-down"), 0, 4 )
        self.lay_inputs.addWidget( self.adc_scaledown, 0, 5 )
        self.lay_inputs.addWidget( self.collapse, 0, 8 )
        self.lay_inputs.addWidget( self.draw_diag, 0, 9 )
        self.lay_inputs.addWidget( self.draw_cosmics, 0, 10 )
        self.lay_inputs.addWidget( self.prev_event, 0, 11 )
        self.lay_inputs.addWidget( self.next_event, 0, 12 )
        self.last_clicked_channel = None
        self.user_plot_item = {} # storage for user plot items

        # axis options
        self.replot = QtGui.QPushButton("Re-plot!")
        self.openCosmicWindow = QtGui.QPushButton("Cosmic Disc. Viewer")
        self.draw_only_PMTs = QtGui.QCheckBox("only PMTs")  # draw only PMTs
        self.draw_only_PMTs.setChecked(False)
        self.draw_user_items = QtGui.QCheckBox("draw user items")  # draw user products
        self.draw_user_items.setChecked(True)
        self.draw_chlabels = QtGui.QCheckBox("channel labels")  # draw user products
        self.draw_chlabels.setChecked(False)
        self.run_user_analysis = QtGui.QCheckBox("run user funcs.")  # draw user products
        self.run_user_analysis.setChecked(True)

        self.lay_inputs.addWidget( self.draw_only_PMTs, 1, 8 )
        self.lay_inputs.addWidget( self.draw_chlabels, 1, 9 )
        self.lay_inputs.addWidget( self.draw_user_items, 1, 10 )
        self.lay_inputs.addWidget( self.run_user_analysis, 1, 11 )
        self.lay_inputs.addWidget( self.replot, 1, 12 )

        # other options
        self.channellist = [] # when not None, only draw channels in this list
        self.pedfunction = self.getpedestal

        # user analyses
        self.user_analysis_products = []
        self.user_analyses = []

        # connect
        self.replot.clicked.connect( self.plotData )
        self.next_event.clicked.connect( self.nextEvent )
        self.prev_event.clicked.connect( self.prevEvent )
        self.pmtdiagram.sigClicked.connect( self.pmtDiagramClicked )
        #self.pmtdiagram.scene().sigMouseMoved.connect(self.onMovePMTdiagram)
        
        
    def plotData( self ):
        # setup the graphics
        self.setGraphicsLayout()
        
        
    def nextEvent(self):
        pass

    def prevEvent(self):
        pass
            
    def getWaveformPlot(self):
        return self.wfplot
    
    def getPMTdiagram(self):
        return self.pmtdiagram
            
    def gotoEvent( self, event, slot=None ):
        pass
            
    def setOverlayMode( self, mode=True ):
        if mode==True:
            self.collapse.setChecked(True)
        else:
            self.collapse.setChecked(False)

    def selectChannels( self, chlist ):
        if type(chlist) is not list:
            print "select channels with python list"
            return
        self.channellist = chlist
        
    def plotAllChannels( self ):
        self.channellist = []

    def addUserWaveformItem( self, item, ch=None ):
        if ch not in self.user_plot_item.keys():
            self.user_plot_item[ch] = []
        self.user_plot_item[ ch ].append( item )

    def clearUserWaveformItem( self ):
        self.user_plot_item = {}

    def getChanColor( self, id, alpha=255 ):
        if id<32:
            return (255,255,255,alpha)
        elif id>=32 and id<36:
            return (0,0,255,alpha)
        else:
            return (0,255,0,alpha)
        
    def pmtDiagramClicked( self, plot, points ):
        for p in points:
            settings =  p.data()
            if settings is not None and settings['id'] not in self.channellist:
                p.setPen( (0, 255, 255, 255) )
                self.channellist.append( settings['id'] )
                self.last_clicked_channel = settings['id']
            else:
                if settings['id'] in self.channellist:
                    self.channellist.remove( settings['id'] )
                if len( self.channellist )==0:
                    p.setPen( self.getChanColor( settings['id'], alpha=255 ) )
                else:
                    p.setPen( self.getChanColor( settings['id'], alpha=50 ) )
                self.last_clicked_channel=None
        self.plotData()

    def setPMTdiagramValues( self, channeldata, scale=1.0 ):
        """
        channeldict: dict
        """
        self.pmtspot = []
        for ch in range(0,36):
            pos = getPosFromID(ch)
            bordercol = self.getChanColor( ch, alpha=255 )
            if ch in channeldata:
                col = self.pmtscale.colorMap().map( channeldata[ch]/scale )
            else:
                col = self.pmtscale.colorMap().map( 0.0 )
            self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":30, 'pen':{'color':bordercol,'width':2}, 'brush':col, 'symbol':'o', 'data':{"id":ch,"highlight":False}} )
        self.pmtdiagram.setData( self.pmtspot  )

    def getpedestal(self,wfm,femch=None):
        slot = int(self.slot.text())
        if slot==5:
            var = 1.0
        else:
            var = 20.0
        ped = pedestal.getpedestal( wfm, 10, var )
        if ped is None:
            print "ped is None, try with higher threshold" 
            ped = pedestal.getpedestal( wfm, 10, 20.0 )
        if ped is None:
            print "ped is still none, set to first sample: ",wfm[0]
            ped = wfm[0]
        return ped

    def setPedestalFunction( self, pedfunc ):
        self.pedfunction = pedfunc

    def addUserAnalysis( self, user_analysis ):
        self.user_analyses.append( user_analysis )

    def clearUserAnalyses( self ):
        self.user_analyses = []
        self.user_analysis_chproducts = {}
                              
                                        
    def setGraphicsLayout(self):
        self.graphics.clear()
        self.time_window.setRange()
        tick_range = self.time_window.tick_range
        print tick_range
        self.time_window = CosmicWindow()
        self.time_window.setTickWindow( tick_range )
        nextrow = 0
        if self.draw_diag.isChecked():
            self.graphics.addItem( self.pmt_map, nextrow, 0, rowspan=2 )
            self.graphics.addItem( self.pmtscale, nextrow+2, 0, rowspan=1 )
            nextrow += 3
        if True:
            # always draw waveforms
            self.graphics.addItem( self.wfplot, nextrow, 0, rowspan=3 )
            nextrow += 3
        if self.draw_cosmics.isChecked():
            self.graphics.addItem( self.time_window, nextrow, 0, rowspan=1 )


