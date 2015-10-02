import os,sys
from pylard.pylardata.opdataplottable import OpDataPlottable
from ophit import OpHitData
from rawdigitlarlite import RawDigitsOpData
import ROOT

class OpticalData( OpDataPlottable ):

    def __init__(self,inputfiles):
        super( OpticalData , self ).__init__()

        # input file name
        self.files = inputfiles

        # producers for various data-products
        self.opwf_producer    = 'pmtreadout'
        self.ophit_producer   = 'opflash'
        self.opflash_producer = 'opflash'

        # prepare a list of files for each data-product & producer
        self.opwf_files    = []
        self.ophit_files   = []
        self.opflash_files = []
        self.SplitInputFiles()
        
        # OpticalData owns instances of all data object classes
        self.opdata  = RawDigitsOpData(self.opwf_files)
        self.opdata.setProducer(self.opwf_producer)
        self.ophits  = OpHitData(self.ophit_files)
        self.ophits.setProducer(self.ophit_producer)
        self.opflash = None


    def SplitInputFiles(self):

        # name of trees expected given the producer names
        opdigit_t = 'opdigit_%s_tree'%self.opwf_producer
        ophit_t   = 'ophit_%s_tree'%self.opflash_producer
        opflash_t   = 'opflash_%s_tree'%self.opflash_producer

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
                

        print 'waveform files:'
        print self.opwf_files
        print
        print 'hit files:'
        print self.ophit_files
        print
        print 'opflash files:'
        print self.opflash_files
