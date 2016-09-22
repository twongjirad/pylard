import os,sys,time
from larlite import larlite
from larcv import larcv
import numpy as np
from pylard.pylardata.tpcdataplottable import TPCdataPlottable

class PyLArLiteDrawImage2D:

    MAXWIRES     = 3456
    MAXTIMETICKS = 6048
    STARTTICK    = 2400
    TICKOFFSET   = 2400
    NPLANES      = 3

    def __init__(self):
        self.supera_algo = larlite.SuperaWireAlgo()

    def configure(self,pset):
        self.wire_producer     = pset.get("wire_producer")
        #self.trigger_producer  = pset.get("trigger_producer")
        self.wire_downsampling = int(pset.get("wire_downsampling"))
        self.time_downsampling = int(pset.get("time_downsampling"))
        self.maxwires          = int(pset.get("max_wires",PyLArLiteDrawImage2D.MAXWIRES))
        self.maxticks          = int(pset.get("max_ticks",PyLArLiteDrawImage2D.MAXTIMETICKS))
        self.start_tick        = int(pset.get("start_tick",PyLArLiteDrawImage2D.STARTTICK))
        self.tick_offset       = int(pset.get("start_tick",PyLArLiteDrawImage2D.TICKOFFSET))
        self.verbosity         = int(pset.get("Verbosity",2))
        self.supera_algo.setVerbosity( self.verbosity )
        

    def visualize( self, larlite_io, larcv_io, rawdigit_io ):
        
        #triggerdata = larlite_io.get_data(larlite.data.kTrigger,self.trigger_producer)
        wiredata    = larlite_io.get_data(larlite.data.kWire,   self.wire_producer)
        print "wire objects: ",wiredata.size()

        event_img = larcv.EventImage2D()
        event_roi = larcv.EventROI()
        
        planes = []
        start = time.time()
        for p in range(PyLArLiteDrawImage2D.NPLANES):
            plane_rawmeta = larcv.ImageMeta( self.maxwires, self.maxticks,
                                             self.maxticks, self.maxwires,
                                             0.0, self.start_tick+self.maxticks, p )
            rawimg = larcv.Image2D( plane_rawmeta )
            rawimg.paint(0.0)

            print "fill image with supera"
            self.supera_algo.fillImage( rawimg, wiredata, self.tick_offset )

            newrows = int(plane_rawmeta.rows()/self.time_downsampling)
            newcols = int(plane_rawmeta.cols()/self.wire_downsampling)
            print "Compressing image: newrows=",newrows," newcols=",newcols
            rawimg.compress( newrows, newcols )

            print "copy to container"
            event_img.Append( rawimg ) # a copy. bleh
            planes.append(p)
        print "wire -> Image2D time: ",time.time()-start,"secs"

        pytpcdata = TPCdataPlottable( self.wire_producer, event_img.Image2DArray(), event_roi.ROIArray(), planes )
        return pytpcdata
            
            

            
            
