import os,sys
import pyqtgraph

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

# data
datafile = open('/Users/twongjirad/working/zmqtests/Event1_Run1_SubRun0.npy', 'r')
data = np.load( datafile )

## Create a GL View widget to display data
app = QtGui.QApplication([])


## Create window with ImageView widget
w = pg.GraphicsWindow(title="Basic plotting examples")

ind1_plot = w.addPlot(name="IND1", title="Induction 1")
ind1_image = pg.ImageItem()
ind1_plot.addItem( ind1_image )
ind1_image.setImage( data[0:2400,:] )

w.nextRow()
ind2_plot = w.addPlot(name="IND2", title="Induction 2")
ind2_image = pg.ImageItem()
ind2_plot.addItem( ind2_image )
ind2_image.setImage( data[2400:4800,:] )

w.nextRow()
col_plot = w.addPlot(name="COL", title="Collection")
col_image = pg.ImageItem()
col_plot.addItem( col_image )
col_image.setImage( data[4800:,:] )

ind2_plot.setYLink( ind1_plot )
col_plot.setYLink( ind1_plot )


#imv = pg.ImageView()
#w.setCentralWidget(imv)
#w.show()
#w.setWindowTitle('pyqtgraph example: ImageView')

#print data[-100:,0:50]
#print data.shape
#imv.setImage( data[0:2000,:] )

#plot = gl.GLSurfacePlotItem(z=data, shader='shaded', color=(0.5, 0.5, 1, 1), computeNormals=False, smooth=False) # chokes
#w.addItem(plot)


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
