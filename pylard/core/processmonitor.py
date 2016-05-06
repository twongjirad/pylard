import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

class ProcessMonitor(QtGui.QWidget):
    def __init__(self,processMan):
        super(ProcessMonitor,self).__init__()
        self.processMan = processMan
        self.layout = QtGui.QGridLayout()
        self.process_tree = pg.TreeWidget()
        self.process_clearbutton = QtGui.QPushButton("Clear")
        self.process_menu = QtGui.QComboBox()

        self.layout.addWidget( self.process_tree, 0, 0, 3, 1 )
        self.layout.addWidget( self.process_menu, 3, 0, 1, 1 )
        self.layout.addWidget( self.process_clearbutton, 4, 0, 1, 1 )

        self.setLayout( self.layout )

    def initDataInterface(self,files):
        pass