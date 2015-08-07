from pylard.pylardata.opdataplottable import OpDataPlottable
import numpy as np
import pandas as pd
from root_numpy import root2array, root2rec, tree2rec, array2root
import ROOT

class WFOpData( OpDataPlottable ):
    def __init__(self,inputfile):
        super(WFOpData, self).__init__()
        self.fname = inputfile
        print "Loading file into data frame ..."
        self.numpy_rec_array = root2array(self.fname,'raw_wf_tree')
        self.wf_df = pd.DataFrame(self.numpy_rec_array)
        self.nsamples = len(self.wf_df['wf'][0])
        self.opdetdigi = np.ones( (self.nsamples,48) )*2048.0
        print "Loaded."


    def getEvent( self, eventid, slot=5 ):
        q = self.wf_df.query('event==%d and slot==%d'%(eventid,slot))
        for ch,ch_df in q.groupby('ch'):
            if ch>=self.opdetdigi.shape[1]:
                continue
            wf = np.array(ch_df['wf'].values[0])
            print ch,wf,self.opdetdigi.shape[0],len(wf)
            self.opdetdigi[:len(wf),ch] = wf[:self.opdetdigi.shape[0]]

        
        
