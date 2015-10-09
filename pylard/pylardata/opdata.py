import os,sys
from pylard.pylardata.opdataplottable import OpDataPlottable
from ophit import OpHitData
from opdetwf import OpDetWfData
from opflash import OpFlashData
from trigger import TriggerData
import ROOT
from ROOT import larlite

class OpticalData( OpDataPlottable ):

    def __init__(self,inputfiles):
        super( OpticalData , self ).__init__()

        # input file name
        self.files = inputfiles

        # producers for various data-products
        self.opwf_producer    = 'pmtreadout'
        self.ophit_producer   = 'opflash'
        self.opflash_producer = 'opflash'
        self.trigger_producer = 'daq'

        # prepare a list of files for each data-product & producer
        self.opwf_files    = []
        self.ophit_files   = []
        self.opflash_files = []
        self.trigger_files = []
        self.SplitInputFiles()

        # call larlite manager
        self.manager = larlite.storage_manager()
        self.manager.reset()
        for f in self.opwf_files:
            self.manager.add_in_filename(f)
        for f in self.ophit_files:
            self.manager.add_in_filename(f)
        for f in self.opflash_files:
            self.manager.add_in_filename(f)
        for f in self.trigger_files:
            self.manager.add_in_filename(f)

        self.manager.set_io_mode(larlite.storage_manager.kREAD)
        self.manager.open()
        
        # OpticalData owns instances of all data object classes
        self.opdetwf = OpDetWfData(self.opwf_producer)
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
        for f in self.files:

            
            # skip if not root file
            if (f.find('.root') < 0):
                continue

            froot = ROOT.TFile(f)

            # if the file contains waveforms
            if (froot.GetListOfKeys().Contains(opdigit_t) == True):
                self.opwf_files.append(f)

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
    def getEvent(self, eventid):

        # what is the difference between the
        # requested event and the first one?
        evt_diff = eventid - self.first_event

        self.manager.go_to(evt_diff)

        self.event  = self.manager.event_id()
        self.subrun = self.manager.subrun_id()
        self.run    = self.manager.run_id()

        # save the trigger information for this event
        self.trigger.getEvent(self.manager)

        # save the trigger time for the entire event
        self.trigger_time = self.trigger.getTrigTime()
        
        self.opdetwf.getEvent(self.manager,self.trigger_time)
        
        self.ophits.getEvent(self.manager)

        self.opflash.getEvent(self.manager)

        return True
