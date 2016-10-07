import os,sys
from larcv import larcv
from pylard.pylardata.tpcdataplottable import TPCdataPlottable

class DrawImage2D:

    def __init__(self):
        pass

    def configure(self,pset):
        self.timedownsample = pset.get("TimeDownsamplingFactor",1.0)
        self.wiredownsample = pset.get("WireDownsamplingFactor",1.0)
        self.image_producer = pset.get("image2d_producer")
        self.dump           = pset.get("dump",False)

    def visualize( self, larlite_io, larcv_io, rawdigit_io ):
        
        event_images = larcv_io.get_data( larcv.kProductImage2D, self.image_producer )
        planes = []
        for img in event_images.Image2DArray():
            planes.append( img.meta().plane() )
            if self.dump:
                arr = larcv.as_ndarray( img )
                print arr
        pytpcdata = TPCdataPlottable( self.image_producer, event_images.Image2DArray(), planes )
        return pytpcdata
