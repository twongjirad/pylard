import os,sys
import ROOT as rt
import hashlib
from filemanager import FileManager

#try:
#    from larcv import larcv as larcv
#except:
#    print "Could no load LArCV"
#    sys.exit(-1)

class ProcessManager:

    FILEMAN_STATUS_NOTREADY = -1
    FILEMAN_STATUS_READY    = 0
    FILEMAN_STATUS_ERROR    = 1
    
    ANALYZER_STATUS_NOREADY = -1
    ANALYZER_STATUS_READY   = 0
    ANALYZER_STATUS_ERROR   = 1

    def __init__(self):
        self.file_manager = None
        self.config_hash  = None
        self.ready        = False
        self.index_state = ProcessManager.INDEXSTATUS_NONE
        os.system("mkdir -p .pylardcache")
        
    def initialize(self):

        try:
            from larlite import larlite as larlt
        except:
            print "Could not load LArLite"
            sys.exit(-1)

        for critvar in [self.filelist,self.config]:
            if critvar is None:
                print "Could not load process manager."
                return False
        
        self.ana_processman = larlt.ana_processor()
        self._parse_filelist()
        self.ana_processman.set_io_mode(larlt.storage_manager.kREAD)
        self.ana_processman.set_ana_output_file("")
        
    def isConfigured(self):
        return self.ready

    def setFilelist(self,flist):
        self.filelist = flist
        
    def setConfig(self,cfg):
        self.config = cfg

    def _parse_filelist(self):
        """ this has a lot to do. we read in the files. we then build an index."""
        if os.path.exists(self.filelist):
            print "couldn't find ",self.filelist

        self.fileman = FileManager( self.filelist )
        for f in self.fileman.sorted_filelist:
            self.ana_processman.add_input_file( f )
            self.ana_processman.set_io_mode(larlt.storage_manager.kREAD)
    
    def getNextEvent(self):
        pass

    def getPrevEvent(self):
        pass

    def getEntry(self, ientry, run=None, subrun=None, event=None):
        """ main event loop driver """
        if self.loaded_larcv == False:
            try:
                from larcv import larcv as larcv
                self.loaded_larcv = True
            except:
                print "Could no load LArCV"
                sys.exit(-1)

        # setup event loop config file
        hasher = haslib.md5()
        hasher.update( self.configfile )
        #if self.config_hash is None or self.
        #hash 

        # check if storage manager iniatialized

        # check if analyzer chain is setup

        # load entry

        # run larlite analyzers

        # run display makers


    def parseAnalyzers(self):
        """ parse analyzer configuration file. """
        
        pass
        
    
            

    
