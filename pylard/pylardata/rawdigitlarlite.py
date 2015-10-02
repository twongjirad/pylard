from pylard.pylardata.opdataplottable import OpDataPlottable
import pylard.pylardata.pedestal as ped
import pylard.pylardata.cosmicdisc as cd
import numpy as np
import pandas as pd
from root_numpy import root2array, root2rec, tree2rec, array2root
import ROOT
from ROOT import larlite
import time

NCHAN = 48
NSPERTICK = 15.625 # ns
NSPERFRAME = 1600000.0 # 1.6 ms in ns

class RawDigitsOpData( OpDataPlottable ):

    def __init__(self,inputfiles):
        super(RawDigitsOpData, self).__init__()

        # set input file name
        self.files = inputfiles

        # get the producer name
        self.producer = 'pmt_xmit'
        
        # set the slot number to use
        self.slot = 5

        # call larlite manager
        self.manager = larlite.storage_manager()
        self.manager.reset()
        for f in self.files:
            self.manager.add_in_filename(f)
        self.manager.set_io_mode(larlite.storage_manager.kREAD)
        self.manager.open()

        # wf and pedestal holder
        self.opdetdigits = {}
        self.pedestals   = {} 

        # cosmics window holder
        self.cosmics = cd.CosmicDiscVector()

        # event location
        self.first_event = 0
        self.event_range = [ self.first_event, self.first_event+100 ]
        self.entry_points = {}
        self.entry_points[ self.first_event ] = 0
        self.maxevent = None
        self.samplesPerFrame = 102400
        self.nspertick = 15.625
        
        # number of samples per beam-gate window
        self.nsamples = 1000
        # number of PMT channels to use
        self.n_pmts = 48
        # fill pedestals w/ baseline
        self.pedestals[self.slot] = np.ones( self.n_pmts ) *2048.

    # --------------------
    # define producer name
    def setProducer(self,producer):
        self.producer = producer

    def getData( self, slot=5, remake=False ):
        if slot not in self.opdetdigits or remake==True:
            print "Allocating array for slot ",slot," with length: ",self.getNBeamWinSamples()
            self.opdetdigits[slot] = np.ones( ( self.nsamples , self.n_pmts ) )*2048.0
        return self.opdetdigits[slot]

    def getPedestal(self,slot=5):
        if slot not in self.pedestals:
            self.pedestals[slot] = np.ones( self.n_pmts )*2048.0
        return self.pedestals[slot]

    def getSampleLength(self):
        return self.nsamples

    def getEvent( self, eventid, slot=5 ):

        # move to next event
        #self.manager.next_event()
        self.manager.go_to(eventid)
        
        # load optical waveforms
        print 'producer name is:%s'%self.producer
        self.opdata = self.manager.get_data(larlite.data.kFIFO,self.producer)

        # prepare the cosmics data
        self.fillCosmicsData()

        # store the beam windows into the numpy array expected by the parent class
        self.fillBeamWindow()

        return True

    def determineWaveformLengths( self ):
        df = self.wf_df['adcs'].apply( len )
        self.wf_df['nsamples'] = pd.Series( df, index=self.wf_df.index )

    def convertToFrameSample( self, timestamp, trig_timestamp  ):
        return int( (timestamp-trig_timestamp)*1000.0/NSPERTICK ) # timestamps in microseconds of course
                                                  
    def fillBeamWindow( self ):

        # Fill the beam sample array
        wf_v = np.ones( (self.nsamples, self.n_pmts ) )*2048.

        # self.opdata contains the larlite::ev_opdetwaveform object
        for n in xrange(self.opdata.size()):

            wf = self.opdata.at(n)
            
            # only select the slot we are interested in
            if (wf.module_address() != self.slot):
                continue

            # only select beam-gate windows
            if (wf.size() != self.nsamples):
                continue

            pmt = wf.channel_number()
            
            # only use first 48 pmts
            if ( pmt >= self.n_pmts ):
                continue

            adcs = np.array(wf)[:self.nsamples]
            #print adcs
            wf_v[:self.nsamples,pmt] = adcs

        self.opdetdigits[self.slot] = wf_v
            
        return


    def fillCosmicsData(self):
        
        self.cosmics = cd.CosmicDiscVector()

        # self.opdata contains the larlite::ev_opdetwaveform object
        for n in xrange(self.opdata.size()):

            wf = self.opdata.at(n)
            
            # only select the slot we are interested in
            if (wf.module_address() != self.slot):
                continue

            # only select cosmic windows
            if (wf.size() >= self.nsamples):
                continue

            pmt = wf.channel_number()
            
            # only use first 48 pmts
            if ( pmt >= self.n_pmts ):
                continue
                
            # we have a good window -> save it!
            adcs = np.array(wf)#-self.pedestals[self.slot][pmt]
            femslot = wf.module_address()
            frame_raw = wf.readout_sample_number_RAW()
            #frame_usec = self.convertToFrameSample( frame_raw )
            #print 'ch : %02i \t time: %06i \t wf : '%(pmt,frame_raw),adcs
            cosmics_window = cd.CosmicDiscWindow( adcs , femslot , pmt , frame_raw )
            self.cosmics.addWindow( cosmics_window )

        return
