from pylard.pylardata.opdataplottable import OpDataPlottable
import pylard.pylardata.pedestal as ped
import pylard.pylardata.cosmicdisc as cd
import numpy as np
import pandas as pd
from root_numpy import root2array, root2rec, tree2rec, array2root
import ROOT
import time

"""
This module loads beam and window optical waveforms such that opdetdisplay can retrieve them.
It is able to parse data from
(1) RawDigitsWriter_module.cc (found in uboonecode/uboone/RawData/utils)
(2) WF tree, which is an output by larlite (still experimental)
"""

NCHAN = 48
NSPERTICK = 15.625 # ns
NSPERFRAME = 1600000.0 # 1.6 ms in ns

class RawDigitsOpData( OpDataPlottable ):
    def __init__(self,inputfile, tree_type=None):
        super(RawDigitsOpData, self).__init__()
        self.fname = inputfile

        # if not supplied, determine type of data we've been given
        if tree_type==None:
            f = ROOT.TFile( self.fname )
            if f.GetListOfKeys().Contains("rawdigitwriter"):
                self.tree_type = "rawdigits"
            elif f.GetListOfKeys().Contains("raw_wf_tree"):
                self.tree_type = "wftree"
            else:
                raise ValueError("Cannot determine tree type")

        if self.tree_type=="rawdigits":
            self.ttree = ROOT.TChain('rawdigitwriter/OpDetWaveforms')
            if self.ttree is None:
                self.ttree = ROOT.TChain('rawdigitwriter/RawData/OpDetWaveforms')
            self.configForRawDigits()
            print "Loading adcs (vector<short>) from 'rawdigitwriter/RawData/OpDetWaveforms' into pandas data frame ..."
        elif self.tree_type=="wftree":
            self.ttree = ROOT.TChain('raw_wf_tree')
            self.configForWFTree()
            print "Loading adcs (vector<short>) from 'raw_wf_tree' into pandas data frame..."
        else:
            raise ValueError("tree type must be either 'rawdigits' or 'wftree'")

        # find first event number, define first entry range
        self.ttree.Add( self.fname )
        self.tree_entry = 0
        self.ttree.GetEntry(self.tree_entry)
        self.first_event = self.ttree.event # this is a fortitous accident that both types of trees uses event
        self.event = None
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

    def gotoEvent( self, event, run=None, subrun=None ):
        """ concrete instantiation of abc method """
        if self.maxevent is not None and event>self.maxevent:
            print "No events for ",event,"!"
            return False

        if event==self.event and run==self.run and subrun==self.subrun:
            return True
        self.update_the_sample_size = True # optimization
        self.event  = event
        self.run    = run
        self.subrun = subrun

        # load TTree data into pandas array -- why? why not?
        if event < self.event_range[0] or event > self.event_range[1]:
            self.loadEventRange( event-10, event+100 )

        # separate beam and cosmic readout windows
        self.sortReadoutWindows( event )

        # hack for flasher
        #self.getData(slot=5)[:,39] = self.getData(slot=6)[:,39]
        self.newevent = False
        return True

    def getNextEntry(self):
        """ concrete instantiation of abc method """
        # get next event
        if self.event is not None:
            nextevent = self.event+1
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
            numpy_rec_array= tree2rec( self.ttree, selection="event>%d"%(self.event), start=last_tree_entry, stop=last_tree_entry+10 )
            wf_df = pd.DataFrame(numpy_rec_array)
            nextevent =  wf_df["event"].min()
            self.entry_points[ nextevent ] = last_tree_entry+1
            print "loaded edge of new dataframe. nextevent now ",nextevent
            #raw_input()
            if len(wf_df)==0:
                return False # no more
        else:
            nextevent = q["event"].min()
            #print  q["event"]
            print "next event is ",nextevent
        
        return self.gotoEvent( nextevent )
            

    def loadEventRange( self, start, end ):
        """ load events between range from tree into pandas data frame """
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
        df = self.wf_df[self.__adcs].apply( len )
        self.wf_df['nsamples'] = pd.Series( df, index=self.wf_df.index )

    def getNBeamWinSamples( self):
        if self.event is None:
            print "no current event!"
            return None
        if self.update_the_sample_size:
            df = self.wf_df.query("event==%d"%(int(self.event)))
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

    def sortReadoutWindows( self, event ):

        self.clearEvent()

        self.beamwin_info = {} # stores trigger info
        q = self.wf_df.query('event==%d'%(event))
        if self.__frame is not None and self.__frame in q:
            self.firstframe = q["frame"].min()
        else:
            self.firstframe = 0
        the_trig_timestamp = None
        nbeamwindows = 0

        for femslot,slot_df in q.groupby(self.__slot):
            for ch,ch_df in slot_df.groupby(self.__ch):

                self.beamwin_info[(femslot,ch)] = { "tstamp":0 }

                # must handle old content: we must provide blanks where columns don't exist
                # variables that must have values
                __nentries__ = len(ch_df[self.__tstamp].values)
                v_adc   = ch_df[self.__adcs].values
                v_ts    = ch_df[self.__tstamp].values
                v_slot  = ch_df[self.__slot].values
                # we can make due
                if self.__frame is not None:
                    v_fr  = ch_df[self.__frame].values
                else:
                    v_fr  = np.zeros( __nentries__, dtype=np.int )
                if self.__sample is not None:
                    v_sample = ch_df[self.__sample]
                else:
                    v_sample = np.zeros( __nentries__, dtype=np.int )
                #if self.__trig is not None and self.__trig in ch_df:
                if self.__trig is not None:
                    v_trig = ch_df[self.__trig]
                else:
                    v_trig   = v_ts
                vals = zip( v_adc, v_ts, v_fr, v_sample, v_slot, v_trig )

                for (awf,tstamp,frame,sample,slot,trig_timestamp) in vals:
                    wf = np.array( awf )
                    framesample = self.convertToFrameSample( tstamp, trig_timestamp )
                    if "earliest_tstamp" not in self.beamwin_info:
                        self.beamwin_info["earliest_tstamp"] = trig_timestamp
                        self.beamwin_info["latest_tstamp"] = trig_timestamp+0.015625*1000
                    if len(wf)>=500:
                        if len( self.getBeamWindows( femslot, ch ) )>=1:
                            print "double beam window for (slot %d,ch %d). skip the second one."%(femslot,ch)
                            continue
                        # beam windows!
                        #print "beamwindow waveform len=",len(wf),femslot,"ch=",ch,"tstamp=",tstamp,"trig_stamp=",trig_timestamp,"framesample=",framesample
                        nbeamwindows += 1
                        self.beamwindows.makeWindow( wf, framesample*NSPERTICK, femslot, ch, timepertick=NSPERTICK )
                        self.beamwin_info[(femslot,ch)]["tstamp"] = tstamp
                        the_trig_timestamp = trig_timestamp
                        if ch<32:
                            if "earliest_tstamp" not in self.beamwin_info or self.beamwin_info["earliest_tstamp"]>tstamp:
                                self.beamwin_info["earliest_tstamp"] = tstamp
                            tend = tstamp + (0.001*NSPERTICK)*len( wf ) # microseconds
                            if "latest_tstamp" not in self.beamwin_info or self.beamwin_info["latest_tstamp"]<tend:
                                self.beamwin_info["latest_tstamp"] = tend
                    else:              
                        # cosmic windows!
                        #print "cosmic window len=",len(wf),": slot=",femslot,"ch=",ch,"tstamp=",tstamp,"trig_stamp=",trig_timestamp,"framesample=",framesample
                        self.cosmicwindows.makeWindow( wf, framesample*NSPERTICK, femslot, ch, timepertick=NSPERTICK )
        try:
            print "Event %d has %d cosmic windows and %d beam windows (beam window length=%d)" % ( event, self.cosmics.getNumWindows(), nbeamwindows, self.getNBeamWinSamples() ),
            print " earliest tstamp=",self.beamwin_info["earliest_tstamp"]," trig time=",the_trig_timestamp
        except:
            print "Event ",event," has ",self.cosmicwindows.getNumWindows()," cosmic windows and ",self.beamwindows.getNumWindows()," beam windows (length=",self.getNBeamWinSamples(),")"
            
    def convertToFrameSample( self, timestamp, trig_timestamp  ):
        return int( (timestamp-trig_timestamp)/(0.001*NSPERTICK) ) # timestamps in microseconds of course                                                  

    def configForRawDigits(self):
        self.__run    = "run"
        self.__subrun = "subrun"
        self.__event  = "event"
        self.__slot   = "opslot"
        self.__ch     = "opfemch"
        self.__tstamp = "timestamp"
        self.__frame  = "frame"
        self.__sample = "sample"
        self.__trig   = "trig_timestamp"
        self.__adcs   = "adcs"

    def configForWFTree(self):
        self.__run    = "run"
        self.__subrun = "subrun"
        self.__event  = "event"
        self.__slot   = "slot"
        self.__ch     = "ch"
        self.__tstamp = "timestamp"
        self.__adcs   = "wf"
        if "frame" in dir(self.ttree):
            self.__frame = "frame"
        else:
            self.__frame = None
        if "sample" in dir(self.ttree):
            self.__sample = "sample"
        else:
            self.__sample = None
        if "trig" in dir(self.ttree):
            self.__trig = "trig"
        else:
            self.__trig = None
