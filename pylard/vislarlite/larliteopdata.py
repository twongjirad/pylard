import os,sys
import numpy as np
import pyqtgraph as pg
from pylard.pylardata.opdataplottable import OpDataPlottable
from pylard.config.pmtpos import getDetectorCenter
#from ophit import OpHitData
#from opflash import OpFlashData
#from trigger import TriggerData
import ROOT
from ROOT import larlite

class LArLiteOpticalData( OpDataPlottable ):
    """ interface class between LArLite Optical data and OpDataPlottable """
    colorcodes = { 13: (0,5,193,155), -13:(102,102,255),
                   211: (153,0,76), -211:(255,102,178),
                   11: (153,0,0), -11:(255, 102, 102 ),
                   2212: (0,153,0), 2112:(128,128,128),
                   12:(255,255,255), -12:(255,255,255),
                   14:(255,255,255), -14:(255,255,255),
                   16:(255,255,255), -16:(255,255,255) }
    
    def __init__(self):
        super( LArLiteOpticalData , self ).__init__()

    # ------------------------
    # Required methods: just dummies now
    def gotoEvent(self, eventid, run=None, subrun=None):
        """ required method from abc """
        return True

    def getNextEntry( self ):
        """ required method from abc """
        return True
    # ------------------------

    
