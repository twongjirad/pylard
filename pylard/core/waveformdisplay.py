from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

class OpDetWaveformDisplay(QtGui.PlotItem):
    def __init__(self):
        super(OpDetWaveformDisplay,self).__init__(name="Waveform Plot")
        self.wf_time_range = pg.LinearRegionItem(values=[50,1500], orientation=pg.LinearRegionItem.Vertical)
        self.addItem( self.wf_time_range )

    def plot(eventdata):
        pass
