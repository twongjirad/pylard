import os,sys
from pylard.vislarlite.larliteopdata import LArLiteOpticalData
from larlite import larlite
import numpy as np

class PyLArLiteDrawOpHits:

    MAXNPMTS=48
    NSPERTICK=15.625

    def __init__(self):
        pass

    def configure(self,pset):
        self.ophit_producer   = pset.get("ophit_producer")
        self.trigger_producer = pset.get("trigger_producer")
        
    def visualize( self, larlite_io, larcv_io, rawdigit_io ):
        ophits_v  = larlite_io.get_data(larlite.data.kOpHit, self.ophit_producer)
        trigger   = larlite_io.get_data(larlite.data.kTrigger, self.trigger_producer)

        ntrig = trigger.TriggerNumber()
        ttrig = trigger.TriggerTime()
        tbeam = trigger.BeamGateTime()

        print "Trigger: ",ntrig,ttrig,tbeam,ttrig-tbeam
        print "Number of ophits: ",ophits_v.size()
        
        pyopdata = LArLiteOpticalData()
        
        for iophit in xrange(0,ophits_v.size()):
            ophit = ophits_v.at(iophit)
            # we draw a box around the ophit
            box_x = np.zeros( 5 )
            box_y = np.zeros( 5 )
            box_x[0] = ophit.PeakTime()-0.5*ophit.Width()
            box_x[1] = ophit.PeakTime()-0.5*ophit.Width()
            box_x[2] = ophit.PeakTime()+0.5*ophit.Width()
            box_x[3] = ophit.PeakTime()+0.5*ophit.Width()
            box_x[4] = ophit.PeakTime()-0.5*ophit.Width()

            box_y[0] = 0
            box_y[1] = ophit.Amplitude()
            box_y[2] = ophit.Amplitude()
            box_y[3] = 0
            box_y[4] = 0
            
            box_x[:] *= 1000.0 # usec to ns
            
            ch = ophit.OpChannel()%100
            slot = 5 + ophit.OpChannel()/100
            pyopdata.makeUserWindow( box_y, ophit.PeakTime(), 
                                     slot, ch,
                                     default_color=(255,0,0,125), timepertick=PyLArLiteDrawOpHits.NSPERTICK, x=box_x )
            #print "ophit: ch=",ophit.OpChannel()," t=",ophit.PeakTime(),ophit.PeakTimeAbs(),ophit.PeakTime()-ophit.PeakTimeAbs(),ophit.Width()

        return pyopdata
        
