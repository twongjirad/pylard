import os,sys
import ROOT as rt
import hashlib

try:
    import larlite as larlt
except:
    print "Could not load LArLite"
    sys.exit(-1)
try:
    import larcv as larcv
except:
    print "Could no load LArCV"
    sys.exit(-1)

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
        for critvar in [self.filelist,self.config]:
            if critvar is None:
                print "Could not load process manager."
                return False
    
        self._parse_filelist()
        
        self.ana_processman = larlt.ana_processor()
        
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

        f = open( self.filelist, 'r' )
        flist = f.readlines()
        self.larlitefilelist = []
        for f in flist:
            if ".root" in f:
                self.larlitefilelist.append( f )
        
        self.ana_processman.add_input_file( f )
        self.ana_processman.set_io_mode(larlt.storage_manager.kREAD)
                
            

    
