import os,sys
from pylard.vislarlite.larliteopdata import LArLiteOpticalData
from larlite import larlite
import numpy as np

class PyLArLiteDrawOpFlash:

    MAXNPMTS=32
    MAXNCHS=48
    NSPERTICK=15.625

    colorlist = {0:(255,0,0,128),
                 1:(0,255,0,128),
                 2:(0,0,255,128),
                 3:(128,128,0,128),
                 4:(128,0,128,128),
                 5:(0,128,128,128)}

    def __init__(self):
        pass

    def configure(self,pset):
        self.opflash_producer = pset.get("opflash_producer")
        self.ophit_producer   = pset.get("ophit_producer")
        self.assn_producer    = pset.get("assn_producer")
        self.trigger_producer = pset.get("trigger_producer")
        
    def visualize( self, larlite_io, larcv_io, rawdigit_io ):
        opflashs_v = larlite_io.get_data(larlite.data.kOpFlash, self.opflash_producer)
        ophit_v    = larlite_io.get_data(larlite.data.kOpHit,   self.ophit_producer)
        assn       = larlite_io.get_data(larlite.data.kAssociation, self.assn_producer)

        empty_assn = False
        if assn.association_keys().size()==0:
            empty_assn = True
        
        print "Number of opflashs: ",opflashs_v.size()
        
        pyopdata = LArLiteOpticalData()
        colorindex = 0
        for iopflash in xrange(0,opflashs_v.size()):
            opflash = opflashs_v.at(iopflash)

            if empty_assn:
                # if empty we create fake hits on all channels for this flash
                # we draw a box around the opflash
                box_x = np.zeros( 5 )
                box_y = np.zeros( 5 )
                box_x[0] = opflash.Time()-0.5*opflash.TimeWidth()
                box_x[1] = opflash.Time()-0.5*opflash.TimeWidth()
                box_x[2] = opflash.Time()+0.5*opflash.TimeWidth()
                box_x[3] = opflash.Time()+0.5*opflash.TimeWidth()
                box_x[4] = opflash.Time()-0.5*opflash.TimeWidth()

                box_y[0] = 0
                box_y[1] = 100.0
                box_y[2] = 100.0
                box_y[3] = 0
                box_y[4] = 0

                box_x[:] *= 1000.0 # us to ns

                slot = 5
                for ch in range(0,PyLArLiteDrawOpFlash.MAXNPMTS):
                    pyopdata.makeUserWindow( box_y, opflash.Time(), 
                                             slot, ch, 
                                             default_color=PyLArLiteDrawOpFlash.colorlist[colorindex], 
                                             timepertick=PyLArLiteDrawOpFlash.NSPERTICK, x=box_x )
                print "opflash. ",opflash.Time()

        #assn.list_association()

        return pyopdata
        
