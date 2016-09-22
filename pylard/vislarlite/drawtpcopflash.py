import os,sys
from larlite import larlite
import pyqtgraph as pg
import numpy as np

class PyLArLiteDrawTPCOpFlash:

    USPERTICK=0.5

    colorlist = {0:(255,0,0,128),
                 1:(0,255,0,128),
                 2:(0,0,255,128),
                 3:(128,128,0,128),
                 4:(128,0,128,128),
                 5:(0,128,128,128)}

    def __init__(self):
        pass

    def configure(self,pset):
        self.opflash_producers = pset.get("opflash_producers")
        self.trigger_tick      = float(pset.get("trigger_tick"))
        self.min_tick          = float(pset.get("min_tick",2400))
        self.max_tick          = float(pset.get("max_tick",2400+6048))
        
    def visualize( self, larlite_io, larcv_io, rawdigit_io ):

        flash_plots = []
        colorindex = 0


        if type(self.opflash_producers) is str:
            s = self.opflash_producers
            s = s[s.find("[")+1:]
            s = s[:s.find("]")]
            print s
            slist = s.split(",")
            self.opflash_producers = []
            for p in slist:
                p = p.replace("\"","").strip()
                self.opflash_producers.append(p)

        print "flash producers: ",type(self.opflash_producers)
        
        for producer in self.opflash_producers:

            if type(producer) is not str:
                continue

            print "processing flashes from ",producer
            opflashs_v = larlite_io.get_data(larlite.data.kOpFlash, producer )
        
            for iopflash in xrange(0,opflashs_v.size()):
                opflash = opflashs_v.at(iopflash)
                x = np.zeros(2) # wires
                y = np.zeros(2) # time
                tick = self.trigger_tick + opflash.Time()/PyLArLiteDrawTPCOpFlash.USPERTICK # in ticks
                if tick<self.min_tick or tick>self.max_tick:
                    continue
                y[:] = tick
                
                #x[0] = opflash.ZCenter()/0.3 + -0.5*opflash.ZWidth()
                #x[1] = opflash.ZCenter()/0.3 +  0.5*opflash.ZWidth()
                x[0] = 0
                x[1] = 3456.0

                flashbar = pg.PlotDataItem( x=x, y=y, pen=(255,255,255,100) )
                flash_plots.append(flashbar)

                print "tpc opflash: t=",opflash.Time()," tick=",y[0]," z=",opflash.ZCenter()," dz=",opflash.ZWidth()

                colorindex += 1
                if colorindex>=len(PyLArLiteDrawTPCOpFlash.colorlist):
                    colorindex = 0

        print "total opflashes: ",len(flash_plots)

        return flash_plots
        
