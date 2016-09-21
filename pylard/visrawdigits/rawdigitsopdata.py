import os,sys
from pylard.pylardata.opdataplottable import OpDataPlottable

class RawDigitsOpData( OpDataPlottable ):
    def __init__(self):
        super(RawDigitsOpData, self).__init__()
    def gotoEvent( self, event, run=None, subrun=None ):
        """ concrete instantiation of abc method """
        return False
    def getNextEntry(self):
        """ concrete instantiation of abc method """
        return False
    
