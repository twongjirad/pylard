from pylard.pylardata.opdataplottable import OpDataPlottable
import pylard.pylardata.pedestal as ped
import pylard.pylardata.cosmicdisc as cd
import numpy as np
import pandas as pd
from root_numpy import root2array, root2rec, tree2rec, array2root
import ROOT
import time

"""
******************************************************************************
*Tree    :OpDetWaveforms: PMT Readout Waveforms                                  *
*Entries :   638639 : Total =       361102141 bytes  File  Size =   99788152 *
*        :          : Tree compression factor =   3.62                       *
******************************************************************************
*Br    0 :run       : run/I                                                  *
*Entries :   638639 : Total  Size=    2557942 bytes  File Size  =      16047 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression= 159.35     *
*............................................................................*
*Br    1 :subrun    : subrun/I                                               *
*Entries :   638639 : Total  Size=    2558047 bytes  File Size  =      14728 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression= 173.62     *
*............................................................................*
*Br    2 :event     : event/I                                                *
*Entries :   638639 : Total  Size=    2558012 bytes  File Size  =      20771 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression= 123.11     *
*............................................................................*
*Br    3 :opcrate   : opcrate/I                                              *
*Entries :   638639 : Total  Size=    2558082 bytes  File Size  =      16115 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression= 158.68     *
*............................................................................*
*Br    4 :opslot    : opslot/I                                               *
*Entries :   638639 : Total  Size=    2558047 bytes  File Size  =      29055 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression=  88.01     *
*............................................................................*
*Br    5 :opfemch   : opfemch/I                                              *
*Entries :   638639 : Total  Size=    2558082 bytes  File Size  =     206079 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression=  12.41     *
*............................................................................*
*Br    6 :frame     : frame/I                                                *
*Entries :   638639 : Total  Size=    2558012 bytes  File Size  =     269925 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression=   9.47     *
*............................................................................*
*Br    7 :sample    : sample/I                                               *
*Entries :   638639 : Total  Size=    2558047 bytes  File Size  =    1141255 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression=   2.24     *
*............................................................................*
*Br    8 :timestamp : timestamp/D                                            *
*Entries :   638639 : Total  Size=    5115260 bytes  File Size  =    1498956 *
*Baskets :       55 : Basket Size=     679936 bytes  Compression=   3.41     *
*............................................................................*
*Br    9 :readoutch : readoutch/I                                            *
*Entries :   638639 : Total  Size=    2558152 bytes  File Size  =     222101 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression=  11.51     *
*............................................................................*
*Br   10 :category  : category/I                                             *
*Entries :   638639 : Total  Size=    2558117 bytes  File Size  =      26441 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression=  96.71     *
*............................................................................*
*Br   11 :gaintype  : gaintype/I                                             *
*Entries :   638639 : Total  Size=    2558117 bytes  File Size  =      26419 *
*Baskets :       31 : Basket Size=     339968 bytes  Compression=  96.79     *
*............................................................................*
*Br   12 :trig_timestamp : trig_timestamp/D                                  *
*Entries :   638639 : Total  Size=    5115555 bytes  File Size  =      44556 *
*Baskets :       55 : Basket Size=     679936 bytes  Compression= 114.78     *
*............................................................................*
*Br   13 :beam_timestamp : beam_timestamp/D                                  *
*Entries :   638639 : Total  Size=    5115555 bytes  File Size  =      34756 *
*Baskets :       55 : Basket Size=     679936 bytes  Compression= 147.14     *
*............................................................................*
*Br   14 :adcs      : vector<short>                                          *
*Entries :   638639 : Total  Size=  317616581 bytes  File Size  =   96187862 *
*Baskets :     3055 : Basket Size=   25600000 bytes  Compression=   3.30     *
*............................................................................*
"""

NCHAN = 48
NSPERTICK = 15.625 # ns
NSPERFRAME = 1600000.0 # 1.6 ms in ns

class RawDigitsOpData( OpDataPlottable ):
    def __init__(self,inputfile):
        super(RawDigitsOpData, self).__init__()
        self.fname = inputfile
        print "Loading adcs (vector<short>) from 'rawdigitwriter/RawData/OpDetWaveforms' into pandas data frame ..."
        # find first event number, define first entry range
        self.ttree = ROOT.TChain('rawdigitwriter/RawData/OpDetWaveforms')
        self.ttree.Add( self.fname )
        self.tree_entry = 0
        self.ttree.GetEntry(self.tree_entry)
        self.first_event = self.ttree.event
        self.current_event = None
        self.event_range = [self.first_event, self.first_event+100]
        self.entry_points = {}
        self.entry_points[ self.first_event ] = self.tree_entry
        self.maxevent = None
        self.update_the_sample_size = False # optimization. tells getNBeamWinSamples to either calculate or use cached value
        self.__nbeamsamples = 0 # cached value of beam window size for the event

        self.loadEventRange( self.event_range[0], self.event_range[1] )

        self.opdetdigits = {}
        self.pedestals = {}

    def getData( self, slot=5, remake=False ):
        if slot not in self.opdetdigits or remake==True:
            print "Allocating array for slot ",slot," with length: ",self.getNBeamWinSamples()
            self.opdetdigits[slot] = np.ones( (self.getNBeamWinSamples(),48) )*2048.0
        return self.opdetdigits[slot]

    def getPedestal(self,slot=5):
        if slot not in self.pedestals:
            self.pedestals[slot] = np.ones( 48 )*2048.0
        return self.pedestals[slot]

    def getEvent( self, eventid, slot=5 ):
        if self.maxevent is not None and eventid>self.maxevent:
            print "No events for ",eventid,"!"
            return False

        if eventid==self.current_event:
            return True
        self.update_the_sample_size = True # optimization
        self.current_event = eventid

        # load TTree data into pandas array -- why? why not?
        if eventid < self.event_range[0] or eventid > self.event_range[1]:
            self.loadEventRange( eventid-10, eventid+100 )

        # sepaarate beam and cosmic readout windows
        self.sortReadoutWindows( eventid )

        # store the beam windows into the numpy array expected by the parent class
        self.fillBeamWindowArray()

        # hack for flasher
        self.getData(slot=5)[:,39] = self.getData(slot=6)[:,39]
        self.newevent = False
        return True

    def getNextEvent(self):
        # get next event
        if self.current_event is not None:
            nextevent = self.current_event+1
        else:
            nextevent = self.first_event
        if self.maxevent is not None and nextevent>=self.maxevent:
            print "No events for ",nextevent,"! maxevent=",self.maxevent
            return False
        ok = True
        inc = 1

        q = self.wf_df.query( "event>=%d"%(nextevent) )
        if len( q )==0:
            print "empty query. must find next event number if tree"
            events = self.entry_points.keys()
            events.sort()
            last_tree_entry = self.entry_points[ events[-1] ]
            numpy_rec_array= tree2rec( self.ttree, selection="event>%d"%(self.current_event), start=last_tree_entry, stop=last_tree_entry+10 )
            wf_df = pd.DataFrame(numpy_rec_array)
            nextevent =  wf_df["event"].min()
            self.entry_points[ nextevent ] = last_tree_entry+1
            print "loaded edge of new dataframe. nextevent now ",nextevent
            #raw_input()
            if len(wf_df)==0:
                return False # no more
        else:
            nextevent = q["event"].min()
            print "next event is ",nextevent
        
        return self.getEvent( nextevent )
            

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
        # load data into pandas dataframe
        numpy_rec_array= tree2rec( self.ttree, selection="event>=%d && event<=%d"%(self.event_range[0], self.event_range[1]), start=start_entry, stop=stop_entry )
        self.wf_df = pd.DataFrame(numpy_rec_array)
        # append the sample sizes of adc strings as a column to dataframe
        self.determineWaveformLengths()
        print "Time to load: ",time.time()-s

    def determineWaveformLengths( self ):
        df = self.wf_df['adcs'].apply( len )
        self.wf_df['nsamples'] = pd.Series( df, index=self.wf_df.index )

    def getNBeamWinSamples( self):
        if self.current_event is None:
            print "no current event!"
            return None
        if self.update_the_sample_size:
            df = self.wf_df.query("event==%d"%(int(self.current_event)))
            self.__nbeamsamples = df["nsamples"].max()
            self.update_the_sample_size = False
        return self.__nbeamsamples
        

    def scanForEvent( self, event, start_entry=0 ):
        entry = start_entry
        bytes = self.ttree.GetEntry(entry)
        lastevent = None
        while bytes>0 and self.ttree.event<=event:
            lastevent = self.ttree.event
            if event>=self.ttree.event:
                entry+=1 # keep going
            #print entry, lastevent
            bytes = self.ttree.GetEntry(entry)
            if bytes==0:
                self.maxevent = lastevent
                print "Found max event! ",self.maxevent
            self.entry_points[ self.ttree.event ] = entry-1
        return entry

    def searchEntryHistory(self, event ):
        # searches entry history, telling the best start entry to scan given past history
        oldevents = self.entry_points.keys()
        if len(oldevents)>0:
            oldevents.sort()
        #print "event index history: ",self.entry_points
        if len(oldevents)==1:
            return self.entry_points[oldevents[0]]
        elif len(oldevents)==2:
            if event>oldevents[1]:
                return self.entry_points[oldevents[1]]
            else:
                return oldevents[0]
            
        # now do good old binary search
        hipos = len(oldevents)-1
        lopos = 0
        while np.abs(hipos-lopos)>1:
            newpos = (hipos+lopos)/2
            if event<oldevents[newpos]:
                hipos = newpos
            elif event>oldevents[newpos]:
                lopos = newpos
            else:
                # found it!
                lopos = newpos
                break
            print "newpos=",newpos, "lo=",lopos,"hi=",hipos,oldevents[lopos], " < ", event, " < ",oldevents[hipos]
        
        return self.entry_points[ oldevents[lopos] ]

    def sortReadoutWindows( self, eventid ):
        # clear stores
        self.cosmics = cd.CosmicDiscVector()
        self.beamwin_wfms = {}
        self.beamwin_info = {}
        q = self.wf_df.query('event==%d'%(eventid))
        self.firstframe = q["frame"].min()
        for femslot,slot_df in q.groupby('opslot'):
            for ch,ch_df in slot_df.groupby('opfemch'):
                if ch>=self.getData(slot=femslot).shape[1]:
                    continue
                self.beamwin_wfms[(femslot,ch)] = []
                self.beamwin_info[(femslot,ch)] = { "tstamp":0 }
                if "trig_timestamp" in ch_df:
                    vals = zip( ch_df['adcs'].values, ch_df['timestamp'].values,ch_df['frame'].values,ch_df['sample'].values,ch_df['opslot'].values,ch_df['trig_timestamp'])
                else:
                    # deprecated, should remove.
                    vals = zip( ch_df['adcs'].values, ch_df['timestamp'].values,ch_df['frame'].values,ch_df['sample'].values,ch_df['opslot'].values,ch_df['timestamp'].values)
                for (awf,tstamp,frame,sample,slot,trig_timestamp) in vals:
                    wf = np.array( awf )
                    if len(wf)>=1000:
                        self.beamwin_wfms[(femslot,ch)].append( wf )
                        self.beamwin_info[(femslot,ch)]["tstamp"] = tstamp
                        if ch<32:
                            if "earliest_tstamp" not in self.beamwin_info or self.beamwin_info["earliest_tstamp"]>tstamp:
                                self.beamwin_info["earliest_tstamp"] = tstamp
                            tend = tstamp + (0.001*NSPERTICK)*len( wf ) # microseconds
                            if "latest_tstamp" not in self.beamwin_info or self.beamwin_info["latest_tstamp"]<tend:
                                self.beamwin_info["latest_tstamp"] = tend
                    else:                            
                        framesample = self.convertToFrameSample( tstamp, trig_timestamp )
                        #print "cosmic window: ",femslot,ch,tstamp,trig_timestamp,framesample
                        cwd = cd.CosmicDiscWindow( wf, femslot, ch, framesample )
                        self.cosmics.addWindow( cwd )
        try:
            print "Event %d has %d cosmic windows and %d beam windows (beam window length=%d)" % ( eventid, self.cosmics.getNumWindows(), len(self.beamwin_wfms), self.getNBeamWinSamples() )
        except:
            print "Event ",eventid," has ",self.cosmics.getNumWindows()," cosmic windows and ",len(self.beamwin_wfms)," beam windows (length=",self.getNBeamWinSamples(),")"
            
    def convertToFrameSample( self, timestamp, trig_timestamp  ):
        return int( (timestamp-trig_timestamp)/(0.001*NSPERTICK) ) # timestamps in microseconds of course
                                                  
    def fillBeamWindowArray( self ):

        # allocate correct array size
        tstart = self.beamwin_info["earliest_tstamp"]
        tend   = self.beamwin_info["latest_tstamp"]
        nbeamsamples = int( (tend-tstart)/(0.001*NSPERTICK) )
        self.beamwin_info["nsamples"] = nbeamsamples
        self.update_the_sample_size = False
        self.__nbeamsamples = nbeamsamples
        print "BEAM WINDOW SAMPLES = ",nbeamsamples," tstart=",tstart," tend=",tend
        for slot in [5,6]:
            self.opdetdigits[slot] = np.ones( (nbeamsamples,48) )*2048.0

        for (femslot,ch),wfs in self.beamwin_wfms.items():
            # first get earliest time stamp
            tstamp = self.beamwin_info[(femslot,ch)]["tstamp"]
            firstsample = int( (tstamp-tstart)/(0.001*NSPERTICK) )
            firstwfmsample = 0
            if firstsample<0:
                firstsample = 0
                firstwfmsample = -firstsample
            #print "slot ",femslot," ch",ch," first sample=",firstsample
            for wf in wfs:
                copylen = np.minimum(firstsample+len(wf),nbeamsamples)-firstsample
                if copylen>len(wf)-firstwfmsample:
                    copylen = len(wf)-firstwfmsample
                self.opdetdigits[femslot][firstsample:firstsample+copylen,ch] = wf[firstwfmsample:copylen]
                if firstsample!=0:
                    self.opdetdigits[femslot][:firstsample,ch] = wf[0]
                if firstsample+copylen<nbeamsamples:
                    self.opdetdigits[femslot][firstsample+copylen:,ch] = wf[-1]
                self.getPedestal(slot=femslot)[ch] = ped.getpedestal( self.opdetdigits[femslot][:,ch], int(nbeamsamples/20), 1.0, verbose=False )
