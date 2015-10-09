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
USPERTICK = 15.625/1000. # ns
NSPERFRAME = 1600000.0 # 1.6 ms in ns

class OpDetWfData( OpDataPlottable ):

    def __init__(self,producer='pmtreadout'):
        super(OpDetWfData, self).__init__()

        # get the producer name
        self.producer = producer
        
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
        self.samplesPerFrame = 25600
        self.nspertick = 15.625

        # event time-range
        self.event_time_range = [+4800., -1600] # usec

        # trigger time
        self.trigger_time = None
        
        # number of samples in entire waveform
        self.nsamples = self.samplesPerFrame*4
        # number of samples in beam-gate window
        self.beam_samples = 1000
        # number of PMT channels to use
        self.n_pmts = 32
        # fill pedestals w/ baseline
        self.resetChannels()

    # -----------------------------
    # define producer name
    def setProducer(self, producer):
        self.producer = producer

    # -----------------------------
    # reset waveforms
    def resetChannels(self):
        
        for pmt in xrange(self.n_pmts):
            self.opdetdigits[pmt] = {}
            self.pedestals[pmt] = 2048.
        return

    # ----------------------------------
    # get the data for the current event
    # return the dictionary of waveforms
    def getData( self, remake=False ):

        if remake==True:
            self.resetChannels()
        return self.opdetdigits

    # ---------------------------
    # get the pedestal vector
    def getPedestal(self):
        return self.pedestals

    def getSampleLength(self):
        return self.nsamples

    # ----------------------------
    # load the data for this event
    def getEvent( self, mgr, trig_time=None):

        self.trigger_time = trig_time

        # reset channels
        self.resetChannels()

        # load optical waveforms
        self.opdata = mgr.get_data(larlite.data.kOpDetWaveform,self.producer)

        # prepare the wf data
        self.fillWaveforms()

        return True

    def determineWaveformLengths( self ):
        df = self.wf_df['adcs'].apply( len )
        self.wf_df['nsamples'] = pd.Series( df, index=self.wf_df.index )

    def convertToFrameSample( self, timestamp, trig_timestamp  ):
        return int( (timestamp-trig_timestamp)*1000.0/NSPERTICK ) # timestamps in microseconds of course
                     
        
    # ------------------------
    # function to fill wf info
    def fillWaveforms( self ):

        # loop through all waveforms and add them to the wf dictionary
        # self.opdata contains the larlite::ev_opdetwaveform object
        for n in xrange(self.opdata.size()):
        
            wf = self.opdata.at(n)

            pmt = wf.ChannelNumber()

            adcs = np.array(wf)
            
            # only use first 48 pmts
            if ( pmt >= self.n_pmts ):
                continue

            # add the PMT wf to the dictionary of channels
            time = wf.TimeStamp() # in usec
            if (self.trigger_time == None):
                time -= 1600.
            else:
                time -= self.trigger_time
            # keep finding event time-boundaries
            if (time+len(adcs)*USPERTICK > self.event_time_range[1]):
                self.event_time_range[1] = time+len(adcs)*USPERTICK
            if (time < self.event_time_range[0]):
                self.event_time_range[0] = time

            time_tick = int(time*1000/NSPERTICK)
            #print 'wf time is : ',time
            self.opdetdigits[pmt][time] = adcs

        return


