from pylard.pylardata.opdataplottable import OpDataPlottable
import numpy as np
import ROOT
from ROOT import larlite
import time

class TriggerData():

    def __init__(self,producer='daq'):

        # get the producer name
        self.producer = producer

        # trigger data
        self.triggedata = None
        
        # larlite OpHit stored here:
        self.trigger_time = None
        
        # trigger time-stamp
        self.trig_time = None


    #---------------------
    # define producer name
    def setProducer(self,producer):
        self.producer = producer
        
        
    # -------------------------
    # return trigger time
    def getTrigTime(self):
        
        return self.trigger_time

    #---------------------------
    # get data for current event
    def getEvent(self, mgr):

        # load trigger data
        self.triggerdata = mgr.get_data(larlite.data.kTrigger,self.producer)
        self.trigger_time = self.triggerdata.TriggerTime();
        if self.trigger_time>1e300:
            print "larby's"
            self.trigger_time = 3200.0
