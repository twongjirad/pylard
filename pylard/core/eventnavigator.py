import os,sys
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import collections


class EventNavigator(QtGui.QWidget):
    def __init__(self,processMan):
        super(EventNavigator,self).__init__()
        self.processMan = processMan # tie in to all the action

        self.data = collections.OrderedDict()
        self.data["filename"] = "Not Set"
        self.data["event meta status"] = "loading..0%"
        self.data["EventList"] = ["None"]

        self.layout = QtGui.QVBoxLayout()
        self.filedialog = QtGui.QFileDialog()

        self.eventtree = pg.DataTreeWidget(data=self.data)
        self.eventtree.setData(self.data,hideRoot=True)
        self.loadfile_button  = QtGui.QPushButton("Load Files")
        self.nextevent_button = QtGui.QPushButton("Next Event")
        self.prevevent_button = QtGui.QPushButton("Previous Event")

        self.layout.addWidget( self.eventtree )
        self.layout.addWidget( self.loadfile_button )
        self.layout.addWidget( self.nextevent_button )
        self.layout.addWidget( self.prevevent_button )

        self.setLayout(self.layout)

        self.loadfile_button.clicked.connect( self.selectedFiles )

    def selectedFiles(self):
        self.filedialog.getOpenFileName()
        filenames = self.filedialog.selectedFiles()
        files = []
        for ifile in range(0,filenames.count()):
            files.append( str(filenames.takeAt(ifile)) )
        print "select: ",str(files)
        self.data["filename"] = str(files)
        self.eventtree.setData(self.data,hideRoot=True)
        self.processMan.initDataInterface(files)

    def nextEvent(self):
        pass

    def previousEvent(self):
        pass
