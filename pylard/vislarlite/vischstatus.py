import os,sys
from larcv import larcv
from larlite import larlite
from pylard.pylardata.tpcdataplottable import TPCdataPlottable

class PyLArLiteVisChStatus:

    MAXWIRES     = 3456
    MAXTICKS = 6048
    STARTTICK    = 2400
    TICKOFFSET   = 2400
    NPLANES      = 3

    def __init__(self):
        pass

    def configure(self,pset):
        self.chstatus_producer = pset.get("chstatus_producer")
        self.wire_downsampling = int(pset.get("wire_downsampling"))
        self.time_downsampling = int(pset.get("time_downsampling"))

    def visualize( self, larlite_io, larcv_io, rawdigit_io ):

        event_chstatus = larlite_io.get_data( larlite.data.kChStatus, self.chstatus_producer )

        planes = []
        chstatus_imgs = larcv.EventImage2D()

        for p in range(0,PyLArLiteVisChStatus.NPLANES):
            plane_rawmeta = larcv.ImageMeta( PyLArLiteVisChStatus.MAXWIRES, PyLArLiteVisChStatus.MAXTICKS,
                                             PyLArLiteVisChStatus.MAXTICKS, PyLArLiteVisChStatus.MAXWIRES,
                                             0.0, PyLArLiteVisChStatus.STARTTICK+PyLArLiteVisChStatus.MAXTICKS, p )
            rawimg = larcv.Image2D( plane_rawmeta )
            rawimg.paint(0.0)

            meta = rawimg.meta()
            plane = meta.plane()
            planes.append(plane)

            chstatus = event_chstatus.at(p)
            
            status_v = chstatus.status()
            for ch in range(0,status_v.size()):
                status = status_v.at(ch)
                #print "w=",i," status=",status_v.at(i)," wcol=",wcol
                if status_v.at(ch) not in [4,5]:
                    if ch<0 or ch>=meta.cols():
                        print "Tried to fill a non-existent pixel column. wire=",ch," maxcols=",meta.cols()
                        continue
                    rawimg.paint_col( ch, 255.0 )

            # compress
            newrows = int(plane_rawmeta.rows()/self.time_downsampling)
            newcols = int(plane_rawmeta.cols()/self.wire_downsampling)
            if newrows!=plane_rawmeta.rows() or newcols!=plane_rawmeta.cols():
                print "Compressing image: newrows=",newrows," newcols=",newcols
                rawimg.compress( newrows, newcols )

            # append image
            chstatus_imgs.Append( rawimg )

        pytpcdata = TPCdataPlottable( "chstatus", chstatus_imgs.Image2DArray(), planes )
        return pytpcdata
