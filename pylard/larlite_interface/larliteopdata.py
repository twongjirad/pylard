import os,sys
import numpy as np
import pyqtgraph as pg
from pylard.pylardata.opdataplottable import OpDataPlottable
from pylard.config.pmtpos import getDetectorCenter
from ophit import OpHitData
from opflash import OpFlashData
from trigger import TriggerData
import ROOT
from ROOT import larlite

class LArLiteOpticalData( OpDataPlottable ):
    """ interface class between LArLite Optical data and OpDataPlottable """
    colorcodes = { 13: (0,5,193,155), -13:(102,102,255),
                   211: (153,0,76), -211:(255,102,178),
                   11: (153,0,0), -11:(255, 102, 102 ),
                   2212: (0,153,0), 2112:(128,128,128),
                   12:(255,255,255), -12:(255,255,255),
                   14:(255,255,255), -14:(255,255,255),
                   16:(255,255,255), -16:(255,255,255) }
    
    def __init__(self,inputfiles):
        super( LArLiteOpticalData , self ).__init__()

        # input file name
        self.files = inputfiles

        # producers for various data-products
        #self.opwf_producer    = 'pmtreadout' # pmtreadout for data
        self.opwf_producer    = 'pmtreadout'#'opreformat' # pmtreadout for data
        self.ophit_producer   = 'opFlash'
        self.opflash_producer = 'opFlash'
        #self.trigger_producer = 'triggersim'
        self.trigger_producer = 'daq'
        self.mctrack_producer = 'mcreco'
        self.mctruth_producer = 'generator'

        # data-products that we are interested in
        self.dataproduct_list = ['opdigit','ophit','opflash','trigger','mctruth','mctrack']
        # dictionary linking producer name -> trees w/ that producer name
        self.dataproduct_dict = {}

        # prepare a list of files for each data-product & producer
        self.opwf_files    = []
        self.ophit_files   = []
        self.opflash_files = []
        self.trigger_files = []
        self.mctrack_files = []
        self.mctruth_files = []

        self.SplitInputFiles()

        # limiter for now
        self.n_pmts = 48

        # call larlite manager
        self.manager = larlite.storage_manager()
        self.manager.reset()
        self.usedfiles = []
        for filelist in [ self.opwf_files, self.ophit_files, self.opflash_files, self.trigger_files, self.mctrack_files, self.mctruth_files ]:
            for f in filelist:
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
        opdigit_t = 'opdigit_%s_tree'%(self.opwf_producer)
        ophit_t   = 'ophit_%s_tree'%(self.opflash_producer)
        opflash_t = 'opflash_%s_tree'%(self.opflash_producer)
        trigger_t = 'trigger_%s_tree'%(self.trigger_producer)
        mctrack_t = 'mctrack_%s_tree'%(self.mctrack_producer)
        mctruth_t = 'mctruth_%s_tree'%(self.mctruth_producer)

        # go through list of files and sub-split files with
        # specific data-products
        if type(self.files) is str:
            self.files = [self.files]

        for f in self.files:
            
            # skip if not root file
            if (f.find('.root') < 0):
                continue

            froot = ROOT.TFile(f)

            print froot.GetListOfKeys().Print()
            for key in froot.GetListOfKeys():
                # try and find the data-products we
                # are interested in within the key name
                for dataproduct in self.dataproduct_list:
                    # if we find it right at the beginning of the tree name
                    if (key.GetName().find(dataproduct) == 0):
                        # find the producer name
                        prod_name = key.GetName().split('_')[1]
                        print 'found producer %s for data-product %s'%(prod_name,dataproduct)
                        # add to dictionary
                        if dataproduct in self.dataproduct_dict:
                            self.dataproduct_dict[dataproduct].append(prod_name)
                        else:
                            self.dataproduct_dict[dataproduct] = [prod_name]

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

            # if the file contains mc information
            if (froot.GetListOfKeys().Contains(mctrack_t) == True):
                self.mctrack_files.append(f)

            # if the file contains mc information
            if (froot.GetListOfKeys().Contains(mctruth_t) == True):
                self.mctruth_files.append(f)
            else:
                print "no mctruth tree was loaded: ",mctruth_t

        print 'waveform files:'
        print self.opwf_files
        print
        print 'trigger files:'
        print self.trigger_files
        print
#         print 'hit files:'
#         print self.ophit_files
#         print
#         print 'opflash files:'
#         print self.opflash_files
#         print


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

        self.clearEvent()

        self.fillWaveforms()
        
        self.ophits.getEvent(self.manager)

        self.opflash.getEvent(self.manager)

        self.drawMCTrackWfmData()

        self.event  = self.manager.event_id()
        self.subrun = self.manager.subrun_id()
        self.run    = self.manager.run_id()

        return True

        

    # ------------------------
    # function to fill wf info
    def fillWaveforms( self ):

        # hack!!!
        nloops = 0
        lastpmt = -1

        print 'producer name requested: %s'%self.opwf_producer

        # load optical waveforms
        self.opdata = self.manager.get_data(larlite.data.kOpDetWaveform, str(self.opwf_producer) )

        # if we did not succeed:
        if not self.opdata:
            print 'could not find kOpDetWaveform w/ producer name %s'%self.opwf_producer
            return

        print "number of opdet waveforms: ",self.opdata.size()," trigger time=",self.trigger_time

        # loop through all waveforms and add them to beam and cosmic containers
        # self.opdata contains the larlite::ev_opdetwaveform object
        for n in xrange(self.opdata.size()):
        
            wf = self.opdata.at(n)

            pmt = wf.ChannelNumber()

            # ----------------
            # THIS IS A HACK
            if lastpmt>pmt:
                nloops += 1
            lastpmt = pmt
            if nloops in [0,3]:
                slot = 5
            else:
                slot = 6
            # ----------------

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
                time -= 1600. #?
            else:
                time -= self.trigger_time
            
            if len(adcs)>=500: # is there another way to tag beam windows?
                #print "beam window: ch=",pmt," len=",len(adcs)," timestamp=",time," ticks=",time/0.015625
                self.beamwindows.makeWindow( adcs, time*1000.0, slot, pmt, timepertick=15.625 )
            else:
                #print "cosmic window: ch=",pmt," len=",len(adcs)," timestamp=",time," ticks=",time/0.015625
                self.cosmicwindows.makeWindow( adcs, time*1000.0, slot, pmt, timepertick=15.625 )

        return

    # ---------------------
    # Get MC Track information
    def drawMCTrackWfmData( self ):
        """ draws MC info """
        self.mctrackdata = self.manager.get_data( larlite.data.kMCTrack, self.mctrack_producer )
        self.mctruthdata = self.manager.get_data( larlite.data.kMCTruth, self.mctruth_producer )

        if not self.mctrackdata:
            print 'no mctrack data'
            return

        if not self.mctruthdata:
            print 'no truth data'
            return

        mct0 = 3200.0 # us time stamp (weird quirk or data I looked at?)
        offset = (self.trigger_time-3200.0)*1000.0
        larsoft_offset = getDetectorCenter()
        print "[LArLiteOpticalData ] MC Tracks"
        print "mc tracks: ",self.mctrackdata.size()," tracks"
        print "offset=",(self.trigger_time-3200.0)*1000.0
        print "larsoft offset=",larsoft_offset

        for itrack in range(0,self.mctrackdata.size()):
            track = self.mctrackdata.at(itrack)
            nsteps = track.size()
            pid = track.PdgCode()
            first_step = track.Start();
            last_step  = track.End()
            t = first_step.T() - offset
            print "  Track ",itrack,": pdg=",track.PdgCode(),"nsteps=",nsteps," tstart=",first_step.T()," tend=",last_step.T(),
            print " start=(%.1f,%.1f,%.1f)"%(first_step.X(),first_step.Y(),first_step.Z())," E=",first_step.E(),
            print " end=(%.1f,%.1f,%1f)"%(last_step.X(),last_step.Y(),last_step.Z())," E=",last_step.E(),
            print "mct=",t
            # make waveform plot and diagram track
            color = self.colorcodes[ pid ]
            self.userwindows.makeWindow( np.linspace( 0.0, 40.0, 20 ), np.ones( 20 )*t, 100, None, default_color=color, highlighted_color=color )
            # plot track on diagram. we want downstream to go right to left, while x is out of the page. must invert y and z when we draw
            
            z = np.linspace( -(first_step.Z()-larsoft_offset[2]), -(last_step.Z()-larsoft_offset[2]), 5 )
            y = np.linspace( (first_step.Y()-larsoft_offset[1]), (last_step.Y()-larsoft_offset[1]), 5 )
            self.addUserDiagramPlotDataItem( pg.PlotDataItem( z, y, pen={"color":color,"width":5} ) )
            if abs(pid)==13: 
                # muon makes decay electron
                t2 = last_step.T() - offset
                ecolor = self.colorcodes[ 11 ]
                self.userwindows.makeWindow( np.linspace( 0.0, 40.0, 20 ), np.ones( 20 )*t2, 100, None, default_color=ecolor, highlighted_color=color )

                
        print "mc truth (",self.mctruthdata.size()," instances): ",self.mctruthdata.at(0).GetParticles().size()," particles in first instance"
        for ipart in range(0,self.mctruthdata.at(0).GetParticles().size()):
            mcpart = self.mctruthdata.at(0).GetParticles().at(ipart)
            print "particle ",mcpart.TrackId()," pdg=",mcpart.PdgCode()," ndaughters=",mcpart.Daughters().size()
