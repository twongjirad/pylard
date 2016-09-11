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

    INDEXSTATUS_NONE = -1
    INDEXSTATUS_OK = 0
    INDEXSTATUS_BUILDLING = 1

    def __init__(self):
        self.filelist = None
        self.config   = None
        self.ready    = False
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
                
            

    
