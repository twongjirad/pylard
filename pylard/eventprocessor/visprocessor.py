import os,sys
from larcv import larcv


class VisProcessor:
    def __init__(self):
        self.psets = []
        self.modules = {}
        self.destination = {}
        self.products = {}
        self.searchpaths = ["pylard",""]

    def configure(self,config):
        self.psets.append( larcv.CreatePSetFromFile(config) )
        self._buildVisList()
        
    def _buildVisList(self):
        for pset in self.psets:
            if not pset.contains_pset("VisProcessor"):
                continue
            vispset = pset.get_pset("VisProcessor")
            keys = vispset.pset_keys()
            for k in keys:
                modpset = vispset.get_pset(k)
                # get module type
                modtype = modpset.get("module_type")
                modfile = modpset.get("module_file")
                dest    = modpset.get("destination")
                modname = modfile.replace("/",".")
                module = None
                for d in self.searchpaths:
                    try:
                        exec("from %s.%s import %s"%(d,modname,modtype))
                        exec("module=%s()"%(modtype))
                        foundmod = True
                    except:
                        foundmod = False
                    if foundmod: break
                module.configure( modpset )
                self.modules[k] = module
                self.destination[k] = dest
                print "configured: ",modtype,modfile,module

    def loadModules(self):
        pass

    def execute(self, data):
        for modkey,module in self.modules.items():
            print "make vis products key=",modkey," mod=",module
            self.products[modkey] = module.visualize( data.ioman["LARLITE"], data.ioman["LARCV"] )
