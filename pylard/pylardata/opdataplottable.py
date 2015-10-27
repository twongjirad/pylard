import numpy as np
import abc

class OpDataPlottable(object):
    __metaclass__ = abs.ABCMeta
    def __init__(self):
        self.beamwindows = CosmicDiscVector()
        self.cosmicwindows = CosmicDiscVector()

    @abc.abstractmethod    
    def gotoEvent(self, event, run, subrun ):
        """ user must implement this. it instructs that the opdata should get the data for event, run, subrun """
        raise RuntimeError('need to overwrite this function')
    
    @abs.abstractmethod:
    def getNextEntry( self ):
        """ user should fill self.run, self.subrun, self.event"""
        raise RuntimeError('need to overwrite this function')

    def clearEvent( self ):
        self.beamwindows.clear()
        self.cosmicwindows.clear()
        
    def getWaveformPlotData( self, tstart, tend, remake_cache=False ):
        """ loop through beam, cosmic and user data to be plotted on the waveform canvas.  make plots, return."""
        pass
