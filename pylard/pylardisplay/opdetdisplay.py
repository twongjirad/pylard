import os,sys,copy
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from collections import OrderedDict

from pylard.config.pmt_chmap import getPMTID, getChannel, getPMTIDList, getPaddleIDList
from pylard.config.pmtpos import getPosFromID 
from pylard.pylardisplay.cosmicdiscdisplay import CosmicDiscDisplay

NSPERTICK = 15.625

class OpDetDisplay(QtGui.QWidget) :
    def __init__(self, opdata):
        super(OpDetDisplay,self).__init__()
        self.opdata = opdata

        # Plots
        self.graphics = pg.GraphicsLayoutWidget()
        self.plot = pg.PlotItem(name='Plot1')
        self.diagram = pg.PlotItem(name="plot2")
        self.pmtscale =  pg.GradientEditorItem(orientation='bottom')
        self.lastevent = None
        self.newevent = True

        # main layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget( self.graphics, 0, 0 )
        self.graphics.addItem( self.diagram, 0, 0 )
        self.graphics.addItem( self.pmtscale, 1, 0 )
        self.graphics.addItem( self.plot, 2, 0 )
        self.lay_inputs = QtGui.QGridLayout()
        self.layout.addLayout( self.lay_inputs, 1, 0 )
        
        # inputs layout
        # widgets
        
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

        self.lay_inputs.addWidget( self.openCosmicWindow, 1, 0, 1, 2 )
        self.lay_inputs.addWidget( self.draw_cosmics, 1, 9 )
        self.lay_inputs.addWidget( self.draw_user_items, 1, 10 )
        self.lay_inputs.addWidget( self.run_user_analysis, 1, 11 )
        self.lay_inputs.addWidget( self.set_xaxis, 1, 12 )

        # range selections
        self.time_range = pg.LinearRegionItem(values=[50,150], orientation=pg.LinearRegionItem.Vertical)
        self.plot.addItem( self.time_range )

        # diagram objects
        self.definePMTdiagram()

        # other options
        self.channellist = [] # when not None, only draw channels in this list
        self.pedfunction = self.getpedestal

        # user analyses
        self.user_analysis_products = []
        self.user_analyses = []

        # cosmic display subwindow
        self.cosmicdisplay = CosmicDiscDisplay(self)

        # connect
        self.set_xaxis.clicked.connect( self.plotData )
        self.next_event.clicked.connect( self.nextEvent )
        self.prev_event.clicked.connect( self.prevEvent )
        self.openCosmicWindow.clicked.connect( self.showCosmicDisplay )
        
    def plotData( self ):

        evt = int(self.event.text())
        slot = int(self.slot.text())
        if self.lastevent is None or evt!=self.lastevent:
            self.opdata.getEvent( evt, slot=slot )
            self.lastevent = evt
            self.newevent = True
        else:
            #print "old event: ",self.lastevent
            self.newevent = False
        
        scaledown = float( self.adc_scaledown.text() )
        
        # --------------------------------------------------
        # BEAM SAMPLE WINDOW
        self.plot.clear()
        offset = 1.0
        if self.collapse.isChecked():
            offset = 0.0
            scaledown = 1.0
        
        nbins = self.opdata.getData( slot=int(self.slot.text() ) ).shape[0]
        x = np.linspace( 0, nbins*NSPERTICK, num=nbins )
        for ipmt in xrange(0,self.opdata.getData( slot=int(self.slot.text() ) ).shape[1]):

            if len(self.channellist)>0 and ipmt not in self.channellist and not self.draw_all.isChecked():
                continue
            
            pencolor = self.getChanColor( ipmt )
            if self.last_clicked_channel is not None and ipmt==self.last_clicked_channel:
                pencolor = (0, 255, 255 )

            wfm = self.opdata.getData( slot=int(self.slot.text() ) )[:,ipmt]
            y = (wfm-self.pedfunction(wfm,ipmt))/scaledown+ipmt*offset

            self.plot.plot(x=x, y=y, pen=pencolor, name="PMT%d"%(ipmt))

            if ipmt in self.user_plot_item.keys():
                for useritem in self.user_plot_item[ipmt]:
                    self.plot.addItem( useritem )

        self.plot.setXRange(0,nbins*NSPERTICK,update=True)
        self.plot.addItem( self.time_range )

        if "cosmics" in dir(self.opdata):
            if self.newevent:
                # refresh the cosmic window display
                self.cosmicdisplay.plotCosmicWindows( self.opdata.cosmics )
            if self.draw_cosmics.isChecked():
                # overlay the cosmic waveforms
                self.cosmicdisplay.applyCosmicDiscRange( clearplot=False )
                    
                

        # ----------------------------------------------------
        # diagram object
        bnds = self.time_range.getRegion()
        istart = int( bnds[0]/NSPERTICK )
        iend = int( bnds[1]/NSPERTICK )
        if istart>iend:
            tmp = istart
            istart = iend
            iend = tmp

        self.pmtspot = []

        for ich in xrange(self.opdata.getData( slot=int(self.slot.text() ) ).shape[1],-1,-1):
            if ich>=36:
                continue
            wfm =  self.opdata.getData( slot=int(self.slot.text() ) )[istart:iend,ich]
            maxamp = np.max( wfm )-self.pedfunction(wfm,ich)
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

        # axis!
        ax = self.plot.getAxis('bottom')
        ax.setHeight(30)
        xStyle = {'color':'#FFFFFF','font-size':'14pt'}
        #ax.setLabel('64 MHz Sample Tick',**xStyle)
        ax.setLabel('ns from readout start',**xStyle)
        ay = self.plot.getAxis('left')
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
        self.pmtdiagram.sigClicked.connect( self.pmtDiagramClicked )

        
    def nextEvent(self):
        evt = int(self.event.text())
        slot = int(self.slot.text())

        ok = self.opdata.getEvent( evt+1, slot=slot )
        if ok:
            self.event.setText("%d"%(evt+1))
        else:
            print "Next event not ok"
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
            
    def getWaveformPlot(self):
        return self.plot
    
    def getPMTdiagram(self):
        return self.diagram
            
    def gotoEvent( self, event, slot=None ):
        evt = int(self.event.text())
        if slot is None:
            slot = int(self.slot.text())
        else:
            self.slot.setText("%d"%(slot))
        
        try:
            more = self.opdata.getEvent( event, slot=slot )
            self.event.setText( "%d"%(event) )
        except:
            more = self.opdata.getEvent( evt, slot=slot )
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
        #print "ped: ",self.opdata.getPedestal( slot=slot )
        #raw_input()
        if femch is not None:
            return self.opdata.getPedestal( slot=slot )[femch]
        else:
            return self.opdata.getPedestal( slot=slot )

    def setPedestalFunction( self, pedfunc ):
        self.pedfunction = pedfunc

    def addUserAnalysis( self, user_analysis ):
        self.user_analyses.append( user_analysis )

    def clearUserAnalyses( self ):
        self.user_analyses = []
        self.user_analysis_chproducts = {}
        
    def showCosmicDisplay( self ):
        self.cosmicdisplay.show()
                
