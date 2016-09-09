import os,sys

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

    def __init__(self):
        self.filelist = None
        self.config   = None
        

    def initialize(self):
        for critvar in [self.filelist,self.config]:
            if critvar is None:
                print "Could not load process manager."
                return False
            
        self.ana_processman = larlt.ana_processor()
        
