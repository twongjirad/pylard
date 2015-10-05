from pylard.pylardata.opdataplottable import OpDataPlottable
import numpy as np
import ROOT
from ROOT import larlite
import time

class OpFlashData( OpDataPlottable ):

    def __init__(self,inputfiles):
        super(OpFlashData, self).__init__()

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
        self.opflashdata = None

        # keep track of flashes
        # flashes saved in per time-range dictionary
        self.flashes = {}


    #---------------------
    # define producer name
    def setProducer(self,producer):
        self.producer = producer


    # -------------------------
    # return data
    def getData(self, remake=False):
        # if we are to clear the event
        if remake == True:
            self.flashes = {}
            return self.flashes
        # otherwise save the current hits
        return self.flashes


    #---------------------------
    # get data for current event
    def getEvent(self, eventid):

        self.flashes = {}

        # move to the specified event
        self.manager.go_to(eventid)
        
        # load optical hits
        self.opflashdata = self.manager.get_data(larlite.data.kOpFlash,
                                                 self.producer)

        # load each hit
        for n in xrange(self.opflashdata.size()):

            flash = self.opflashdata.at(n)

            # flash time
            time = flash.Time()+1600.
            abstime = flash.AbsTime()
            frame = flash.Frame()
            dt   = flash.TimeWidth()
            PE   = flash.TotalPE()
            Ypos = flash.YCenter()
            Zpos = flash.ZCenter()
            #print '\t[Time, Abs Time, Frame]  : [%.02f, %.02f, %.02f]'%(time,abstime,frame)
            #print '\t[PE, Ypos, Zpos] : [%.02f, %.02f, %.02f]'%(PE,Ypos,Zpos)
            #print
            
            self.flashes[ (time, time+dt) ] = [ PE, Ypos, Zpos ]
