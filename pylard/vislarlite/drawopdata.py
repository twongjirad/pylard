import os,sys
from pylard.vislarlite.larliteopdata import LArLiteOpticalData
from larlite import larlite
import numpy as np


class PyLArLiteDrawOpdata:

    MAXNPMTS=48
    NSPERTICK=15.625

    def __init__(self):
        print "PyLArLiteDrawOpdata init"
    def configure(self,pset):
        self.opdata_producer = pset.get("opdata_producer")
        self.trigger_producer = pset.get("trigger_producer")
        
        
    def visualize( self, larlite_io, larcv_io ):
        """ fill larliteopdata object. its a concrete instance of opdataplottable """
        print "Visualize PyLArLiteDrawOpdata"
        print " larlite_io: ",larlite_io
        print " larcv_io: ",larcv_io

        pyopdata = LArLiteOpticalData()
        
        # get trigger information
        self.triggerdata = larlite_io.get_data(larlite.data.kTrigger,self.trigger_producer)
        self.trigger_time = self.triggerdata.TriggerTime()
        if self.trigger_time>1e300:
            #print "larby's"
            self.trigger_time = 3200.0

        # fill waveforms
        nloops = 0
        lastpmt = -1

        # load optical waveforms
        self.opdata = larlite_io.get_data(larlite.data.kOpDetWaveform,self.opdata_producer)
        
        # if we did not succeed:
        if not self.opdata:
            print 'could not find kOpDetWaveform w/ producer name %s'%opwf_producer
            return

        # loop through all waveforms and add them to beam and cosmic containers
        # self.opdata contains the larlite::ev_opdetwaveform object
        for n in xrange(self.opdata.size()):
        
            wf = self.opdata.at(n)
            pmt = wf.ChannelNumber()
            slot = 5 + pmt/100
            pmt = pmt%100

            # only use first 48 pmts (HG SLOT)
            if ( pmt >= PyLArLiteDrawOpdata.MAXNPMTS ):
                continue

            # adcs
            adcs = []
            for i in xrange(wf.size()):
                adcs.append(wf.at(i))
            adcs = np.array(adcs)

            # set relative time
            time = wf.TimeStamp() # in usec
            if (self.trigger_time == None):
                time -= 3200. #?
            else:
                time -= self.trigger_time
            
            if len(adcs)>=500: # is there another way to tag beam windows?
                print "beam window: ch=",pmt," slot=",slot," len=",len(adcs)," timestamp=",time,"(rel) ",time+self.trigger_time," (raw)"," ticks=",time/0.015625
                pyopdata.beamwindows.makeWindow( adcs, time*1000.0, slot, pmt, timepertick=PyLArLiteDrawOpdata.NSPERTICK )
            else:
                #print "cosmic window: ch=",pmt," slot=",slot," len=",len(adcs)," timestamp=",time," ticks=",time/0.015625
                pyopdata.cosmicwindows.makeWindow( adcs, time*1000.0, slot, pmt, timepertick=PyLArLiteDrawOpdata.NSPERTICK )



        
        

        
        
        
