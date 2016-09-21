import os,sys
from larcv import larcv
import hashlib

class VisProcessor:
    def __init__(self):
        self.psets = {}
        self.modules = {}
        self.destination = {}
        self.products = {}
        self.active = {}
        self.searchpaths = ["pylard",""]
        self.confighash = {}

    def configure(self,config):
        m = hashlib.md5()
        m.update(config)
        h = m.hexdigest()
        doconfig = False
        if config not in self.confighash:
            self.confighash[config] = h
            doconfig = True
        else:
            if self.confighash[config] != h:
                doconfig = True
        if doconfig:
            self.psets[config] = larcv.CreatePSetFromFile(config)
            self._buildVisList()

    def _buildVisList(self):
        for cfg,pset in self.psets.items():
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
                active  = modpset.get("isactive",True)
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
                if module is not None:
                    module.configure( modpset )
                    self.modules[k] = module
                    self.destination[k] = dest
                    self.active[k] = active
                    print "configured: ",modtype,modfile,module
                else:
                    print "could not load module: from %s.%s import %s"%(d,modname,modtype),". from ",modfile
                    self.active[k] = False

    def loadModules(self):
        pass

    def execute(self, data):
        for modkey,module in self.modules.items():
            if self.active[modkey]:
                print "make vis products key=",modkey," mod=",module
                self.products[modkey] = module.visualize( data.ioman["LARLITE"], data.ioman["LARCV"], data.ioman["RAWDIGITS"] )
            else:
                print "skipping inactive vis module, key=",modkey," mod=",module
