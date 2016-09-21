import os,sys
from larlite import larlite
from larcv import larcv
import numpy as np
from pylard.pylardata.tpcdataplottable import TPCdataPlottable

class PyLArLiteDrawImage2D:

    MAXWIRES     = 3456
    MAXTIMETICKS = 6400
    STARTTICK    = 2400
    NPLANES      = 3

    def __init__(self):
        pass

    def configure(self,pset):
        self.wire_producer     = pset.get("wire_producer")
        self.trigger_producer  = pset.get("trigger_producer")
        self.wire_downsampling = pset.get("wire_downsampling")
        self.time_downsampling = pset.get("time_downsampling")
        self.maxwires          = pset.get("max_wires",PyLArLiteDrawImage2D.MAXWIRES)
        self.maxticks          = pset.get("max_ticks",PyLArLiteDrawImage2D.MAXTIMETICKS)
        self.start_tick        = pset.get("start_tick",PyLArLiteDrawImage2D.STARTTICK)
        

    def visualize( self, larlite_io, larcv_io, rawdigit_io ):
        
        triggerdata = larlite_io.get_data(larlite.data.kTrigger,self.trigger_producer)
        wiredata    = larlite_io.get_data(larlite.data.kWire,   self.wire_producer)

        for p in range(PyLArLiteDrawImage2D.NPLANES):
            plane_rawmeta = larcv.ImageMeta( self.maxwires, self.maxticks,
                                             self.maxticks, self.maxwires,
                                             0.0, self.start_tick, p )
            rawimg = larcv.Image2D( plane_rawmeta )
            rawimg.paint(0.0)

        for wire in wiredata:
            pass
            
            
