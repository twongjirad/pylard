import os,sys,time
from pylard.eventprocessor.visprocessor import VisProcessor


cfg = "default_larlite.cfg"
vis = VisProcessor()

vis.configure(cfg)


#sys.exit(-1)

sload = time.time()
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pylard as pylard
from pylard.display.mainwindow import PyLArD as mainwindow
from pylard.eventprocessor.processmanager import ProcessManager
from pylard.eventprocessor.visprocessor import VisProcessor
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


for n in range(3):
    s = time.time()
    # LARCV DRIVES
    data.getEntry( n, "LARCV" )
    print "Entry ",n

    # LARLITE DRIVES
    #data.getEntry(n,"LARLITE")
    print "retrival time: ",time.time()-s,"secs"

    vis.execute( data )



