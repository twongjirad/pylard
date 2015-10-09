import os,sys
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
        self.graphics = pg.GraphicsLayoutWidget()
        # waveform plotting region
        self.wfplot = pg.PlotItem(name="Wf Plot")
        # pmt plotting diagram
        self.pmt_map = pg.PlotItem(name="PMT map")
        # time-range selction window
        self.time_window = CosmicWindow()
        #self.time_window = pg.PlotItem(name='Time Window')
        
        self.pmtscale =  pg.GradientEditorItem(orientation='bottom')
        self.lastevent = None
        self.newevent = True

        # main layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget( self.graphics, 0, 0, 1, 10 )
        self.graphics.addItem( self.pmt_map, 0, 0, rowspan=2 )
        self.graphics.addItem( self.pmtscale, 2, 0, rowspan=1 )
        self.graphics.addItem( self.wfplot, 3, 0, rowspan=3 )
        self.graphics.addItem( self.time_window, 6, 0, rowspan=1 )
        self.lay_inputs = QtGui.QGridLayout()
        self.layout.addLayout( self.lay_inputs, 7, 0 )
        
        # inputs layout
        # widgets
        
        # Plot optionsd
        if opdata is not None:
            self.run    = QtGui.QLineEdit("%d"%(opdata.run))   # run
            self.subrun = QtGui.QLineEdit("%d"%(opdata.subrun)) # subrun
            self.event  = QtGui.QLineEdit("%d"%(opdata.event)) # event
        else:
            self.run    = QtGui.QLineEdit("0")   # run
            self.subrun = QtGui.QLineEdit("0") # subrun
            self.event  = QtGui.QLineEdit("0") # event
        self.collapse = QtGui.QCheckBox()  # collapse onto one another
        self.collapse.setChecked(False)
        self.beam_window = QtGui.QPushButton("Beam Window")
        self.prev_event = QtGui.QPushButton("Previous")
        self.next_event = QtGui.QPushButton("Next")
        self.adc_scaledown = QtGui.QLineEdit("100.0")
        self.draw_all = QtGui.QCheckBox()  # collapse onto one another
        self.draw_all.setChecked(False)
        self.lay_inputs.addWidget( QtGui.QLabel("Run"), 0, 0 )
        self.lay_inputs.addWidget( self.run, 0, 1 )
        self.lay_inputs.addWidget( QtGui.QLabel("Subrun"), 0, 2 )
        self.lay_inputs.addWidget( self.subrun, 0, 3 )
        self.lay_inputs.addWidget( QtGui.QLabel("Event"), 0, 4 )
        self.lay_inputs.addWidget( self.event, 0, 5 )
        self.lay_inputs.addWidget( QtGui.QLabel("ADC scale-down"), 1, 0 )
        self.lay_inputs.addWidget( self.adc_scaledown, 1, 1 )
        self.lay_inputs.addWidget( QtGui.QLabel("Overlay Mode"), 0, 6 )
        self.lay_inputs.addWidget( self.collapse, 0, 7 )
        self.lay_inputs.addWidget( QtGui.QLabel("Draw all"), 0, 8 )
        self.lay_inputs.addWidget( self.draw_all, 0, 9 )
        self.lay_inputs.addWidget( self.prev_event, 0, 10 )
        self.lay_inputs.addWidget( self.beam_window, 1, 10 )
        self.lay_inputs.addWidget( self.next_event, 0, 11 )
        self.last_clicked_channel = None
        self.user_plot_item = {} # storage for user plot items

        # axis options
        self.set_xaxis = QtGui.QPushButton("Re-plot!")
        self.draw_flashes = QtGui.QCheckBox()  # draw user products
        self.draw_flashes.setChecked(True)
        self.run_user_analysis = QtGui.QCheckBox()  # draw user products
        self.run_user_analysis.setChecked(True)

        self.lay_inputs.addWidget( QtGui.QLabel("Draw Flashes"), 1, 8 )
        self.lay_inputs.addWidget( self.draw_flashes, 1, 9 )
        self.lay_inputs.addWidget( self.set_xaxis, 0, 12 )

        # range selections
        self.time_range = pg.LinearRegionItem(values=[0,23.6], orientation=pg.LinearRegionItem.Vertical)
        self.wfplot.addItem( self.time_range )
        
        # array of pmt-maxima in time_range
        self.pmt_max = np.zeros(32)

        # PMT scatter points
        self.pmtdiagram   = ScatterPMT()#pg.ScatterPlotItem(pxMode=False)
        # Flash scatter points
        self.flashdiagram = pg.ScatterPlotItem(pxMode=False) 

        # diagram objects
        self.definePMTdiagram()

        # other options
        self.channellist = [] # when not None, only draw channels in this list

        # user analyses
        self.user_analysis_products = []
        self.user_analyses = []

        # connect
        self.set_xaxis.clicked.connect( self.plotData )
        self.next_event.clicked.connect( self.nextEvent )
        self.prev_event.clicked.connect( self.prevEvent )
        self.beam_window.clicked.connect( self.scaleToBeam )


    # --------------------------
    # scale event to beam window
    def scaleToBeam( self ):

        self.time_window.setTickWindow([0,1500])
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
            self.newevent = False
        
        scaledown = float( self.adc_scaledown.text() )

        # clear time-window display
        self.time_window.clear()
        
        # clear the pmt-maxima
        self.pmt_max = np.zeros(32)
        
        # BEAM SAMPLE WINDOW
        self.wfplot.clear()
        offset = 1.0
        if self.collapse.isChecked():
            offset = 0.0
            scaledown = 1.0
        
        # start plotting waveforms
        wfs = self.opdata.opdetwf.getData()

        # get OpHits
        #hits = self.opdata.ophits.getData()

        # what are the bounds that we want to plot in?
        bounds = self.time_window.time_range.getRegion() # usec
        print bounds
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
                pulse_end = pulse_start + len(pulse_ADCs)              # usec
                #print 'pulse region : [%i,%i]'%(pulse_start_tick,pulse_end_tick)
                #print 'adding wf to time-region [%i,%i]'%(pulse_start,pulse_end)
                #print 'wf : ',pulse_ADCs
                pmt_wf[ pulse_start_tick : pulse_end_tick ] = pulse_ADCs
                
                # if pulse is in the pmt-color range
                if ( ( (pulse_start) > pmt_bnds[0]) and ( (pulse_end) < pmt_bnds[1]) ):
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
            
            # plot the waveform in the cosmics window
            self.time_window.plot(x=TDCs, y=ADCs, pen=pencolor, name="PMT%d"%(ipmt))
            
            if ipmt in self.user_plot_item.keys():
                for useritem in self.user_plot_item[ipmt]:
                    self.wfplot.addItem( useritem )

        # set the range for the view
        self.wfplot.setXRange(bounds[0]*USPERTICK, bounds[1]*USPERTICK, update=True)

        # add the time-range
        self.wfplot.addItem( self.time_range )

        if (self.draw_flashes.isChecked() == True):
            # add all the flashes
            flashes = self.opdata.opflash.flashes
            for flash in flashes:
                
                time = flash[0]
                flashInfo = flashes[flash]
                PE = flashInfo[0]
                Ypos = flashInfo[1]
                Zpos = -(flashInfo[2]-(1036./2))
                if (PE > 10):
                    self.wfplot.addLine(time, movable=False, pen={'color':(255,255,0,255),'width':2})

        # do any additional drawing to the cosmics window
        self.time_window.plotCosmicWindows(event_time_range)        

        
        # pmt and flash positions
        self.pmtspot = []

        # first append PMTs with their appropriate color
        for ich in xrange(32):

            ipmt = ich
            #print 'max is : %.02f'%self.pmt_max[ich]
            col = self.pmtscale.colorMap().map( ( self.pmt_max[ich] ) /self.getPedestal(ipmt) )
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
                if (PE < 10) : continue
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
            ay.setLabel('PMT Ch',**yStyle)

    # ------------------------
    # PMT position mapping ---
    def definePMTdiagram(self):
        self.pmtspot = []
        for pid in getPMTIDList():
            pos = getPosFromID( pid )
            self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":30, 'pen':{'color':'w','width':2}, 'brush':(255,255,255,255), 'symbol':'o'} )
        for pid in getPaddleIDList():
            pos = getPosFromID( pid )
            self.pmtspot.append( {"pos":(pos[2],pos[1]), "size":25, 'pen':{'color':(0,0,255,1.0),'width':2}, 'brush':(255,255,255,255), 'symbol':'s'} )

        self.pmtdiagram.addPoints( self.pmtspot )
        self.pmt_map.addItem( self.pmtdiagram ) 
        self.pmtdiagram.sigClicked.connect( self.pmtDiagramClicked )
        self.pmtdiagram.scene().sigMouseMoved.connect(self.onMove)

        
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


    def getPedestal(self,pmt):
        return self.opdata.opdetwf.pedestals[pmt]


    # -------------------------------------------
    # function that decides what to do when mouse
    # hovers over a point in the PMT diagram
    def onMove(self, pos):

        act_pos = self.pmtdiagram.mapFromScene(pos)

        p1 = self.pmtdiagram.pointsAt(act_pos)
        
        #if (len(p1) != 0):
        #    print 'found %i SpotItems'%len(p1)
        #    print p1[0]
        #    print p1[0].brush
        #    print p1[0].data
