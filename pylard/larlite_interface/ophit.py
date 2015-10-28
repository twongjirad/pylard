from pylard.pylardata.opdataplottable import OpDataPlottable
import numpy as np
import ROOT
from ROOT import larlite
import time

class OpHitData():

    def __init__(self,producer='opflash'):

        # get the producer name
        self.producer = producer
        
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

    # -------------------------
    # return data
    def getData(self, remake=False):

        # if we are to clear the event
        if remake == True:
            return self.initialize_hits()
        # otherwise save the current hits
        return self.hits

    #---------------------------
    # get data for current event
    def getEvent(self, mgr):

        # load optical hits
        self.ophitdata = mgr.get_data(larlite.data.kOpHit,
                                      self.producer)
        
        # load each hit
        try:
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
                # print 'found hit for PMT %i : '%hit_chan,hit_info

                self.hits[hit_chan].append( hit_info)
        except:
            pass
