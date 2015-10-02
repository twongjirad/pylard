from pylard.pylardata.opdataplottable import OpDataPlottable
import numpy as np
import ROOT
from ROOT import larlite
import time

class OpHitData( OpDataPlottable ):

    def __init__(self,inputfiles):
        super(OpHitData, self).__init__()

        # set input file name
        self.files = inputfiles
        
        # get the producer name
        self.producer = 'opflash'
        
        # call larlite manager
        self.manager = larlite.storage_manager()
        self.manager.reset()
        for f in self.files:
            self.manager.add_in_filename(f)
        self.manager.set_io_mode(larlite.storage_manager.kREAD)
        self.manager.open()
        
        # allow only the 32 "regular" PMTs
        self.pmt_max = 31
        
        # larlite OpHit stored here:
        self.ophitdata = None
        
        # keep track of hits
        # hits saved in per-pmt dictionary
        self.hits = {}
        # create an empty vector in which to store wfs for each PMT
        self.initialize_hits()


    #---------------------
    # define producer name
    def setProducer(self,producer):
        self.producer = producer
        
        
    # -----------------------
    # initialize PMT hits
    def initialize_hits(self):
        
        for x in xrange(self.pmt_max+1):
            self.hits[x] = []

        return

    #---------------------------
    # get data for current event
    def getEvent(self, eventid):

        # move to the specified event
        self.manager.go_to(eventid)
        
        # load optical hits
        self.ophitdata = self.manager.get_data(larlite.data.kOpHit,
                                               self.producer)

        # load each hit
        for n in xrange(self.ophitdata.size()):

            hit = self.ophitdata.at(n)

            # get PMT channel
            hit_chan  = hit.OpChannel()
            if (hit_chan > self.pmt_max):
                continue

            # hit stored as [ (t_start, t_end) , amp ]
            hit_start = hit.PeakTime()-hit.Width()
            hit_end   = hit.PeakTime()+hit.Width()
            hit_amp   = hit.Amplitude()
            hit_info  = [ (hit_start,hit_end) , hit_amp ]
            print 'found hit for PMT %i : '%hit_chan,hit_info

            self.hits[hit_chan].append( hit_info)
            
            
