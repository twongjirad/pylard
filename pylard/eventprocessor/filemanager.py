import os,sys
import ROOT as rt
import hashlib
import time
import pickle

class FileManager:
    def __init__( self, flist, use_cache=True ):
        self.parsed = False
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
            self.larlitefilelist = fmandata["larlitefilelist"]
            self.flavors         = fmandata["flavors"]
            self.flavor_def      = fmandata["flavor_def"]
            self.producers       = fmandata["producers"]
            self.datatypes       = fmandata["datatypes"]
            self.parsed = True
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
                         "flavors":self.flavors,
                         "flavor_def":self.flavor_def,
                         "producers":self.producers,
                         "datatypes":self.datatypes }
                pickle.dump( data, fmanpickled )
                print "Caching FileManager Data to ",".pylardcache/"+str(self.fhash)+"/fmandata.pickle"


        
        
    def _parse_filelist(self):
        """ this has a lot to do. we read in the files. we then build an index."""
        if os.path.exists(self.filelist):
            print "couldn't find ",self.filelist

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
        for f in self.larlitefilelist:
            r = rt.TFile(f)
            nfkeys = r.GetListOfKeys().GetEntries()
            found_id_tree = False
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

            if not found_id_tree:
                continue
            m = hashlib.md5()
            m.update(hashstr)
            flavor = m.digest()
            if flavor not in self.flavors:
                self.flavors.append( flavor )
                flavor_eventset[flavor] = []
                self.flavor_def[flavor] = hashstr
            idtree = r.Get("larlite_id_tree")
            eventset = [] # list of events
            for n in range(idtree.GetEntries()):
                idtree.GetEntry(n)
                rse = ( idtree._run_id, idtree._subrun_id, idtree._event_id )
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
        for eventset in eventsets:
            events_to_flavors[eventset].sort() # sort the flavors with this event-set
            flavorset = tuple( events_to_flavors[eventset] )
            if flavorset not in flavorfiles:
                flavorfiles[flavorset] = []
                flavorsets.append(flavorset)
                flavorset_rse_dict[flavorset] = {}
            for flavor in flavorset:
                flavorfiles[flavorset].append( events_to_files[eventset][flavor] )
            for rse in eventset:
                ientry = len( flavorset_rse_dict[flavorset] )+1
                flavorset_rse_dict[flavorset][rse] = ientry

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

                
                
            

