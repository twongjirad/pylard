import numpy as np
import ROOT as rt
from root_numpy import root2array, root2rec, tree2rec
import time

class rawdigits:

    def __init__( self, fname ):
        # constants
        self.NADCS = 9600
        self.NCHAN = 8320

        # load tree
        start = time.time()
        self.tf = rt.TFile( fname, 'open' )
        self.rawtree = self.tf.Get("rawdigitwriter/RawData/RawDigits")
        print "Loading file: ",time.time()-start," secs"
        
        self.waveforms_cached = False

    def loadEvent( self, event ):
        start = time.time()
        print "loading event %d waveforms ..."%(event),
        self.current_rec = tree2rec( self.rawtree, selection="event==%d"%(event) )
        if len(self.current_rec)>0:
            self.waveforms_cached = False
            print " ok."
        else:
            print "No waveforms found from event %d in the file" %(event)
        print "Loading time: ",time.time()-start," secs"

    def getWaveforms( self ):
        if not self.waveforms_cached:
            # extract from record array
            start = time.time()
            self.NADCS = len( self.current_rec["adcs"][0] )
            print "Gettig waveforms, length=",self.NADCS,", number of channels=",self.NCHAN
            self.wfms = np.zeros( (self.NCHAN,self.NADCS), dtype=np.uint16 )
            for r in self.current_rec:
                #print r["adcs"]
                self.wfms[ r["wireid"], :] = r["adcs"][:]
            self.waveforms_cached = True
            print "built wfm array: ",time.time()-start," secs"

        return self.wfms
        



if __name__ == "__main__":
    digits = rawdigits( "~/working/uboone/rawdata/raw_digits.root" )
    digits.loadEvent(11)
    wfms = digits.getWaveforms()
