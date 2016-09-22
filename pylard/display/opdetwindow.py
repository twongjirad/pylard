import os,sys,copy
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict

from pylard.config.pmt_chmap import getPMTID, getChannel, getPMTIDList, getPaddleIDList
from pylard.config.pmtpos import getPosFromID 
from pylard.display.pmtposscatterplot import PMTScatterPlot
from pylard.display.cosmicwindow import CosmicWindow
import pylard.pylardata.pedestal as pedestal
from pylard.pylardata.opdataplottable import OpDataPlottable

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
        # graphics window
        self.graphics.addItem( self.pmt_map, 0, 0, rowspan=2 )
        self.graphics.addItem( self.pmtscale, 2, 0, rowspan=1 )
        self.graphics.addItem( self.wfplot, 3, 0, rowspan=3 )
        self.graphics.addItem( self.time_window, 6, 0, rowspan=1 )
        self.layout.addWidget( self.graphics, 0, 0, 8, 1 )
        self.setLayout(self.layout)

        # -------------
        # Input Widgets
        # -------------
                
        opdata = None # Temp hack

        self.last_clicked_channel = None
        self.user_plot_item = {} # storage for user plot items

        # input layout
        self.lay_inputs = QtGui.QGridLayout()
        navframe = self._makeNavFrame()
        optframe = self._makeOptionsFrame()
        usrframe = self._makeUserItemsFrame()
        self.lay_inputs.addWidget( navframe, 0, 0 )
        self.lay_inputs.addWidget( optframe, 0, 1 )
        self.lay_inputs.addWidget( usrframe, 0, 2 )

        # addd input layout
        self.layout.addLayout( self.lay_inputs, 8, 0, 1, 1)

        # other options
        self.channellist = [] # when not None, only draw channels in this list
        self.pedfunction = self.getpedestal

        # vis products
        self.vis_items = {}

        # user analyses
        self.user_analysis_products = []
        self.user_analyses = []

        # main window
        self.themainwindow = None

    def setMainWindow( self, window ):
        self.themainwindow = window

    def clearVisItems(self):
        self.vis_items = {}

    # --------------------------------------------------
    # --------------------------------------------------
    
    def _makeNavFrame(self):
        navframe        = QtGui.QFrame()
        navframe.setLineWidth(1)
        navframe.setFrameShape( QtGui.QFrame.Box )
        navframe_layout = QtGui.QGridLayout()

        self.entry  = QtGui.QLineEdit("")  # entry number
        self.run    = QtGui.QLineEdit("")  # run number
        self.subrun = QtGui.QLineEdit("")  # run number
        self.event  = QtGui.QLineEdit("")  # run number
        self.slot   = QtGui.QLineEdit("5") # slot number
        self.adc_scaledown = QtGui.QLineEdit("20.0")
        self.prev_event = QtGui.QPushButton("Previous")
        self.next_event = QtGui.QPushButton("Next")
        self.get_event  = QtGui.QPushButton("Goto Entry")
        self.get_rse  = QtGui.QPushButton("Goto RSE")
        self.replot = QtGui.QPushButton("Re-plot!")

        navframe_layout_top = QtGui.QGridLayout()
        navframe_layout_bot = QtGui.QGridLayout()

        entrylabel  = QtGui.QLabel("Entry")
        runlabel    = QtGui.QLabel("Run")
        subrunlabel = QtGui.QLabel("Subrun")
        eventlabel  = QtGui.QLabel("Event")
        femlabel    = QtGui.QLabel("FEM")
        adc_scale_label = QtGui.QLabel("ADC scale-down")

        entrylabel.setFixedWidth(30)
        runlabel.setFixedWidth(25)
        subrunlabel.setFixedWidth(50)
        eventlabel.setFixedWidth(35)
        adc_scale_label.setFixedWidth(100)

        navframe_layout_top.addWidget( entrylabel,  0, 0 )
        navframe_layout_top.addWidget( self.entry,  0, 1 )
        navframe_layout_top.addWidget( runlabel,    0, 2 )
        navframe_layout_top.addWidget( self.run,    0, 3 )
        navframe_layout_top.addWidget( subrunlabel, 0, 4 )
        navframe_layout_top.addWidget( self.subrun, 0, 5 )
        navframe_layout_top.addWidget( eventlabel,  0, 6 )
        navframe_layout_top.addWidget( self.event,  0, 7 )
        navframe_layout_top.addWidget( femlabel,    0, 8 )
        navframe_layout_top.addWidget( self.slot,   0, 9 )
        navframe_layout_top.addWidget( adc_scale_label, 0, 10 )
        navframe_layout_top.addWidget( self.adc_scaledown, 0, 11 )
        
        navframe_layout_bot.addWidget( self.replot,     0, 0 )
        navframe_layout_bot.addWidget( self.prev_event, 0, 1 )
        navframe_layout_bot.addWidget( self.next_event, 0, 2 )
        navframe_layout_bot.addWidget( self.get_event,  0, 3 )
        navframe_layout_bot.addWidget( self.get_rse,    0, 4 )

        navframe_layout.addLayout( navframe_layout_top, 0, 0 )
        navframe_layout.addLayout( navframe_layout_bot, 1, 0 )

        navframe.setLayout( navframe_layout )

        # connect signals
        self.replot.clicked.connect( self.plotData )
        self.next_event.clicked.connect( self.nextEntry )
        self.prev_event.clicked.connect( self.prevEntry )
        self.get_event.clicked.connect( self.getEntry )
        self.get_rse.clicked.connect( self.getRSE )
        self.pmtdiagram.sigClicked.connect( self.pmtDiagramClicked )

        return navframe
        
    def _makeOptionsFrame(self):
        opt_frame        = QtGui.QFrame()
        opt_frame.setLineWidth(1)
        opt_frame.setFrameShape( QtGui.QFrame.Box )
        opt_frame_layout = QtGui.QGridLayout()
        
        # control the waveform viewer
        self.collapse = QtGui.QCheckBox("overlay mode")  # collapse onto one another
        self.collapse.setChecked(False)
        self.draw_diag = QtGui.QCheckBox("diagram")  # collapse onto one another
        self.draw_diag.setChecked(True)
        self.draw_cosmics = QtGui.QCheckBox("disc. windows")
        self.draw_cosmics.setChecked(True)
        self.draw_only_PMTs = QtGui.QCheckBox("no logic")  # draw only PMTs
        self.draw_only_PMTs.setChecked(False)
        self.draw_chlabels = QtGui.QCheckBox("channel labels")  # draw user products
        self.draw_chlabels.setChecked(False)
        #self.run_user_analysis = QtGui.QCheckBox("run user funcs.")  # draw user products
        #self.run_user_analysis.setChecked(True)

        opt_frame_layout.addWidget( QtGui.QLabel("Options"), 0, 0)
        opt_frame_layout.addWidget( self.collapse,           0, 1 )
        opt_frame_layout.addWidget( self.draw_only_PMTs,     0, 2 )
        opt_frame_layout.addWidget( self.draw_diag,          1, 0 )
        opt_frame_layout.addWidget( self.draw_cosmics,       1, 1 )
        opt_frame_layout.addWidget( self.draw_chlabels,      1, 2 )

        for checkbox in [ self.collapse, self.draw_diag, self.draw_cosmics, self.draw_only_PMTs, self.draw_chlabels ]:
            checkbox.stateChanged.connect( self.plotData )

        opt_frame.setLayout( opt_frame_layout )

        return opt_frame

    def _makeUserItemsFrame(self):
        user_frame        = QtGui.QFrame()
        user_frame.setLineWidth(1)
        user_frame.setFrameShape( QtGui.QFrame.Box )
        user_frame_layout = QtGui.QGridLayout()
        self.user_items = pg.TreeWidget()
        self.user_items.setFixedHeight(   80 )
        self.user_items.setMinimumWidth( 300 )
        self.draw_user_items = QtGui.QCheckBox("draw user items")  # draw user products
        self.draw_user_items.setChecked(True)

        user_frame_layout.addWidget( self.draw_user_items, 0, 0, 1, 1 )
        user_frame_layout.addWidget( self.user_items,      1, 0, 5, 2 )
        user_frame.setLayout( user_frame_layout )

        return user_frame

    # --------------------------------------------------
    # --------------------------------------------------
        
    def plotData( self ):

        # prep window
        print self.vis_items

        # setup the graphics
        self.setGraphicsLayout()
        scaledown = float( self.adc_scaledown.text() )
        
        # clear
        self.wfplot.clear()

        # get plotting options
        offset = 1.0
        if self.collapse.isChecked():
            offset = 0.0
            scaledown = 1.0

        # get discr window time range
        nsrange = self.time_window.getTimeRangeNS()

        # draw waveforms
        self.drawWaveforms(offset,scaledown,nsrange)

        # draw user waveforms
        if self.draw_user_items.isChecked():
            self.drawUserWaveforms(offset,scaledown,nsrange)

        # refresh range object
        self.wfplot.addItem( self.wf_time_range )

        # axis
        ax = self.wfplot.getAxis('bottom')
        ax.setHeight(30)
        xStyle = {'color':'#FFFFFF','font-size':'14pt'}
        ax.setLabel('ns from readout start',**xStyle)
        ay = self.wfplot.getAxis('left')
        yStyle = {'color':'#FFFFFF','font-size':'14pt'}
        if self.collapse.isChecked():
            ay.setLabel('ADC counts - Pedestal',**yStyle)
        else:
            ay.setLabel('PMT Channel Number',**yStyle)

        # cosmic window
        opdata = self.vis_items["opdata"]
        self.time_window.plotCosmicWindows( opdata.cosmicwindows )

        # pmt diagram
        self.drawDiagramData()
        
    def nextEntry(self):
        ok = self.themainwindow.nextEntry()
        if not ok:
            return ok

    def prevEntry(self):
        ok = self.themainwindow.prevEntry()
        if not ok:
            return ok

    def getEntry( self ):
        entry = int( self.entry.text() )
        ok = self.themainwindow.getEntry( entry )
        if not ok:
            return ok

    def getRSE( self ):
        rse = ( int(self.run.text()), int(self.subrun.text()), int(self.event.text()) )
        ok = self.themainwindow.getRSE( rse[0], rse[1], rse[2] )
        if not ok:
            return ok
            
    def getWaveformPlot(self):
        return self.wfplot
    
    def getPMTdiagram(self):
        return self.pmtdiagram            
            
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

    def setEntryNumbers( self, entry, run, subrun, event ):
        self.entry.setText("%d"%(entry))
        self.run.setText("%d"%(run))
        self.subrun.setText("%d"%(subrun))
        self.event.setText("%d"%(event))

    def drawWaveforms(self,offset,scaledown,nsrange):
        if "opdata" in self.vis_items:
            opdata = self.vis_items["opdata"]
        else:
            print "Need VisItem with name \"opdata\""
            return

        print "Draw waveforms beween: ",nsrange," ticks"

        # get the windows to draw
        wfmdata = opdata.getWaveformPlotData( nsrange[0], nsrange[1] )
        slot = int(self.slot.text())
        for window in wfmdata:
            ipmt  = window.ch
            islot = window.slot
            # skip (or not) the logic channels
            if self.draw_only_PMTs.isChecked():
                if ipmt%100>=32:
                    continue
            # check if we draw this channel
            if islot!=slot:
                continue

            if len(self.channellist)>0 and ipmt not in self.channellist:
                continue

            pencolor = self.getChanColor(ipmt)
            if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                pencolor = (0, 255, 255 )

            ped = self.pedfunction(window.wfm,ipmt)
            y = (window.wfm-ped)/scaledown+ipmt*offset
            x = window.genTimeArray()
            #print "draw wfm islot=",islot," ipmt=",ipmt
            self.wfplot.plot(x=x,y=y,pen=pencolor)

    def drawUserWaveforms(self,offset,scaledown,nsrange):
        
        for name,vis in self.vis_items.items():
            if name=="opdata":
                continue
            if not issubclass(vis,OpDataPlottable):
                continue

            userwfms = self.vis_items[name].getWaveformPlotData( nsrange[0], nsrange[1] )
            for wfm in userwfms:
                ipmt = wfm.ch
                if ipmt is not None and (len(self.channellist)>0 and ipmt not in self.channellist):
                    continue
                pencolor = wfm.default_color
                if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                    pencolor = wfm.highlighted_color

                if ipmt is not None:
                    y = np.asarray(wfm.wfm)/scaledown + ipmt*offset
                else:
                    y = wfm.wfm
                
                x = wfm.genTimeArray()
                self.wfplot.plot( x=x, y=y, pen=pencolor )

    def addVisItem( self, name, product ):
        self.vis_items[name] = product

    def drawDiagramData(self,):
        slot = int(self.slot.text())
        bnds = self.wf_time_range.getRegion()
        if "opdata" not in self.vis_items:
            return
        wfms = self.vis_items["opdata"].getWaveformPlotData( bnds[0], bnds[1] ) # this won't work for beam windows...
        
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
        self.pmt_map.clear()
        self.pmtspot = []
        self.pmtlabels = []

        for ich in range(0,36):
            if ich>=36:
                continue
            if ich not in chmaxes:
                maxamp = 0.0
            else:
                maxamp = chmaxes[ich]
            ipmt = getPMTID( ich )-1
            col = self.pmtscale.colorMap().map( (maxamp)/2048.0 )
            alpha = 255
            if len(self.channellist)>0 and ipmt not in self.channellist:
                alpha = 50
            bordercol = self.getChanColor( ipmt, alpha=alpha )
            if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                bordercol = ( 0, 255, 255, alpha )

            # beam goes right to left!
            # note that pmt pos are in larsoft coordinates with origin moved such that drawing is in center of detector
            # we have to invert the z!
            if ipmt in getPMTIDList():
                pos = getPosFromID(ipmt, origin_at_detcenter=True )
                self.pmtspot.append( {"pos":(-pos[2],pos[1]), "size":30, 'pen':{'color':bordercol,'width':2}, 'brush':col, 'symbol':'o', 'data':{"id":ipmt,"highlight":False}} )
            elif ipmt in getPaddleIDList():
                pos = getPosFromID( ipmt, origin_at_detcenter=True )
                self.pmtspot.append( {"pos":(-pos[2],pos[1]), "size":25, 'pen':{'color':bordercol,'width':2}, 'brush':col, 'symbol':'s', 'data':{"id":ipmt,"highlight":False}} )
            # add label
            if self.draw_chlabels.isChecked():
                pmtlabel = pg.TextItem( "CH%d" %(ipmt), color=bordercol, anchor=(0.5,0.5) )
                pmtlabel.setFont( QtGui.QFont("Helvetica [Cronyx]",10) )
                pmtlabel.setPos( -pos[2], pos[1]+26 )
                self.pmtlabels.append( pmtlabel )
                self.pmt_map.addItem( pmtlabel )

        self.pmtdiagram.setData( self.pmtspot  )
        self.pmt_map.addItem( self.pmtdiagram )
