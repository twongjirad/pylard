import os,sys
import ROOT as rt
from ROOT import std
import numpy as np
from pylard.visrawdigits.rawdigitsopdata import RawDigitsOpData

class rawdigits_processor:
    USPERTICK = 0.015625
    NSPERTICK = 15.625
    def __init__(self,fileman):
        self.opwfms  = rt.TChain("rawdigitwriter/OpDetWaveforms")
        self.tpcwfms = rt.TChain("rawdigitwriter/RawDigits")
        for s in fileman.sorted_filelist:
            self.opwfms.Add(s)
            self.tpcwfms.Add(s)
        self.rawdigits_entrymap = fileman.rawdigits_entrymap
        self.rawdigits_tpcindex = fileman.rawdigits_tpcindex
        self.entry_dict = fileman.entry_dict
        self.rse_dict   = fileman.rse_dict
        self.opdata = None
        self.tpcdata = None

    def configure(self,pset):
        pass

    def get_entry(self,entry):
        self.opdata = self._getOpWfms(entry)
        self.tpcdata = self._getTPCdata(entry)
        return True
    
    def get_opdata(self):
        return self.opdata

    def get_tpcdata(self):
        return self.tpcdata

    def _getOpWfms(self,entry):
        rse = self.entry_dict[entry]
        (optree_pos,optree_nentries) = self.rawdigits_entrymap[rse]

        opdata = RawDigitsOpData()

        beamwin_info = {} # stores trigger info
        firstframe = 0
        the_trig_timestamp = None
        nbeamwindows = 0
        maxbeamsamples = 0
        print "entry pos=",optree_pos," nentries=",optree_nentries
        for ientry in range(optree_pos,optree_pos+optree_nentries):
            self.opwfms.GetEntry(ientry)

            # make a dict entry for this slot,ch combination
            femslot = self.opwfms.opslot
            ch      = self.opwfms.opfemch%100
            beamwin_info[(femslot,ch)] = { "tstamp":0 }

            nticks  = len(self.opwfms.adcs)
            if nticks>maxbeamsamples:
                maxbeamsamples = nticks
            v_adc   = self.opwfms.adcs
            v_ts    = self.opwfms.timestamp
            v_fr    = self.opwfms.frame
            v_sm    = self.opwfms.sample
            v_trig  = self.opwfms.trig_timestamp
            
            wf = np.array( v_adc )
            framesample = self.convertToFrameSample( v_ts, v_trig )
            #for (awf,tstamp,frame,sample,slot,trig_timestamp) in vals:
                
            if "earliest_tstamp" not in beamwin_info:
                beamwin_info["earliest_tstamp"] = v_trig
                beamwin_info["latest_tstamp"]   = v_trig+rawdigits_processor.USPERTICK*1000
            if len(wf)>=500:
                if len( opdata.getBeamWindows( femslot, ch ) )>=1:
                    print "double beam window for (slot %d,ch %d). skip the second one."%(femslot,ch)
                    continue
                # beam windows!
                #print "beamwindow waveform len=",len(wf),femslot,"ch=",ch,"tstamp=",tstamp,"trig_stamp=",trig_timestamp,"framesample=",framesample
                nbeamwindows += 1
                opdata.beamwindows.makeWindow( wf, framesample*rawdigits_processor.NSPERTICK, femslot, ch, timepertick=rawdigits_processor.NSPERTICK )
                beamwin_info[(femslot,ch)]["tstamp"] = v_ts
                the_trig_timestamp = v_trig
                if ch<32:
                    if "earliest_tstamp" not in beamwin_info or beamwin_info["earliest_tstamp"]>v_ts:
                        beamwin_info["earliest_tstamp"] = v_ts
                    tend = v_ts + (rawdigits_processor.USPERTICK)*len( wf ) # microseconds
                    if "latest_tstamp" not in beamwin_info or beamwin_info["latest_tstamp"]<tend:
                        beamwin_info["latest_tstamp"] = tend
            else:              
                # cosmic windows!
                #print "cosmic window len=",len(wf),": slot=",femslot,"ch=",ch,"tstamp=",tstamp,"trig_stamp=",trig_timestamp,"framesample=",framesample
                opdata.cosmicwindows.makeWindow( wf, framesample*rawdigits_processor.NSPERTICK, femslot, ch, timepertick=rawdigits_processor.NSPERTICK )
        try:
            print "Event %s has %d cosmic windows and %d beam windows (beam window length=%d)" % ( str(rse),
                                                                                                   opdata.cosmics.getNumWindows(), 
                                                                                                   nbeamwindows, maxbeamsamples ),
            print " earliest tstamp=",beamwin_info["earliest_tstamp"]," trig time=",the_trig_timestamp
        except:
            print "Event ",rse," has ",opdata.cosmicwindows.getNumWindows()," cosmic windows and ",
            print opdata.beamwindows.getNumWindows()," beam windows (max length=",maxbeamsamples,")"
        return opdata
            
    def convertToFrameSample( self, timestamp, trig_timestamp  ):
        return int( (timestamp-trig_timestamp)/(rawdigits_processor.USPERTICK) ) # timestamps in microseconds of course                                                  

    def _getTPCdata(self,entry):
        rse = self.entry_dict[entry]
        # our job is to get the vector of values into memory. the vis processor will convert to image2D for us
        start_entry = self.rawdigits_tpcindex[rse][0]
        nentries    = self.rawdigits_tpcindex[rse][1]

        adcs = {0:{},
                1:{},
                2:{}}
        for ientry in range(start_entry,start_entry+nentries):
            self.tpcwfms.GetEntry(ientry)
            wireid = self.tpcwfms.wireid
            if wireid<2400:
                planeid = 0
                ch = wireid
            elif wireid>=2400 and wireid<4800:
                planeid = 1
                ch = wireid-2400
            elif wireid>=4800:
                planeid = 2
                ch = wireid-4800
            # do I need to write a C++ wrapper function here?
            adc_v = std.vector("short")( self.tpcwfms.adcs )
            adcs[planeid][ch] = adc_v
        print "transferred wfms: plane0=",len(adcs[0]),"plane1=",len(adcs[1]),"plane2=",len(adcs[2])
        return adcs
