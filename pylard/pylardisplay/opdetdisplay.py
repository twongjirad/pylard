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

NSPERTICK = 15.625

class OpDetDisplay(QtGui.QWidget) :
    def __init__(self, opdata):
        super(OpDetDisplay,self).__init__()
        self.resize( 1200, 700 )


        # Set the data
        self.opdata = opdata

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
        
        # Plot optionsd
        if opdata is not None:
            self.event = QtGui.QLineEdit("%d"%(opdata.first_event))     # event number
        else:
            self.event = QtGui.QLineEdit("0") # event number
        self.slot  = QtGui.QLineEdit("5")     # slot number
        self.collapse = QtGui.QCheckBox("Overlay Mode")  # collapse onto one another
        self.collapse.setChecked(False)
        self.prev_event = QtGui.QPushButton("Previous")
        self.next_event = QtGui.QPushButton("Next")
        self.adc_scaledown = QtGui.QLineEdit("100.0")
        self.draw_all = QtGui.QCheckBox("draw all")  # collapse onto one another
        self.draw_all.setChecked(False)
        self.draw_cosmics = QtGui.QCheckBox("draw cosmics")
        self.draw_cosmics.setChecked(True)
        self.lay_inputs.addWidget( QtGui.QLabel("Event"), 0, 0 )
        self.lay_inputs.addWidget( self.event, 0, 1 )
        self.lay_inputs.addWidget( QtGui.QLabel("FEM Slot"), 0, 2 )
        self.lay_inputs.addWidget( self.slot, 0, 3 )
        self.lay_inputs.addWidget( QtGui.QLabel("ADC scale-down"), 0, 4 )
        self.lay_inputs.addWidget( self.adc_scaledown, 0, 5 )
        self.lay_inputs.addWidget( self.collapse, 0, 8 )
        self.lay_inputs.addWidget( self.draw_all, 0, 9 )
        self.lay_inputs.addWidget( self.prev_event, 0, 11 )
        self.lay_inputs.addWidget( self.next_event, 0, 12 )
        self.last_clicked_channel = None
        self.user_plot_item = {} # storage for user plot items

        # axis options
        self.set_xaxis = QtGui.QPushButton("Re-plot!")
        self.openCosmicWindow = QtGui.QPushButton("Cosmic Disc. Viewer")
        self.draw_user_items = QtGui.QCheckBox("draw user items")  # draw user products
        self.draw_user_items.setChecked(True)
        self.run_user_analysis = QtGui.QCheckBox("run user funcs.")  # draw user products
        self.run_user_analysis.setChecked(True)

        self.lay_inputs.addWidget( self.draw_cosmics, 1, 9 )
        self.lay_inputs.addWidget( self.draw_user_items, 1, 10 )
        self.lay_inputs.addWidget( self.run_user_analysis, 1, 11 )
        self.lay_inputs.addWidget( self.set_xaxis, 1, 12 )

        # other options
        self.channellist = [] # when not None, only draw channels in this list
        self.pedfunction = self.getpedestal

        # user analyses
        self.user_analysis_products = []
        self.user_analyses = []

        # connect
        self.set_xaxis.clicked.connect( self.plotData )
        self.next_event.clicked.connect( self.nextEvent )
        self.prev_event.clicked.connect( self.prevEvent )
        self.pmtdiagram.sigClicked.connect( self.pmtDiagramClicked )
        #self.pmtdiagram.scene().sigMouseMoved.connect(self.onMovePMTdiagram)
        
        
    def plotData( self ):

        evt = int(self.event.text())
        slot = int(self.slot.text())
        if self.lastevent is None or evt!=self.lastevent:
            self.opdata.gotoEvent( evt )
            self.lastevent = evt
            self.newevent = True
        else:
            #print "old event: ",self.lastevent
            self.newevent = False
        
        scaledown = float( self.adc_scaledown.text() )
        
        # --------------------------------------------------
        # WFM PLOT

        # reset
        self.wfplot.clear()

        # get plotting options
        offset = 1.0
        if self.collapse.isChecked():
            offset = 0.0
            scaledown = 1.0

        # get discriminator window time range
        nsrange = self.time_window.getTimeRangeNS()

        # get the windows to draw
        wfmdata = self.opdata.getWaveformPlotData( nsrange[0], nsrange[1] )
        
        for window in wfmdata:
            
            ipmt = window.ch
            islot = window.slot            

            # check if we draw this channel
            if islot!=slot:
                continue

            if len(self.channellist)>0 and ipmt not in self.channellist and not self.draw_all.isChecked():
                continue
            
            pencolor = self.getChanColor( ipmt )
            if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                pencolor = (0, 255, 255 )

            ped = self.pedfunction(window.wfm,ipmt)
            #print ipmt,": ",ped
            y = (window.wfm-ped)/scaledown+ipmt*offset
            x = window.genTimeArray()

            self.wfplot.plot(x=x, y=y, pen=pencolor)

        if  self.draw_user_items.isChecked():
            userwfms = self.opdata.getUserPlotData( nsrange[0], nsrange[1] )
            print "number of user wfms: ",len(userwfms)
            for wfm in userwfms:
                ipmt = wfm.ch
                if ipmt is not None and (len(self.channellist)>0 and ipmt not in self.channellist and not self.draw_all.isChecked()):
                    continue
                pencolor = wfm.default_color
                if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                    pencolor = wfm.highlighted_color
                y = wfm.wfm
                x = wfm.genTimeArray()
                self.wfplot.plot( x=x, y=y, pen=pencolor )
            
        # refresh range object
        self.wfplot.addItem( self.wf_time_range )

        # axis!
        ax = self.wfplot.getAxis('bottom')
        ax.setHeight(30)
        xStyle = {'color':'#FFFFFF','font-size':'14pt'}
        #ax.setLabel('64 MHz Sample Tick',**xStyle)
        ax.setLabel('ns from readout start',**xStyle)
        ay = self.wfplot.getAxis('left')
        yStyle = {'color':'#FFFFFF','font-size':'14pt'}
        if self.collapse.isChecked():
            ay.setLabel('ADC counts - Pedestal',**yStyle)
        else:
            ay.setLabel('PMT Channel Number',**yStyle)

        # Cosmic Window
        self.time_window.plotCosmicWindows( self.opdata.cosmicwindows )

        # ----------------------------------------------------
        # diagram object
        bnds = self.wf_time_range.getRegion()
        wfms = self.opdata.getWaveformPlotData( bnds[0], bnds[1] ) # this won't work for beam windows...
        #print "bounds: ",bnds," number of windows=",len(wfms)

        # we get the max within range
        chmaxes = {}
        for wfm in wfms:
            if slot!=wfm.slot:
                continue
            tstart = wfm.getTimestamp()
            tend   = wfm.getEndstamp()
            ch     = wfm.ch
            if ch not in chmaxes:
                chmaxes[ch] = 0.0

            tstart_tick = int( np.maximum( 0, (bnds[0]-tstart)/wfm.timepertick ) )
            tend_tick   = int( np.minimum( len(wfm.wfm), (bnds[1]-tstart)/wfm.timepertick ) )
            ped = self.pedfunction(wfm.wfm,ch)
            chmax = np.max( wfm.wfm[tstart_tick:tend_tick]-ped )
            if chmax>chmaxes[ch]:
                chmaxes[ch] = chmax

        # better interface here is needed
        self.pmtspot = []

        for ich in range(0,36):
            if ich>=36:
                continue
            if ich not in chmaxes:
                maxamp = 0.0
            else:
                maxamp = chmaxes[ich]
            ipmt = getPMTID( ich )-1
            #print "maxamp: id=",ipmt,' max=',maxamp,' ped=',self.pedfunction(wfm,ich)
            col = self.pmtscale.colorMap().map( (maxamp)/2048.0 )
            alpha = 255
            if len(self.channellist)>0 and ipmt not in self.channellist:
                alpha = 50
            bordercol = self.getChanColor( ipmt, alpha=alpha )
            if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                bordercol = ( 0, 255, 255, alpha )
            if ipmt in getPMTIDList():
                pos = getPosFromID(ipmt )
                self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":30, 'pen':{'color':bordercol,'width':2}, 'brush':col, 'symbol':'o', 'data':{"id":ipmt,"highlight":False}} )

            elif ipmt in getPaddleIDList():
                pos = getPosFromID( ipmt )
                self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":25, 'pen':{'color':bordercol,'width':2}, 'brush':col, 'symbol':'s', 'data':{"id":ipmt,"highlight":False}} )
        self.pmtdiagram.setData( self.pmtspot  )

        # ----------------------------------------------------
        # added user items

        if self.draw_user_items.isChecked() and None in self.user_plot_item.keys():
            for useritem in self.user_plot_item[None]:
                
                self.wfplot.addItem( useritem )

        # ----------------------------------------------------
        # user analysis items
        if self.run_user_analysis.isChecked():
            # if new event: generate products
            if self.newevent or len(self.user_analysis_products)==0:
                self.user_analysis_products = []
                for userfunc in self.user_analyses:
                    user_products = userfunc( self.opdata, self )
                    for product in user_products:
                        productok = True
                        for k in ["femch","plotitem","screen"]:
                            if k not in product:
                                print "User analyss products needs to be a list of dicts with the following keys: 'femch', 'plotitem', 'screen'."
                                productok = False
                        if not productok:
                            continue
                        self.user_analysis_products.append( product )
            # plot products
            if self.draw_user_items.isChecked():
                for product in self.user_analysis_products:
                    ch = product["femch"]
                    if len(self.channellist)>0 and ch not in self.channellist and not self.draw_all.isChecked():
                        continue
                    item = product["plotitem"]
                    if product["screen"]=="diagram":
                        self.pmtdiagram.addItem( item )
                    elif product["screen"]=="waveform":
                        self.wfplot.addItem( item )
                    else:
                        print "unknonw user product screen option, '",product["screen"],"'. Valid choices are 'diagram' and 'waveform'"
        
    def nextEvent(self):

        ok = self.opdata.getNextEntry()
        if ok:
            evt = self.opdata.event
            slot = int(self.slot.text())
            self.event.setText("%d"%(evt))
        else:
            print "Next event not ok"
            #self.opdata.gotoEvent( evt )
        self.plotData()

    def prevEvent(self):
        evt = int(self.event.text())
        slot = int(self.slot.text())
        try:
            self.opdata.gotoEvent( evt-1 )
            evt = self.opdata.event
            self.event.setText("%d"%(evt))
        except:
            # reload old event
            self.opdata.gotoEvent( evt )
        self.plotData()
            
    def getWaveformPlot(self):
        return self.wfplot
    
    def getPMTdiagram(self):
        return self.pmtdiagram
            
    def gotoEvent( self, event, slot=None ):
        evt = int(self.event.text())
        if slot is None:
            slot = int(self.slot.text())
        else:
            self.slot.setText("%d"%(slot))
        
        try:
            more = self.opdata.gotoEvent( event )
            self.event.setText( "%d"%(event) )
        except:
            more = self.opdata.gotoEvent( evt )
        self.plotData()
        return more
            
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
        
    def showCosmicDisplay( self ):
        self.cosmicdisplay.show()
                
