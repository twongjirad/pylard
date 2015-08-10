from pylard.pylardata.opdataplottable import OpDataPlottable
import numpy as np
import pandas as pd
from root_numpy import root2array, root2rec, tree2rec, array2root
import ROOT
import time

class WFOpData( OpDataPlottable ):
    def __init__(self,inputfile):
        super(WFOpData, self).__init__()
        self.fname = inputfile
        print "Loading file into data frame ..."
        # find first event number
        self.ttree = ROOT.TChain('raw_wf_tree')
        self.ttree.Add( self.fname )
        self.tree_entry = 0
        self.ttree.GetEntry(self.tree_entry)
        self.first_event = self.ttree.event
        self.event_range = [self.first_event, self.first_event+100]
        self.entry_points = {}
        self.entry_points[ self.first_event ] = self.tree_entry

        #self.numpy_rec_array = root2array(self.fname,'raw_wf_tree')
        #numpy_rec_array = tree2rec( self.ttree, selection="event>=%d && event<=%d"%(self.event_range[0], self.event_range[1]) )
        #self.wf_df = pd.DataFrame(self.numpy_rec_array)
        self.loadEventRange( self.event_range[0], self.event_range[1] )
        self.nsamples = len(self.wf_df['wf'][0])
        self.opdetdigi = np.ones( (self.nsamples,48) )*2048.0

    def getEvent( self, eventid, slot=5 ):
        if eventid < self.event_range[0] or eventid > self.event_range[1]:
            self.loadEventRange( eventid-100, eventid+100 )
            
        q = self.wf_df.query('event==%d and slot==%d'%(eventid,slot))
        for ch,ch_df in q.groupby('ch'):
            if ch>=self.opdetdigi.shape[1]:
                continue
            wf = np.array(ch_df['wf'].values[0])
            print ch,wf,self.opdetdigi.shape[0],len(wf)
            self.opdetdigi[:len(wf),ch] = wf[:self.opdetdigi.shape[0]]
        q = self.wf_df.query('event==%d and slot==6 and ch==39'%(eventid)) # hack for flasher
        wf1 = q['wf'][q.first_valid_index()]
        self.opdetdigi[:len(wf1),39] = wf1[:self.opdetdigi.shape[0]]

        
        
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
        start = self.searchEntryHistory( start )
        stop = self.scanForEvent( end+1 )
        print "start/stop entry in tree: ",start,stop
        numpy_rec_array= tree2rec( self.ttree, selection="event>=%d && event<=%d"%(self.event_range[0], self.event_range[1]), start=start, stop=stop )
        #numpy_rec_array= tree2rec( self.ttree )
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
            #print pos, oldevents[pos], " < ", event, " < ",oldevents[pos]
        
        return self.entry_points[ oldevents[pos] ]
