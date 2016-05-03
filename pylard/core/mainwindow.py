import sys
from pyqtgraph.Qt import QtCore, QtGui
from pylard.core.tpcwindow import TPCWindow
from pylard.core.eventnavigator import EventNavigator
from pylard.core.processmonitor import ProcessMonitor
from pylard.core.opdetwindow import OpDetWindow

class PyLArD( QtGui.QMainWindow ):
    def __init__(self, config_yaml="", use_cache=True, cache_dir="./cache"):
        super( PyLArD, self ).__init__()
        self.resize(1400,800)
        self.cw = QtGui.QWidget()
        self.setCentralWidget(self.cw)

        self.tpcview = TPCWindow()
        self.opdetview = OpDetWindow()
        self.viewstack = QtGui.QStackedWidget()
        self.viewstack.addWidget( self.tpcview )
        self.viewstack.addWidget( self.opdetview )

        self.evnav   = EventNavigator()
        self.procman = ProcessMonitor()

        self.button_layout = QtGui.QHBoxLayout()
        self.show_pmt_or_tpc = QtGui.QGroupBox()
        self.show_pmt_or_tpc_layout = QtGui.QHBoxLayout()
        self.show_pmt = QtGui.QRadioButton("pmt display")
        self.show_tpc = QtGui.QRadioButton("tpc display")
        self.show_pmt_or_tpc_layout.addWidget( self.show_tpc )
        self.show_pmt_or_tpc_layout.addWidget( self.show_pmt )
        self.show_tpc.setChecked(True)
        self.show_pmt_or_tpc.setLayout( self.show_pmt_or_tpc_layout )
        self.show_pmt.toggled.connect( self._changeview )
        self.show_tpc.toggled.connect( self._changeview )

        self.layout = None
        self._buildLayout()
        self.show()

    def initUI(self):
        pass

    def _buildLayout(self):

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget( self.viewstack, 0, 0, 1, 1 )
        self.layout.addWidget( self.evnav, 0, 1, 1, 1 )
        self.layout.addWidget( self.procman, 0, 2, 1, 1 )
        self.layout.addWidget( self.procman, 0, 2, 1, 1 )
        self.layout.addWidget( self.show_pmt_or_tpc, 1, 0, 1, 1 )
        self.cw.setLayout( self.layout )

    def _changeview(self):
        if self.show_pmt.isChecked():
            self.viewstack.setCurrentWidget( self.opdetview )
        else:
            self.viewstack.setCurrentWidget( self.tpcview )

    
    
