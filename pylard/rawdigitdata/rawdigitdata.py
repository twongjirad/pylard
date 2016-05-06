from pylard.core.datainterface import DataInterface
from pylard.core.eventdata import EventData
from pylard.core.eventindex import EventIndex
import ROOT
import numpy as np
from threading import Thread
from time import sleep

# should turn these into class variables
NCHAN = 48
NSPERTICK = 15.625 # ns
NSPERFRAME = 1600000.0 # 1.6 ms in ns

def fill_meta( rawdatainstance ):
    index = rawdatainstance.getNextEventIndexOnly()
    while index is not None:
        index = rawdatainstance.getNextEventIndexOnly()
    rawdatainstance.meta_filled = True
    print "Meta filled."

class RawDigitData(DataInterface):
    def __init__(self):
        super(DataInterface,self).__init__()
        self.entry_list = []
        self.event_dict = {} # index to start of entry
        self.meta_filled = False

    def loadFilelist(self, filelist, tree_type=None ):
        # if not supplied, determine type of data we've been given
        if tree_type==None:
            f = ROOT.TFile( filelist[0])
            if f.GetListOfKeys().Contains("rawdigitwriter"):
                self.tree_type = "rawdigits"
            elif f.GetListOfKeys().Contains("raw_wf_tree"):
                self.tree_type = "wftree"
            else:
                raise ValueError("Cannot determine tree type")
            print "Loading data of type: ",self.tree_type

        # setup trees [we make two tree copies. one is going to be used for data. the other for generating meta data]
        if self.tree_type=="rawdigits":
            self.ttree = ROOT.TChain('rawdigitwriter/OpDetWaveforms')
            self.ttree_meta = ROOT.TChain('rawdigitwriter/OpDetWaveforms')
            if self.ttree is None:
                self.ttree = ROOT.TChain('rawdigitwriter/RawData/OpDetWaveforms')
                self.ttree_meta = ROOT.TChain('rawdigitwriter/RawData/OpDetWaveforms')
            self.configForRawDigits()
        elif self.tree_type=="wftree":
            self.ttree = ROOT.TChain('raw_wf_tree')
            self.ttree_meta = ROOT.TChain('raw_wf_tree')
            self.configForWFTree()
            print "Loading adcs (vector<short>) from 'raw_wf_tree' into pandas data frame..."
        else:
            raise ValueError("tree type must be either 'rawdigits' or 'wftree'")

        for f in filelist:
            self.tree_entry = -1
            self.ttree.Add( f )
            self.tree_meta_entry = -1
            self.ttree_meta.Add( f )
        print "Loaded filelist containing %d events"%(self.ttree_meta.GetEntries())
        # load the first meta index
        self.current_index = 0
        self.current_eventindex = self.getNextEventIndexOnly()
        # start thread to fill the meta
        self.meta_thread = Thread( target=fill_meta, args=(self,) )
        self.meta_thread.setDaemon(True)
        self.meta_thread.start()

    def processEventData( self, eventdata ):
        pass

    def getEvent( self, eventindex ):
        # This is annoying because each entry in the tree is not an event, but a waveform
        # by default. So we use the indices we've built up to do this
        if eventindex not in self.event_dict:
            return False
        self.ttree_entry = self.event_dict[eventindex]
        numbytes = self.ttree.GetEntry(self.ttree_entry)
        if numbytes==0:
            return None
        eventdata = EventData(eventindex.run,eventindex.subrun,eventindex.event,subevent=eventindex.subevent)
        self.fillEventData( eventdata )
        return eventdata

    def getCurrentEvent(self):
        return self.getEvent(self.current_eventindex)

    def getNextEvent( self ):
        if self.current_index+1==len(self.entry_list):
            # we are out of indices, go to the next one
            index = self.getNextEventIndexOnly()
            if index is None:
                return None
        self.current_index += 1
        self.current_eventindex = self.entry_list[self.current_index]
        return self.getEvent(self.current_eventindex)

    def getPreviousEvent( self ):
        if self.current_index == 0:
            return None
        self.current_index -= 1
        self.current_eventindex = self.entry_list[self.current_index]
        return self.getEvent(self.current_eventindex)

    def getNextEventIndexOnly(self):
        # we build a table of event index to tree entry to help navigate this data
        # really, rawdigitwriter should provide a meta data table
        numbytes = 1
        newindexfound = False
        while numbytes>0 and not newindexfound:
            self.tree_meta_entry += 1
            numbytes = self.ttree_meta.GetEntry(self.tree_meta_entry)
            if numbytes==0:
                return None
            exec("run=self.ttree_meta.%s"%(self.__run))
            exec("subrun=self.ttree_meta.%s"%(self.__subrun))
            exec("event=self.ttree_meta.%s"%(self.__event))
            index = EventIndex(run,subrun,event)
            if index not in self.event_dict:
                self.entry_list.append(index)
                self.event_dict[index] = self.tree_meta_entry
                newindexfound = True 
                return index
        return None

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

    def printEventTable(self):
        for index in self.entry_list:
            print index,self.event_dict[index]

    def convertToFrameSample( self, timestamp, trig_timestamp  ):
        return int( (timestamp-trig_timestamp)/(0.001*NSPERTICK) ) # timestamps in microseconds of course 

    def fillEventData(self,eventdata):
        # assume the self.ttree has been lined up. we now just load up on data
        
        # need the first frame to get the right timing. we either need to loop here and come back
        #  or get all frames, track the min, then go back and calculate the times...
        #if self.__frame is not None and self.__frame in q:
        #    self.firstframe = q["frame"].min()
        #else:
        #    self.firstframe = 0
        the_trig_timestamp = None
        nbeamwindows = 0

        br_event = None
        br_slot  = None
        br_ch    = None
        br_timestamp = None
        bt_trig = None
        br_adcs_v = None
        

        entry = self.ttree_entry
        numbytes = self.ttree.GetEntry(entry)
        print "start event fill: ",entry,numbytes,br_event
        while numbytes>0 and (br_event==eventdata.index.event or br_event is None):
            
            exec("br_event=self.ttree.%s"%(self.__event))
            exec("br_slot=self.ttree.%s"%(self.__slot))
            exec("br_ch=self.ttree.%s"%(self.__ch))
            exec("br_timestamp=self.ttree.%s"%(self.__tstamp))
            exec("br_adcs_v=self.ttree.%s"%(self.__adcs))
            exec("br_trig=self.ttree.%s"%(self.__trig))

            # must handle old content: we must provide blanks where columns don't exist
            # variables that must have values
            # __nentries__ = len(ch_df[self.__tstamp].values) # not applicable anymore
            
            # we can make due without a frame
            #if self.__frame is not None:
            #    v_fr  = ch_df[self.__frame].values
            #else:
            #    v_fr  = np.zeros( __nentries__, dtype=np.int )

            wf = np.array( br_adcs_v )    
            framesample = self.convertToFrameSample( br_timestamp, br_trig )
            the_trig_timestamp = br_trig

            if len(wf)>=500:
                # beam windows!
                #print "beamwindow waveform len=",len(wf),femslot,"ch=",ch,"tstamp=",tstamp,"trig_stamp=",trig_timestamp,"framesample=",framesample
                eventdata.opdata.addBeamWindow( wf, framesample*NSPERTICK, br_slot, br_ch, br_timestamp, timepertick=NSPERTICK )
            else:              
                # cosmic windows!
                #print "cosmic window len=",len(wf),": slot=",femslot,"ch=",ch,"tstamp=",tstamp,"trig_stamp=",trig_timestamp,"framesample=",framesample
                eventdata.opdata.addCosmicWindow( wf, framesample*NSPERTICK, br_slot, br_ch, timepertick=NSPERTICK )
            entry += 1
            numbytes = self.ttree.GetEntry(entry)
            #print entry,br_event,eventdata.index.event

        try:
            print "RawDigitData: Event %d has %d cosmic windows and %d beam windows (beam window length=%d)" % ( eventdata.index.event, eventdata.opdata.cosmicwindows.getNumWindows(), eventdata.opdata.beamwindows.getNumWindows(), eventdata.opdata.getNBeamWinSamples() ),
            print " earliest tstamp=",eventdata.opdata.beamwin_info["earliest_tstamp"],"the trig=",the_trig_timestamp
        except:
            print "RawDigitData: Event ",eventdata.index.event," has ",eventdata.opdata.cosmicwindows.getNumWindows()," cosmic windows and ",eventdata.opdata.beamwindows.getNumWindows()," beam windows (length=",eventdata.opdata.getNBeamWinSamples(),")"
    
    def isMetaFilled(self):
        return self.meta_filled



if __name__=="__main__":

    filelist = ["run5269_subrun79.root"]
    test = RawDigitData()
    test.loadFilelist(filelist)
    while not test.isMetaFilled():
        print "wait 1 s"
        sleep(1)
        test.printEventTable()
    print "CURRENT: ",test.current_eventindex
    test.getCurrentEvent()


