import os,sys,copy
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict

from pylard.config.pmt_chmap import getPMTID, getChannel, getPMTIDList, getPaddleIDList
from pylard.config.pmtpos import getPosFromID 
from pylard.pylardisplay.cosmicdiscdisplay import CosmicDiscDisplay
from pylard.pylardisplay.cosmicwindow import CosmicWindow

# dumb utility functions to import
from functions import getFlashSize

# PMT scatter-plot items
from ScatterPMT import ScatterPMT

samplesPerFrame = 102400
NSPERTICK = 15.625
USPERTICK = NSPERTICK/1000.

class OpDetDisplay(QtGui.QWidget) :

    def __init__(self, opdata):

        super(OpDetDisplay,self).__init__()
        self.opdata = opdata

        # Plots
        # Mother canvas for plots
        self.graphics = pg.GraphicsLayoutWidget()

        # 1) waveform plotting region
        self.wfplot = pg.PlotItem(name="Wf Plot")
        # 2) pmt plotting diagram
        self.pmt_map = pg.PlotItem(name="PMT map")
        # PMT scatter points
        self.pmtdiagram   = ScatterPMT() #pg.ScatterPlotItem(pxMode=False)
        self.pmt_map.addItem( self.pmtdiagram ) 
        # 3) time-range selction window
        self.time_window = CosmicWindow()
        
        self.pmtscale =  pg.GradientEditorItem(orientation='bottom')
        self.lastevent = None
        self.newevent = True

        # main layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        #self.layout.addWidget( self.graphics, 0, 0 )
        #self.graphics.addItem( self.pmt_map, 0, 0 )
        #self.graphics.addItem( self.pmtscale, 1, 0 )
        #self.graphics.addItem( self.plot, 2, 0 )
#=======
        self.layout.addWidget( self.graphics, 0, 0, 1, 10 )
        self.graphics.addItem( self.pmt_map, 0, 0, rowspan=2 )
        self.graphics.addItem( self.pmtscale, 2, 0, rowspan=1 )
        self.graphics.addItem( self.wfplot, 3, 0, rowspan=3 )
        self.graphics.addItem( self.time_window, 6, 0, rowspan=1 )
#>>>>>>> origin/develop_OpHit_OpFlash_viewer
        self.lay_inputs = QtGui.QGridLayout()
        self.layout.addLayout( self.lay_inputs, 7, 0 )
        
        # inputs widgets layout
        
        # Plot options
        if opdata is not None:
            #self.run    = QtGui.QLineEdit("%d"%(opdata.run))   # run
            #self.subrun = QtGui.QLineEdit("%d"%(opdata.subrun)) # subrun
            self.event  = QtGui.QLineEdit("%d"%(opdata.event)) # event
        else:
            self.event = QtGui.QLineEdit("0") # event number
        self.slot  = QtGui.QLineEdit("5")     # slot number
        self.collapse = QtGui.QCheckBox("Overlay Mode")  # collapse onto one another
        self.collapse.setChecked(False)
        self.beam_window = QtGui.QPushButton("Beam Window")
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
        self.lay_inputs.addWidget( self.prev_event, 0, 10 )
        self.lay_inputs.addWidget( self.next_event, 0, 11 )
        self.lay_inputs.addWidget( self.beam_window, 1, 12 )
        self.last_clicked_channel = None
        self.user_plot_item = {} # storage for user plot items

        # axis options
        self.set_xaxis = QtGui.QPushButton("Re-plot!")
        self.openCosmicWindow = QtGui.QPushButton("Cosmic Disc. Viewer")
        self.draw_user_items = QtGui.QCheckBox("draw user items")  # draw user products
        self.draw_user_items.setChecked(True)
        self.run_user_analysis = QtGui.QCheckBox("run user funcs.")  # draw user products
        self.run_user_analysis.setChecked(True)

        self.lay_inputs.addWidget( self.openCosmicWindow, 1, 0, 1, 2 )
        self.lay_inputs.addWidget( self.draw_cosmics, 1, 9 )
        self.lay_inputs.addWidget( self.draw_user_items, 1, 10 )
        self.lay_inputs.addWidget( self.run_user_analysis, 1, 11 )
        self.lay_inputs.addWidget( self.set_xaxis, 1, 12 )

        #self.lay_inputs.addWidget( QtGui.QLabel("Draw Flashes"), 1, 6 )
        #self.lay_inputs.addWidget( self.draw_flashes, 1, 7 )
        #self.lay_inputs.addWidget( QtGui.QLabel("Draw OpHits"), 1, 8 )
        #self.lay_inputs.addWidget( self.draw_ophits, 1, 9 )
        #self.lay_inputs.addWidget( self.set_xaxis, 0, 12 )

        # range selections
        self.time_range = pg.LinearRegionItem(values=[-0.01,24], orientation=pg.LinearRegionItem.Vertical)
        self.wfplot.addItem( self.time_range )
        
        # array of pmt-maxima in time_range
        self.pmt_max = np.zeros(32)

        # Flash scatter points
        self.flashdiagram = pg.ScatterPlotItem(pxMode=False) 

        # other options
        self.channellist = [] # when not None, only draw channels in this list

        # user analyses
        self.user_analysis_products = []
        self.user_analyses = []

        # cosmic display subwindow
        self.cosmicdisplay = CosmicDiscDisplay(self)

        # connect functions
        # main window
        self.set_xaxis.clicked.connect( self.plotData )
        self.next_event.clicked.connect( self.nextEvent )
        self.prev_event.clicked.connect( self.prevEvent )
        self.beam_window.clicked.connect( self.scaleToBeam )
        # pmt diagram
        self.connectPMTdiagram()

    # --------------------------
    # scale event to beam window
    def scaleToBeam( self ):

        self.time_window.setTickWindow([-50,1550])
        self.plotData()

    # ----------------------
    # draw data on GUI -----
    def plotData( self ):

        evt = int(self.event.text())
        
        # if this is a new event
        if self.lastevent is None or evt!=self.lastevent:
            print 'getting new event'
            self.opdata.getEvent( evt )
            self.lastevent = evt
            self.newevent = True
        else:
            #print "old event: ",self.lastevent
            self.newevent = False
        
        scaledown = float( self.adc_scaledown.text() )
        
        # --------------------------------------------------
        # clear time-window display
        #self.time_window.clear()
        
        # clear the pmt-maxima
        #self.pmt_max = np.zeros(32)
        
        # BEAM SAMPLE WINDOW
        self.wfplot.clear()
        offset = 1.0
        if self.collapse.isChecked():
            offset = 0.0
            scaledown = 1.0
        
        # start plotting waveforms
        wfs = self.opdata.opdetwf.getData()

        # get OpHits
        hits = self.opdata.ophits.getData()
        self.hitdiagram = pg.ScatterPlotItem(pxMode=False) 
        self.hitspots = []

        # what are the bounds that we want to plot in?
        bounds = self.time_window.time_range.getRegion() # usec
        # pmt-color scale bounds
        pmt_bnds = self.time_range.getRegion() # usec

        # if the time_range for PMT drawing is outside of the bounds of what is shown in the middle window
        # then re-adjust range so that the window is fully contained
        if (pmt_bnds[1] < bounds[0]):
            pmt_bnds = ( bounds[0] , bounds[1] )
        elif (pmt_bnds[0] > bounds[1]):
            pmt_bnds = ( bounds[0] , bounds[1] )
        elif ( (pmt_bnds[0] < bounds[0]) and (pmt_bnds[1] > bounds[1]) ):
            pmt_bnds = ( bounds[0] , bounds[1] )
        elif (pmt_bnds[0] < bounds[0]):
            pmt_bnds = ( bounds[0] , pmt_bnds[1] )
        elif (pmt_bnds[1] > bounds[1]):
            pmt_bnds = ( bounds[0], bounds[1] )
        else:
            pmt_bnds = (pmt_bnds[0], pmt_bnds[1])
        self.time_range = pg.LinearRegionItem(values=pmt_bnds, orientation=pg.LinearRegionItem.Vertical)

        # scale to ticks
        bounds = np.array(bounds)/USPERTICK
        bounds[0] = int(bounds[0])
        bounds[1] = int(bounds[1])

        # event time-range
        event_time_range = self.opdata.opdetwf.event_time_range
        event_time_len = event_time_range[1]-event_time_range[0]
        # time-tick values
        TDCs = np.linspace( event_time_range[0], event_time_range[1], int(event_time_len/USPERTICK) )

        #print 'time-tick length = %i'%len(TDCs)
        if (len(TDCs) > 102400*5):
            return
            
        #if (self.draw_flashes.isChecked() == True):
        #    # add all the flashes
        #    flashes = self.opdata.opflash.flashes
        #    for flash in flashes:
        #        
        #        time = flash[0]
        #        flashInfo = flashes[flash]
        #        PE = flashInfo[0]
        #        Ypos = flashInfo[1]
        #        Zpos = -(flashInfo[2]-(1036./2))
        #        #if (PE > 10):
        #        self.wfplot.addLine(time, movable=False, pen={'color':(255,255,0,255),'width':2})


        # for all PMTs
        for ipmt in wfs:

            # if we only want to plot selected PMTs, and this PMT is not in the list -> continue
            if len(self.channellist)>0 and ipmt not in self.channellist and not self.draw_all.isChecked():
                continue

            # prepare a baseline pmt pulse for the entire time-range
            pmt_wf = np.ones(len(TDCs))*self.opdata.opdetwf.pedestals[ipmt]
            
            pmt_pulses = wfs[ipmt]
            
            # loop through all pulses found
            for pulse_start in pmt_pulses:
                
                # pulse_start is in usec
                # get the corresponding time-tick
                pulse_ADCs = pmt_pulses[pulse_start]

                pulse_start_tick = int((pulse_start - event_time_range[0])/USPERTICK)       # ticks
                pulse_end_tick   = pulse_start_tick + len(pulse_ADCs)  # ticks
                pulse_start_usec = pulse_start
                pulse_end_usec   = pulse_start_usec + len(pulse_ADCs)*USPERTICK    # usec
                #print 'pulse region : [%i,%i]'%(pulse_start_tick,pulse_end_tick)
                #print 'adding wf to time-region [%i,%i]'%(pulse_start,pulse_end)
                #print 'wf : ',pulse_ADCs
                pmt_wf[ pulse_start_tick : pulse_end_tick ] = pulse_ADCs
                
                # if pulse is in the pmt-color range
                if ( ( (pulse_start_usec) > pmt_bnds[0]) and ( (pulse_end_usec) < pmt_bnds[1]) ):
                    adcmax = np.max(pulse_ADCs) - self.getPedestal(ipmt)
                    if ( adcmax > self.pmt_max[ipmt] ):
                        self.pmt_max[ipmt] = adcmax


                        
            pencolor = self.getChanColor( ipmt )
            if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                pencolor = (0, 255, 255 )

            # set offset and subtract baseline
            ADCs = ( pmt_wf - self.getPedestal(ipmt) ) / scaledown + ipmt*offset
            
            # get the maximum amplitude
            maxamp = np.max( np.array(pmt_wf) ) - self.getPedestal(ipmt)
            
            # plot the waveform
            self.wfplot.plot(x=TDCs, y=ADCs, pen=pencolor, name="PMT%d"%(ipmt))

            # if we should draw hits
            if (self.draw_ophits.isChecked() == True):
                hits_pmt = hits[ipmt]
                for hit in hits_pmt:
                    self.hitspots.append( {"pos":(hit[0][0],ipmt*offset), "size":1, "pen":{'color':(255,0,0,200),'width':0}, "brush":(255,0,0,0), "symbol":"s"} )
            
            # plot the waveform in the cosmics window
            self.time_window.plot(x=TDCs, y=ADCs, pen=pencolor, name="PMT%d"%(ipmt))
            
            if ipmt in self.user_plot_item.keys():
                for useritem in self.user_plot_item[ipmt]:
                    self.wfplot.addItem( useritem )

        # set the range for the view
        self.wfplot.setXRange(bounds[0]*USPERTICK, bounds[1]*USPERTICK, update=True)

        self.hitdiagram.setData( self.hitspots )
        self.hitdiagram.addPoints( self.hitspots )
        self.wfplot.addItem( self.hitdiagram ) 

        if "cosmics" in dir(self.opdata):
            if self.newevent:
                # refresh the cosmic window display
                self.cosmicdisplay.plotCosmicWindows( self.opdata.cosmics )
            if self.draw_cosmics.isChecked():
                # overlay the cosmic waveforms
                self.cosmicdisplay.applyCosmicDiscRange( clearplot=False )

        # add the time-range
        #self.wfplot.addItem( self.time_range )
        #>>>>>>> origin/develop_OpHit_OpFlash_viewer


        # do any additional drawing to the cosmics window
        self.time_window.plotCosmicWindows(event_time_range)        

        
        # pmt and flash positions
        self.pmtspot = []

        for ich in xrange(self.opdata.getData( slot=int(self.slot.text() ) ).shape[1],-1,-1):
            if ich>=36:
                continue
            wfm =  self.opdata.getData( slot=int(self.slot.text() ) )[istart:iend,ich]
            maxamp = np.max( wfm )-self.pedfunction(wfm,ich)
            ipmt = getPMTID( ich )-1
            #print "maxamp: id=",ipmt,' max=',maxamp,' ped=',self.pedfunction(wfm,ich)
            col = self.pmtscale.colorMap().map( (maxamp)/2048.0 )
        #=======
        # first append PMTs with their appropriate color
        #for ich in xrange(32):
        #    
        #    ipmt = ich
        #    col = self.pmtscale.colorMap().map( ( self.pmt_max[ich] ) /self.getPedestal(ipmt) )
        #>>>>>>> origin/develop_OpHit_OpFlash_viewer
            alpha = 255
            if len(self.channellist)>0 and ipmt not in self.channellist:
                alpha = 50
            bordercol = self.getChanColor( ipmt, alpha=alpha )
            if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                bordercol = ( 0, 255, 255, alpha )
            if ipmt in getPMTIDList():
                pos = getPosFromID(ipmt )
                self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":30, 'pen':{'color':bordercol,'width':2}, 'brush':col, 'symbol':'o', 'data':{"id":ipmt,"highlight":False}} )



        # yellow
        yellow = (255,255,0,255)

        # if we are to draw flashes
        if (self.draw_flashes.isChecked() == True):

            # next append flashes
            for flash in flashes:

                time = flash[0]
                flashInfo = flashes[flash]
                PE   = flashInfo[0]
                Ypos = flashInfo[1]
                Zpos = -(flashInfo[2]-(1036./2))
                PEsize = int(getFlashSize(PE))
            
                # if the time is in the correct time-interval
                if ( ( time > pmt_bnds[0]) and ( time < pmt_bnds[1]) ):
                    self.pmtspot.append( {"pos":(Zpos,Ypos), "size":PEsize, "pen":{'color':yellow,'width':2}, "brush":yellow, "symbol":"d"} )

        self.pmtdiagram.setData( self.pmtspot )

        # axis!
        ax = self.wfplot.getAxis('bottom')
        ax.setHeight(30)
        xStyle = {'color':'#FFFFFF','font-size':'14pt'}
        #ax.setLabel('64 MHz Sample Tick',**xStyle)
        ax.setLabel('us from readout start',**xStyle)
        ay = self.wfplot.getAxis('left')
        yStyle = {'color':'#FFFFFF','font-size':'14pt'}
        if self.collapse.isChecked():
            ay.setLabel('ADC counts - Pedestal',**yStyle)
        else:
            ay.setLabel('PMT Channel Number',**yStyle)

        # ----------------------------------------------------
        # added user items

        if self.draw_user_items.isChecked() and None in self.user_plot_item.keys():
            for useritem in self.user_plot_item[None]:
                
                self.plot.addItem( useritem )

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
                        self.diagram.addItem( item )
                    elif product["screen"]=="waveform":
                        self.plot.addItem( item )
                    else:
                        print "unknonw user product screen option, '",product["screen"],"'. Valid choices are 'diagram' and 'waveform'"

    def connectPMTdiagram(self):
        """ Connect display functions to PMT Position Map """
        self.pmtdiagram.sigClicked.connect( self.pmtDiagramClicked )
        self.pmtdiagram.scene().sigMouseMoved.connect(self.onMovePMTdiagram)
        
    def nextEvent(self):

        evt = int(self.event.text())

        ok = self.opdata.getEvent( evt+1 )
        if ok:
            self.event.setText("%d"%(evt+1))
        else:
            print "Next event not ok"
            self.opdata.getEvent( evt )
        self.plotData()

    def prevEvent(self):
        evt = int(self.event.text())
        try:
            self.opdata.getEvent( evt-1 )
            self.event.setText("%d"%(evt-1))
        except:
            self.opdata.getEvent( evt )
        self.plotData()
            
    def getWaveformPlot(self):
        return self.wfplot
    
    def getPMTdiagram(self):
        return self.pmt_map

    # -------------------------------------
    # go to a specific event --------------
    def gotoEvent( self, event, slot=None ):
        evt = int(self.event.text())
        try:
            more = self.opdata.getEvent( event )
            self.event.setText( "%d"%(event) )
        except:
            more = self.opdata.getEvent( evt )
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

    def getPedestal(self,pmt):
        return self.opdata.opdetwf.pedestals[pmt]


    # -------------------------------------------
    # function that decides what to do when mouse
    # hovers over a point in the PMT diagram
    def onMovePMTdiagram(self, pos):

        act_pos = self.pmtdiagram.mapFromScene(pos)
        p1 = self.pmtdiagram.pointsAt(act_pos)
        
        #if (len(p1) != 0):
        #    print 'found %i SpotItems'%len(p1)
        #    print p1[0]
        #    print p1[0].brush
        #    print p1[0].data
