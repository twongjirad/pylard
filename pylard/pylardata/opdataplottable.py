import numpy as np
import abc
from pylard.pylardata.opwfmplot import OpWfmPlotVector, OpWfmPlot

class OpDataPlottable(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self.beamwindows = OpWfmPlotVector()
        self.cosmicwindows = OpWfmPlotVector()
        self.userwindows = OpWfmPlotVector()

    @abc.abstractmethod    
    def gotoEvent(self, event, run=None, subrun=None ):
        """ user must implement this. it instructs that the opdata should get the data for event, run, subrun """
        raise RuntimeError('need to overwrite this function')
    
    @abc.abstractmethod
    def getNextEntry( self ):
        """ user should fill self.run, self.subrun, self.event"""
        raise RuntimeError('need to overwrite this function')

    def clearEvent( self ):
        self.beamwindows.clear()
        self.cosmicwindows.clear()
        self.userwindows.clear()
        
    def makeBeamWindow( self, wfm, time, slot, ch, default_color=(255,255,255,255), highlighted_color=(0,255,255,255), timepertick=None ):
        """ pass through to self.beamwindows.makewindow """
        self.beamwindows.makeWindow( wfm, time, slot, ch, default_color=default_color, highlighted_color=highlighted_color, timepertick=timepertick )

    def makeCosmicWindow( self, wfm, time, slot, ch, default_color=(255,255,255,255), highlighted_color=(0,255,255,255), timepertick=None ):
        """ pass through to self.cosmicwindows.makewindow """
        self.cosmicwindows.makeWindow( wfm, time, slot, ch, default_color=default_color, highlighted_color=highlighted_color, timepertick=timepertick )

    def makeUserWindow( self, wfm, time, slot, ch, default_color=(255,255,255,255), highlighted_color=(0,255,255,255), timepertick=None ):
        """ pass through to self.userwindows.makewindow """
        self.userwindows.makeWindow( wfm, time, slot, ch, default_color=default_color, highlighted_color=highlighted_color, timepertick=timepertick )

    def getWaveformPlotData( self, tstart, tend, remake_cache=False ):
        """ loop through beam, cosmic and user data to be plotted on the waveform canvas.  make plots, return."""
        beamwfm = self.beamwindows.getWindowsBetweenTimes( tstart, tend )
        cosmicwfms = self.cosmicwindows.getWindowsBetweenTimes( tstart, tend )
        # userwfms will go here as well
        return beamwfm+cosmicwfms
    
