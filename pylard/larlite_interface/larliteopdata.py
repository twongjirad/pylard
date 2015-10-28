import os,sys
import numpy as np
from pylard.pylardata.opdataplottable import OpDataPlottable
from ophit import OpHitData
from opflash import OpFlashData
from trigger import TriggerData
import ROOT
from ROOT import larlite

class LArLiteOpticalData( OpDataPlottable ):
    """ interface class between LArLite Optical data and OpDataPlottable """
    
    def __init__(self,inputfiles):
        super( LArLiteOpticalData , self ).__init__()

        # input file name
        self.files = inputfiles

        # producers for various data-products
        self.opwf_producer    = 'pmtreadout' # pmtreadout for data
        self.ophit_producer   = 'opFlash'
        self.opflash_producer = 'opFlash'
        self.trigger_producer = 'triggersim'

        # prepare a list of files for each data-product & producer
        self.opwf_files    = []
        self.ophit_files   = []
        self.opflash_files = []
        self.trigger_files = []
        self.SplitInputFiles()

        # limiter for now
        self.n_pmts = 48

        # call larlite manager
        self.manager = larlite.storage_manager()
        self.manager.reset()
        self.usedfiles = []
        for f in self.opwf_files:
            self.manager.add_in_filename(f)
            self.usedfiles.append( f )
        for f in self.ophit_files:
            if f not in self.usedfiles:
                self.manager.add_in_filename(f)
                self.usedfiles.append( f )
        for f in self.opflash_files:
            if f not in self.usedfiles:
                self.manager.add_in_filename(f)
                self.usedfiles.append( f )
        for f in self.trigger_files:
            if f not in self.usedfiles:
                self.manager.add_in_filename(f)
                self.usedfiles.append( f )

        self.manager.set_io_mode(larlite.storage_manager.kREAD)
        self.manager.open()
        
        # OpticalData owns instances of all data object classes
        self.ophits  = OpHitData(self.ophit_producer)
        self.opflash = OpFlashData(self.opflash_producer)
        self.trigger = TriggerData(self.trigger_producer)

        self.manager.next_event()

        self.event  = self.manager.event_id()
        self.subrun = self.manager.subrun_id()
        self.run    = self.manager.run_id()

        # event location
        self.first_event = self.event
        self.event_range = [ self.first_event, self.first_event+49 ]
        self.entry_points = {}
        self.entry_points[ self.first_event ] = 0


    def SplitInputFiles(self):

        # name of trees expected given the producer names
        opdigit_t = 'opdigit_%s_tree'%self.opwf_producer
        ophit_t   = 'ophit_%s_tree'%self.opflash_producer
        opflash_t   = 'opflash_%s_tree'%self.opflash_producer
        trigger_t   = 'trigger_%s_tree'%self.trigger_producer

        # go through list of files and sub-split files with
        # specific data-products
        if type(self.files) is str:
            self.files = [self.files]
        for f in self.files:
            
            # skip if not root file
            if (f.find('.root') < 0):
                continue

            froot = ROOT.TFile(f)

            # if the file contains waveforms
            if (froot.GetListOfKeys().Contains(opdigit_t) == True):
                self.opwf_files.append(f)
            else:
                print "no %s in %s"%(opdigit_t,f)

            # if the file contains hits
            if (froot.GetListOfKeys().Contains(ophit_t) == True):
                self.ophit_files.append(f)

            # if the file contains flashes
            if (froot.GetListOfKeys().Contains(opflash_t) == True):
                self.opflash_files.append(f)

            # if the file contains trigger information
            if (froot.GetListOfKeys().Contains(trigger_t) == True):
                self.trigger_files.append(f)

        print 'waveform files:'
        print self.opwf_files
        print
        print 'hit files:'
        print self.ophit_files
        print
        print 'opflash files:'
        print self.opflash_files
        print
        print 'trigger files:'
        print self.trigger_files
        print


    # ------------------------
    # Move to a specific event
    def gotoEvent(self, eventid, run=None, subrun=None):
        """ required method from abc """

        # what is the difference between the
        # requested event and the first one?
        evt_diff = eventid - self.first_event

        self.manager.go_to(evt_diff)
        
        isok = self.loadEvent()
        return isok

    def getNextEntry( self ):
        """ required method from abc """
        self.manager.next_event()
        isok = self.loadEvent()
        return isok

    def loadEvent( self ):

        self.event  = self.manager.event_id()
        self.subrun = self.manager.subrun_id()
        self.run    = self.manager.run_id()

        # save the trigger information for this event
        self.trigger.getEvent(self.manager)

        # save the trigger time for the entire event
        self.trigger_time = self.trigger.getTrigTime()

        self.fillWaveforms()
        
        self.ophits.getEvent(self.manager)

        self.opflash.getEvent(self.manager)

        self.event  = self.manager.event_id()
        self.subrun = self.manager.subrun_id()
        self.run    = self.manager.run_id()

        return True

        

    # ------------------------
    # function to fill wf info
    def fillWaveforms( self ):

        self.clearEvent()

        # load optical waveforms
        self.opdata = self.manager.get_data(larlite.data.kOpDetWaveform, self.opwf_producer)

        print "number of opdet waveforms: ",self.opdata.size()," trigger time=",self.trigger_time

        # loop through all waveforms and add them to beam and cosmic containers
        # self.opdata contains the larlite::ev_opdetwaveform object
        for n in xrange(self.opdata.size()):
        
            wf = self.opdata.at(n)

            pmt = wf.ChannelNumber()

            # only use first 48 pmts (HG SLOT)
            if ( pmt >= self.n_pmts ):
                continue

            # adcs
            adcs = []
            for i in xrange(wf.size()):
                adcs.append(wf.at(i))
            adcs = np.array(adcs)

            # set relative time
            time = wf.TimeStamp() # in usec
            if (self.trigger_time == None):
                time -= 1600.
            else:
                time -= self.trigger_time
            
            if len(adcs)>=500: # is there another way to tag beam windows?
                print "beam window: ch=",pmt," len=",len(adcs)," timestamp=",time," ticks=",time/0.015625
                self.beamwindows.makeWindow( adcs, time*1000.0, 5, pmt, timepertick=15.625 )
            else:
                print "cosmic window: ch=",pmt," len=",len(adcs)," timestamp=",time," ticks=",time/0.015625
                self.cosmicwindows.makeWindow( adcs, time*1000.0, 5, pmt, timepertick=15.625 )

        return
