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
    fman_larlite.setFilelist( "ex_databnb_larlite.txt" )

    # seutp datacoordinator
    data = DataCoordinator()
    data.addManager( "LARLITE", fman_larlite )
    data.addManager( "LARCV", fman_larcv )

    data.configure( "LARCV", "default_larcv.cfg" )

    data.getEntry( 0, "LARCV" )

    event_imgs = data.processdrivers["LARCV"].io().get_data( larcv.kProductImage2D, "tpc" )
    print event_imgs

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
