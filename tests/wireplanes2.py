import os,sys,time
import pyqtgraph

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

from root2waveforms import rawdigits

# Create a GL View widget to display data
app = QtGui.QApplication([])

# Create window with ImageView widget
w = pg.GraphicsWindow(title="Basic plotting examples")
col_plot = w.addPlot(name="COL", title="Collection (Y)")
col_image = pg.ImageItem()
col_plot.addItem( col_image )

w.nextRow()
ind1_plot = w.addPlot(name="IND1", title="Induction 1 (U)")
ind1_image = pg.ImageItem()
ind1_plot.addItem( ind1_image )

w.nextRow()
ind2_plot = w.addPlot(name="IND2", title="Induction 2 (V)")
ind2_image = pg.ImageItem()
ind2_plot.addItem( ind2_image )

ind2_plot.setYLink( ind1_plot )
col_plot.setYLink( ind1_plot )

def plot_wireplanes( inputfile, event ):
    # data
    #datafile = open('/Users/twongjirad/working/zmqtests/Event1_Run1_SubRun0.npy', 'r')
    #data = np.load( datafile )

    digits = rawdigits( inputfile )
    digits.loadEvent(event)
    data = digits.getWaveforms()

    start = time.time()

    col_image.setImage( data[0:2400,:] )
    
    ind2_image.setImage( data[2400:4800,:] )

    ind1_image.setImage( data[4800:,:] )
    
    print "plotted: ",time.time()-start," secs"
    return digits,data
    
if __name__ == '__main__':
    import sys
    inputfile = "swiz/workdir/raw_digits.root"
    event = 12

    # usage: wireplanes2.py <input file> <event>
    if len(sys.argv)>=2:
        inputfile = sys.argv[1]
    if len(sys.argv)>=3:
        event = int( sys.argv[2] )

    print "nput file: ",inputfile
    print "event: ",event

    digits,data = plot_wireplanes( inputfile, event )

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
