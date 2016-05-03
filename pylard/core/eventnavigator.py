import os,sys
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import collections


class EventNavigator(QtGui.QWidget):
    def __init__(self):
        super(EventNavigator,self).__init__()
        init_data = collections.OrderedDict()
        init_data["filename"] = "Not Set"
        init_data["event meta status"] = "loading..0%"
        init_data["EventList"] = ["None"]

        self.layout = QtGui.QVBoxLayout()

        self.eventtree = pg.DataTreeWidget(data=init_data)
        self.loadfile_button = QtGui.QPushButton()
        self.layout.addWidget( self.eventtree )
        self.layout.addWidget( self.loadfile_button )

        self.setLayout(self.layout)
