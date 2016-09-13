import os,sys,time
from larcv import larcv

PROFILE=False

def dev():

    sload = time.time()
    from pyqtgraph.Qt import QtGui, QtCore
    import pyqtgraph as pg
    import pylard as pylard
    from pylard.display.mainwindow import PyLArD as mainwindow
    from pylard.eventprocessor.processmanager import ProcessManager
    from pylard.eventprocessor.filemanager import FileManager
    from pylard.eventprocessor.datacoordinator import DataCoordinator
    print "Loading modules: ",time.time()-sload,"secs"

    app = QtGui.QApplication([])

    # get the pylard window
    smw = time.time()
    mw = mainwindow()
    mw.show()
    print "Loading main window: ",time.time()-smw,"secs"


    # setup file managers
    fman_larlite = FileManager()
    fman_larcv   = FileManager()
    fman_larcv.setFilelist( "ex_databnb_larcv.txt" )
    fman_larlite.setFilelist("ex_databnb_larlite.txt")

    # seutp datacoordinator
    data = DataCoordinator()
    data.addManager( "LARLITE", fman_larlite )
    data.addManager( "LARCV", fman_larcv )

    # Setup IOManagers/ProcessDrivers
    data.configure( "LARCV", "default_larcv.cfg" )
    data.configure( "LARLITE", "default_larlite.cfg" )

    for n in range(20):
        s = time.time()
        # LARCV DRIVES
        data.getEntry( n, "LARCV" )

        # LARLITE DRIVES
        #data.getEntry(n,"LARLITE")
        print "retrival time: ",time.time()-s,"secs"

        # GET LARCV DATA
        event_imgs = data.ioman["LARCV"].get_data( larcv.kProductImage2D, "tpc" )
        print "Entry ",n
        print "  LARCV: ",event_imgs.run(),event_imgs.subrun(),event_imgs.event()
        print "  LARLITE:",data.ioman["LARLITE"].run_id(),data.ioman["LARLITE"].subrun_id(),data.ioman["LARLITE"].event_id()

    # GET LARLITE DATA

    

    if not PROFILE:
        print "[ENTER TO EXIT]"
        raw_input()


if PROFILE:
    from cProfile import Profile
    import StringIO,pstats

    pr = Profile()
    pr.enable()
    dev()
    pr.disable()

    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()
else:
    dev()
