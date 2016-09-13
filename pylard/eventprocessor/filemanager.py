import os,sys
import hashlib
import time
import pickle

class FileManager:
    def __init__( self ):
        self.parsed = False
        self.loaded_larcv = False
        self.loaded_larlite = False
    def setFilelist(self,flist, use_cache=True):
        
        self.filelist = flist
        
        # get the file cache
        m = hashlib.md5()
        fin = open( flist, 'r' )
        fdata = fin.read()
        m.update(fdata)
        self.fhash = m.hexdigest()

        if use_cache and os.path.exists(".pylardcache/"+str(self.fhash)):
            print "Cache exists"
            start = time.time()
            fmanpickled = open( ".pylardcache/"+str(self.fhash)+"/fmandata.pickle", 'rb' )
            fmandata = pickle.load( fmanpickled )
            self.sorted_filelist = fmandata["sorted_filelist"]
            self.rse_dict        = fmandata["rse_dict"]
            self.entry_dict        = fmandata["entry_dict"]
            self.larlitefilelist = fmandata["larlitefilelist"]
            self.flavors         = fmandata["flavors"]
            self.flavor_def      = fmandata["flavor_def"]
            self.producers       = fmandata["producers"]
            self.datatypes       = fmandata["datatypes"]
            self.filetype        = fmandata["filetype"]
            self.parsed = True
            self.loaded_larcv = False
            self.loaded_larlite = False
            self.summary()
            elapsed = time.time()-start
            print "Loading FileManager Data with the cache: ",elapsed,"secs"
        else:
            self._parse_filelist()
            start = time.time()
            self._buildindex()
            self.summary()
            elapsed = time.time()-start
            print "Parsed files in ",elapsed,"seconds."
            if use_cache:
                os.system("mkdir -p .pylardcache/"+str(self.fhash))
                fmanpickled = open( ".pylardcache/"+str(self.fhash)+"/fmandata.pickle", 'wb' )
                data = { "sorted_filelist":self.sorted_filelist, 
                         "larlitefilelist":self.larlitefilelist,
                         "rse_dict":self.rse_dict,
                         "entry_dict":self.entry_dict,
                         "flavors":self.flavors,
                         "flavor_def":self.flavor_def,
                         "producers":self.producers,
                         "datatypes":self.datatypes,
                         "filetype":self.filetype,
                         }
                pickle.dump( data, fmanpickled )
                print "Caching FileManager Data to ",".pylardcache/"+str(self.fhash)+"/fmandata.pickle"

        self.parsed = True

        
    def _parse_filelist(self):
        """ this has a lot to do. we read in the files. we then build an index."""
        if not os.path.exists(self.filelist):
            print "couldn't find ",self.filelist
            return

        f = open( self.filelist, 'r' )
        flist = f.readlines()
        self.larlitefilelist = []
        for f in flist:
            if ".root" in f:
                self.larlitefilelist.append( f.strip() )


    def _buildindex( self ):
        """ 
        we make an list of run,subrun,event (or RSE)
        and provide a map going from RSE to entry
        """
        try:
            import ROOT as rt
        except:
            print "Could not load ROOT"
            sys.exit(-1)
        
        # sigh. this is a mess
        self.producers = []  # all producer names found in ROOT files
        self.datatypes = []  # all data types
        self.flavors = []    # flavor = hash of string listing set of trees found in a given file
        self.flavor_def = {} # map from flavor to list of tree names
        flavor_eventset = {}
        eventsets = []
        events_to_files = {}
        events_to_flavors = {}

        # this loop is going into each file in our list and
        #  - taking the list of trees in the file and making a has out of their names
        #  - this hash is used to define the 'flavor' of the file
        #  - we also make a list of events in the tree, labeling each entry with (run,subrun,event) ID
        #  - we keep track of such list of entries and group files (and flavors) with the same event list
        #  - determine filetype: LArCV or LArLite
        self.filetype = None
        for f in self.larlitefilelist:
            r = rt.TFile(f)
            nfkeys = r.GetListOfKeys().GetEntries()

            # now here we parse the type of objects in the ROOT file
            # we are looking to determine three file types supported by pylard
            #  (1) larlite (2) larcv (3) rawdigitreader
            trees = []
            for i in range(nfkeys):
                keyname = r.GetListOfKeys().At(i).GetName()
                if keyname=="larlite_id_tree":
                    found_id_tree = True
                elif "_tree" in keyname:
                    producer = keyname.split("_")[1]
                    dtype    = keyname.split("_")[0]
                    if producer not in self.producers:
                        self.producers.append( producer )
                    if dtype not in self.datatypes:
                        self.datatypes.append( dtype )
                if keyname not in trees:
                    trees.append(keyname)
            hashstr = ""
            trees.sort()
            for keyname in trees:
                hashstr += keyname +";"

            # determine filetype from type of keys we see
            is_supported_rootfile = False
            idtreename = None
            if "larlite_id_tree" in trees:
                thisfiletype = "LARLITE"
                is_supported_rootfile = True
            if "image2d" in self.datatypes:
                thisfiletype = "LARCV"
                is_supported_rootfile = True
            if "partroi" in self.datatypes:
                thisfiletype = "LARCV"
                is_supported_rootfile = True
            if not is_supported_rootfile:
                continue

            if self.filetype is not None and self.filetype!=thisfiletype:
                print "Error in parsing filelist: Cannot mix filetypes (LArCV/LArLite/RawDigitTree)"
                return
            elif self.filetype is None:
                self.filetype = thisfiletype
            
            # now we determine the idtree to use
            if self.filetype=="LARLITE":
                idtreename = "larlite_id_tree"
            elif self.filetype=="LARCV":
                if self.loaded_larcv == False:
                    s = time.time()
                    import larcv as larcv
                    print "LOADING LARCV: ",time.time()-s,"secs"
                    self.loaded_larcv = True
                for treename in trees:
                    if "image2d" in treename:
                        if idtreename is None:
                            idtreename = treename
                        else:
                            pass # we only use this if we have to
                    if "partroi" in treename:
                        idtreename = treename # we prefer to use this tree for speed
                        break

            if idtreename is None:
                print "Error: Could not setup a proper ID tree for this file"
                continue

            # now we parse the tree contents. define a flavor for it based on all the trees
            # we also get the (run,subrun,event) id for the event
            m = hashlib.md5()
            m.update(hashstr)
            flavor = m.digest()
            if flavor not in self.flavors:
                self.flavors.append( flavor )
                flavor_eventset[flavor] = []
                self.flavor_def[flavor] = hashstr
            if self.filetype=="LARLITE":
                idtree = r.Get(idtreename)
            elif self.filetype=="LARCV":
                print "LARCV indexing with ",idtreename
                idtree = r.Get(idtreename)
                
            eventset = [] # list of events
            for n in range(idtree.GetEntries()):
                idtree.GetEntry(n)
                if self.filetype=="LARLITE":
                    rse = ( idtree._run_id, idtree._subrun_id, idtree._event_id )
                elif self.filetype=="LARCV":
                    idbranchname = idtreename.replace("_tree","_branch")
                    idbranch = None
                    exec("idbranch=idtree.%s"%(idbranchname))
                    rse = ( idbranch.run(), idbranch.subrun(), idbranch.event() )
                eventset.append(rse)
                if rse not in flavor_eventset[flavor]:
                    flavor_eventset[flavor].append( rse )
                else:
                    raise ValueError( "found a repeated run/subrun/event index (%s). what?"%( str(rse) ) )
            eventset = tuple(eventset)
            if eventset not in events_to_files:
                events_to_files[eventset] = {}
                events_to_flavors[eventset] = []
                eventsets.append( eventset )
            events_to_files[eventset][flavor] = f
            events_to_flavors[eventset].append( flavor )
            del idtree
            r.Close()
        self.parsed = True

        # now we take our collection of event lists and
        #  - sort the event lists
        #  - make lists of files with the same set of events in the order of the sorted event list
        #  - for each list we also make a dictionary between (run,subrun,event) index to the entry number
        #  - we pick the list with the biggest number of events as the "official" file list
        eventsets.sort()
        flavorfiles = {}
        flavorsets = []

        flavorset_rse_dict  = {}
        flavorset_entry_dict = {}
        for eventset in eventsets:
            events_to_flavors[eventset].sort() # sort the flavors with this event-set
            flavorset = tuple( events_to_flavors[eventset] )
            if flavorset not in flavorfiles:
                flavorfiles[flavorset] = []
                flavorsets.append(flavorset)
                flavorset_rse_dict[flavorset] = {}
                flavorset_entry_dict[flavorset] = {}
            for flavor in flavorset:
                flavorfiles[flavorset].append( events_to_files[eventset][flavor] )
            for rse in eventset:
                ientry = len( flavorset_rse_dict[flavorset] )
                flavorset_rse_dict[flavorset][rse] = ientry
                flavorset_entry_dict[flavorset][ientry] = rse

        # look for largest fileset
        maxset = None
        nfiles = 0
        for fset in flavorsets:
            n = len(flavorfiles[fset])
            if n>nfiles:
                nfiles = n
                maxset = fset
        # these are the final file list and event dictionary we want
        self.sorted_filelist = flavorfiles[maxset]
        self.rse_dict        = flavorset_rse_dict[maxset]
        self.entry_dict      = flavorset_entry_dict[maxset]

            
        

    def summary(self):
        if not self.parsed:
            print "Filelists not yet parsed."

        print "Number of toal files in filelist: ",len(self.larlitefilelist)
        print "Number of files in the processed fileset=",len(self.sorted_filelist)
        print "Number of file flavors: ",len(self.flavors)
        for i,flavor in enumerate(self.flavors):
            print "Flavor %d definition: "%(i+1),self.flavor_def[flavor]
        print "All Producers Found: ",self.producers
        print "All Datatypes Found: ",self.datatypes

                
                
            

