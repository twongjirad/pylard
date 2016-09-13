import os,sys
import hashlib
import time

class DataCoordinator:
    """ this handles the process drivers for the event loop"""
    def __init__(self):
        # variables for different filetypes (probably should be a class/struct)
        self.filemans = {}
        self.active = {}
        self.ioman = {}
        self.processdrivers = {}
        self.configs = {}
        self.confighash = {}

        self.currentEntry = None
        self.currentManager = None

    def addManager(self,name,fileman):
        self.filemans[name] = fileman
        self.active[name] = False

    def setManagerActivity(self,name,isactive):
        self.active[name] = isactive

    def getManagerEntry(self,entry,name):
        if name=="LARCV":
            ok = self.processdrivers[name].process_entry(entry)
        elif name=="LARLITE":
            ok = self.ioman[name].go_to(entry)
        else:
            ok = True
        return ok

    def getEntry(self,entry,drivingmanager):
        if drivingmanager not in self.filemans:
            return
        self.currentManager = drivingmanager

        if entry not in self.filemans[drivingmanager].entry_dict:
            return

        rse = self.filemans[drivingmanager].entry_dict[entry]

        ok = False
        for name,isactive in self.active.items():
            if isactive and name in self.filemans and rse in self.filemans[name].rse_dict: 
                e = self.filemans[name].rse_dict[rse]
                #print "  driving rse=",rse," ",name," entry=",e
                manok = self.getManagerEntry( e, name )
                if not ok and manok: # want to know at least one was ok
                    ok = True
        if ok:
            self.currentEntry = entry
        return ok

    def nextEntry(self):
        nextentry = self.currentEntry+1
        self.getEntry(nextentry,self.currentManager)

    def prevEntry(self):
        preventry = self.currentEntry-1
        self.getEntry(preventry,self.currentManager)

    
    def configure(self,name,config):
        
        # the config hash: check if we've already configured the processor with the same exact file
        m = hashlib.md5()
        fin = open(config,'r')
        cfg = fin.read()
        m.update(cfg)
        current = m.hexdigest()
        if name in self.confighash and self.confighash[name]==current:
            return # no update to config, dont update processor

        if name=="LARLITE":
            """ for larlite, we will open our own storage manager and manager the process analyzers ourselves """
            from larlite import larlite
            from ROOT import fcllite
            # the iomanager
            if name not in self.confighash:
                # open new file
                io = larlite.storage_manager( larlite.storage_manager.kREAD )
                for fname in self.filemans[name].sorted_filelist:
                    io.add_in_filename( fname )
                io.open()
                self.ioman[name] = io
                self.setManagerActivity(name,True)
            # set the config
            self.configs[name] = fcllite.ConfigManager( config )

        elif name=="LARCV":
            """ needs iomanager configuration from PSET"""
            s = time.time()
            from larcv import larcv
            print "Loading LArCV: ",time.time()-s,"secs"
            
            # parse pset
            print "New or updated configuration provided."
            pset = larcv.CreatePSetFromFile(config)
            if name in self.confighash:
                # existing processosr already working, reload
                proc = self.processdrivers[name]
            else:
                proc = larcv.ProcessDriver("ProcessDriver")
                self.processdrivers[name] = proc
                self.ioman[name] = proc.io()
            self.configs[name] = pset.get_pset("ProcessDriver")
            # reconfigure
            proc.configure( self.configs[name]  )
            from ROOT import std
            if name not in self.confighash:
                v = std.vector("string")()
                for f in self.filemans[name].sorted_filelist:
                    v.push_back(f)
                proc.override_input_file( v )
                proc.initialize()
            self.confighash[name] = current
            self.setManagerActivity(name,True)

                
        

