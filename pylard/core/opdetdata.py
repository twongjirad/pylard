
# This is the data type data the user must fill
# user passes numpy arrays: lots of copying going on, but we live with it
# Data is stored as OpWfmPlot objects, which we use to draw
from  pylard.core.opwfmplot import OpWfmPlotVector

class OpDetData:
    def __init__(self):
        self.beamwindows = OpWfmPlotVector()
        self.cosmicwindows = OpWfmPlotVector()
        self.beamwin_info = {} # stores trigger info
        self.nbeamwinsamples = 0
        
    def addBeamWindow(self, wfm, times, slot, ch, timestamp, timepertick, color=(255,255,255,255), highlighted_color=(0,255,255,255) ):
        if len( self.beamwindows.getWindows( slot, ch ) )>=1:
            print "double beam window for (slot %d,ch %d). skip the second one."%(slot,ch)
            return
        self.beamwindows.makeWindow( wfm, times, slot, ch, 
                                     default_color=color, highlighted_color=highlighted_color,
                                     timepertick=timepertick)
        # update max number of samples
        if self.nbeamwinsamples<len(wfm):
            self.nbeamwinsamples = len(wfm)
        # update timestamp per (slot,ch)
        if (slot,ch) not in self.beamwin_info:
            self.beamwin_info[(slot,ch)] = { "tstamp":0 }
        if "earliest_tstamp" not in self.beamwin_info:
            self.beamwin_info["earliest_tstamp"] = timestamp
            self.beamwin_info["latest_tstamp"]   = timestamp+0.015625*1000
        self.beamwin_info[(slot,ch)]["tstamp"] = timestamp
        if ch<32:
            if "earliest_tstamp" not in self.beamwin_info or self.beamwin_info["earliest_tstamp"]>timestamp:
                self.beamwin_info["earliest_tstamp"] = timestamp
            tend = timestamp + (0.001*timepertick)*len( wfm ) # microseconds
            if "latest_tstamp" not in self.beamwin_info or self.beamwin_info["latest_tstamp"]<tend:
                self.beamwin_info["latest_tstamp"] = tend


    def addCosmicWindow(self, wfm, times, slot, ch, timepertick, color=(255,255,255,255), highlighted_color=(0,255,255,255) ):
        self.cosmicwindows.makeWindow( wfm, times, slot, ch, 
                                       default_color=color, highlighted_color=highlighted_color,
                                       timepertick=timepertick)
    def getNBeamWinSamples(self):
        return self.nbeamwinsamples
        

        

