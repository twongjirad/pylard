import os,sys

class DataCoordinator:
    def __init__(self):
        self.filemans = {}
        self.active = {}
        self.currentEntry = None
        self.currentManager = None

    def addManager(self,name,fileman):
        self.filemans[name] = fileman
        self.active[name] = True

    def setManagerActivity(self,name,isactive):
        self.active[name] = isactive

    def getManagerEntry(self,entry,name):
        return self.filemans[name].getEntry(entry)

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
    
