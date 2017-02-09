import os,sys
import ROOT
from larcv import larcv
from ROOT import std
from pylard.pylardata.tpcdataplottable import TPCdataPlottable

class DrawTPCRawDigits:
    def __init__(self):
        pass
    def configure(self,pset):
        self.timedownsample = pset.get("TimeDownsamplingFactor",6.0)
        self.wiredownsample = pset.get("WireDownsamplingFactor",1.0)

    def visualize(self,larlite_io,larcv_io,rawdigit_io):
        adcs = rawdigit_io.get_tpcdata()
        img_v = std.vector("larcv::Image2D")()
        planes = []
        pedestals = {0:2045.0,1:2045.0,2:460.0}
        for p in range(0,3):
            meta = larcv.ImageMeta( 3456.0, 9600.0, int(9600/self.timedownsample), int(3456/self.wiredownsample), 0, 9600.0, p )
            img = larcv.Image2D( meta )
            img.paint(0.0)
            adc_vals = adcs[p]
            for ch,adc in adc_vals.items():
                col = int(ch/self.wiredownsample)
                
                larcv.fill_img_col( img, adc, col, int(self.timedownsample), pedestals[p] )
                #print ch,col,adc.size(),adc.at(0)
            img_v.push_back( img )
            planes.append(p)

        print planes
        pytpcdata = TPCdataPlottable( "tpc", img_v, planes )
            
        return pytpcdata
