from pylard.pylardata.opdataplottable import OpDataPlottable
import numpy as np
import ROOT
from ROOT import larlite
import time

class OpFlashData():

    def __init__(self,producer='opflash'):

        # get the producer name
        self.producer = producer

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
    def getEvent(self, mgr, trig_time=None):

        self.flashes = {}

        # load optical hits
        self.opflashdata = mgr.get_data(larlite.data.kOpFlash,
                                        self.producer)

        # load each flash
        try:
            print 'found %i flashes'%self.opflashdata.size()

            for n in xrange(self.opflashdata.size()):

                flash = self.opflashdata.at(n)

                # flash time
                time = flash.Time()
                abstime = flash.AbsTime()
                frame = flash.Frame()
                dt   = flash.TimeWidth()
                PE   = flash.TotalPE()
                Ypos = flash.YCenter()
                Zpos = flash.ZCenter()
                #print '\t[Time, dt, Frame]  : [%.02f, %.02f, %.02f]'%(time,dt,frame)
                #print '\t[PE, Ypos, Zpos] : [%.02f, %.02f, %.02f]'%(PE,Ypos,Zpos)
                #print
                #if (PE < 20): continue
                self.flashes[ (time, time+dt) ] = [ PE, Ypos, Zpos ]
        except:
            print 'could not load flashes'
