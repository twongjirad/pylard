from pylard.pylardata.opdataplottable import OpDataPlottable
import pylard.pylardata.pedestal as ped
import numpy as np
import pandas as pd
from root_numpy import root2array, root2rec, tree2rec, array2root
import ROOT
import time

class WFOpData( OpDataPlottable ):
    def __init__(self,inputfile):
        super(WFOpData, self).__init__()
        self.fname = inputfile
        print "Loading wf (vector<short>) from 'raw_wf_tree' into pandas data frame ..."
        # find first event number, define first entry range
        self.ttree = ROOT.TChain('raw_wf_tree')
        self.ttree.Add( self.fname )
        self.tree_entry = 0
        self.ttree.GetEntry(self.tree_entry)
        self.first_event = self.ttree.event
        self.event_range = [self.first_event, self.first_event+100]
        self.entry_points = {}
        self.entry_points[ self.first_event ] = self.tree_entry
        self.maxevent = None

        self.loadEventRange( self.event_range[0], self.event_range[1] )
        self.nsamples = len(self.wf_df['wf'][0])
        #self.opdetdigi = np.ones( (self.nsamples,48) )*2048.0
        self.opdetdigi_highgain = np.ones( (self.nsamples,48) )*2048.0
        self.opdetdigi_lowgain  = np.ones( (self.nsamples,48) )*2048.0
    
    def getData( self, slot=5 ):
        if slot==5:
            return self.opdetdigi_highgain
        else:
            return self.opdetdigi_lowgain

    def getPedestal(self,slot=5):
        if slot==5:
            return self.pedestals_highgain
        else:
            return self.pedestals_lowgain        

    def getSampleLength(self):
        return self.nsamples

    def getEvent( self, eventid, slot=5 ):
        if self.maxevent is not None and eventid>=self.maxevent:
            return False

        if eventid < self.event_range[0] or eventid > self.event_range[1]:
            self.loadEventRange( eventid-100, eventid+100 )
            
        q = self.wf_df.query('event==%d and slot==%d'%(eventid,slot))
        for ch,ch_df in q.groupby('ch'):
            if ch>=self.getData(slot=slot).shape[1]:
                continue
            wf = np.array(ch_df['wf'].values[0])
            #print ch,wf,self.getData(slot=slot).shape[0],len(wf)
            self.getData(slot=slot)[:len(wf),ch] = wf[:self.getData(slot=slot).shape[0]]
            self.getPedestal(slot=slot)[ch] = ped.getpedestal( wf[:samples], samples/20, 0.5 )
        # hack for flasher
        #q = self.wf_df.query('event==%d and slot==6 and ch==39'%(eventid)) 
        #wf1 = q['wf'][q.first_valid_index()]
        #self.getData(slot=slot)[:len(wf1),39] = wf1[:self.getData(slot=slot).shape[0]]
        return True

    def loadEventRange( self, start, end ):
        # load event range from tree
        s = time.time()
        print "Getting Data between Event %d and %d" % ( start, end )
        if start>end:
            # come on, man
            tmp = end
            end = start
            start = tmp
        if start<self.first_event:
            start = self.first_event

        # definie new event range
        self.event_range = [ start, end ]
        # we find position in tree
        start_entry = self.searchEntryHistory( start )
        stop_entry = self.scanForEvent( end+1 )
        print "start/stop entry in tree: ",start_entry,stop_entry
        numpy_rec_array= tree2rec( self.ttree, selection="event>=%d && event<=%d"%(self.event_range[0], self.event_range[1]), start=start_entry, stop=stop_entry )
        self.wf_df = pd.DataFrame(numpy_rec_array)
        print "Time to load: ",time.time()-s

    def scanForEvent( self, event, start_entry=0 ):
        entry = start_entry
        bytes = self.ttree.GetEntry(entry)
        while bytes>0:
            if event>=self.ttree.event:
                entry+=1
                bytes = self.ttree.GetEntry(entry)
            else:
                self.entry_points[ self.ttree.event ] = entry
                break
            if bytes==0:
                self.maxevent = entry-1
        return entry
            
    def searchEntryHistory(self, event ):
        # searches entry history, telling the best start entry to scan given past history
        oldevents = self.entry_points.keys()
        if len(oldevents)>0:
            oldevents.sort()
        print oldevents
        pos = len(oldevents)/2
        if len(oldevents)==1:
            return oldevents[0]
        elif len(oldevents)==2:
            if event>oldevents[1]:
                return self.entry_points[oldevents[1]]
            else:
                return oldevents[0]
            
        # now do good old binary search
        oldpos = pos
        while event < oldevents[pos]  or event > oldevents[pos+1]:
            if event<oldevents[pos]:
                pos = int(pos/2)
            elif event>oldevents[pos+1]:
                pos = int((oldpos+pos)/2)
            print pos, oldevents[pos], " < ", event, " < ",oldevents[pos]
        
        return self.entry_points[ oldevents[pos] ]

    
