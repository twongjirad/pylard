import os,sys,time

PROFILE=False

def dev():

    sload = time.time()
    from pyqtgraph.Qt import QtGui, QtCore
    import pyqtgraph as pg
    import pylard as pylard
    from pylard.display.mainwindow import PyLArD as mainwindow
    from pylard.eventprocessor.processmanager import ProcessManager
    from pylard.eventprocessor.filemanager import FileManager
    print "Loading modules: ",time.time()-sload,"secs"

    app = QtGui.QApplication([])

    # get the pylard window
    smw = time.time()
    mw = mainwindow()
    mw.show()
    print "Loading main window: ",time.time()-smw,"secs"

    man = ProcessManager()
    man.filelist = "myfiles.txt"
    man.config   = "myconfig.cfg"
    man.initialize()
    man.ana_processman.process_event(0)

    #fman = FileManager( "myfiles.txt" )
    #fman_missing = FileManager( "myfiles_missing.txt" )

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
