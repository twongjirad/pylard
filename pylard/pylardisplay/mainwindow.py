import sys
from pyqtgraph.Qt import QtCore, QtGui
from pylard.pylardisplay.detectordisplay import DetectorDisplay
# The different windows

#class ExampleLoader(QtGui.QMainWindow):
#    def __init__(self):
#        QtGui.QMainWindow.__init__(self)
#        #self.ui = Ui_Form()
#        self.cw = QtGui.QWidget()
#        self.setCentralWidget(self.cw)
#        #self.ui.setupUi(self.cw)

class mainwindow( QtGui.QMainWindow ):
    def __init__(self, daefile, use_cache=True, cache_dir="./cache"):
        super( mainwindow, self ).__init__()
        self.cw = QtGui.QWidget()
        self.setCentralWidget(self.cw)
        self.resize(1000,500)
        self.layout = QtGui.QHBoxLayout()
        self.cw.setLayout( self.layout )

        # detector
        self.detector = DetectorDisplay(use_cache=use_cache, cache_dir=cache_dir)
        self.detector.load_geometry( daefile ) # To do: Fix this hard-coding
        self.layout.addWidget( self.detector.solidswidget )
        #self.layout.addWidget( self.detector )
        self.detector.show()

        self.show()

    def initUI(self):
        pass


    
