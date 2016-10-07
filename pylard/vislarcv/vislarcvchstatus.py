import os,sys
from larcv import larcv
from pylard.pylardata.tpcdataplottable import TPCdataPlottable

class PyLArCVVisChStatus:

    def __init__(self):
        pass

    def configure(self,pset):
        self.tpc_img_producer  = pset.get("tpc_img_producer")
        self.chstatus_producer = pset.get("chstatus_producer")

    def visualize( self, larlite_io, larcv_io, rawdigit_io ):
        event_imgs     = larcv_io.get_data( larcv.kProductImage2D,  self.tpc_img_producer )
        event_chstatus = larcv_io.get_data( larcv.kProductChStatus, self.chstatus_producer )

        planes = []
        chstatus_imgs = larcv.EventImage2D()
        # we make some chstatus images
        badgoodimgs = [] # simple bad/good images
        #bytypes  = []
        for iimg in range(0,event_imgs.Image2DArray().size()):
            img = event_imgs.Image2DArray().at(iimg)
            meta = img.meta()
            plane = meta.plane()
            planes.append(plane)

            # bad good image
            chimg = larcv.Image2D( meta )
            chimg.paint(0.0)
            plane_bytypes = [ larcv.Image2D(meta) for x in range(0,6) ]
            for itype in plane_bytypes:
                itype.paint(0.0)

            chstatus = event_chstatus.Status(plane)
            
            wire_pixel_width = int( meta.pixel_width()+0.1 )
            status_v = chstatus.as_vector()
            for i in range(0,status_v.size()):
                wcol = i/wire_pixel_width
                #print "w=",i," status=",status_v.at(i)," wcol=",wcol
                if status_v.at(i) not in [4,5]:
                    if wcol<0 or wcol>=meta.cols():
                        print "Tried to fill a non-existent pixel column. wire=",i," col=",wcol << " maxcols=",meta.cols()
                        continue
                    chimg.paint_col( wcol, 255.0 )
            chstatus_imgs.Append( chimg )

        pytpcdata = TPCdataPlottable( "chstatus", chstatus_imgs.Image2DArray(), planes )
        return pytpcdata
