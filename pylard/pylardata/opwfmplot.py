import numpy as np


class OpWfmPlot:
    def __init__( self, wfm, times, slot, ch, default_color=(255,255,255,255), highlighted_color=(0,255,255,255), timepertick=None, x=None ):
        """
        class storing cosmic discriminator window data
        
        inputs:
        ------
        wfm: numpy array storing ADC counts
        ch: FEMCH number
        time: time of event -- ambiguous, let user decide what time means. can pass float or pass array
        default_color: vector for pyqtgraph to draw color
        highlighted_color: color used when object is clicked on
        """
        if type(times) is float and timepertick is None:
            raise ValueError( "if setting time using a float, need to set the time per tick" )
        elif type(times) is not float and len(times)!=len(wfm):
            raise ValueError( "time and wfm arrays do not match in length!" )
        self.wfm = wfm
        self.times = times
        self.timepertick = timepertick
        self.slot = slot
        self.ch = ch
        self.default_color = default_color
        self.highlighted_color = highlighted_color
        if x is None:
            self.x = x
        else:
            if len(x)!=len(self.wfm):
                raise ValueError("x array, if given, must be same length as wfm")

    def genTimeArray( self ):
        """ return numpy array of times. we do this, so the time array is only allocated when needed. """
        if type(self.times) is float:
            if self.timepertick is not None:
                return np.linspace( self.times, self.times+self.timepertick*len(self.wfm), len(self.wfm) )
        return self.times
    def getTimestamp( self ):
        """ return time stamp, which for arrays is the first entry """
        if type(self.times) is float:
            return self.times
        else:
            return self.times[0]

    def getEndstamp( self ):
        """ return time stamp at end of array, which for arrays is the last entry """
        if type(self.times) is float:
            return self.times + len(self.wfm)*self.timepertick
        else:
            return self.times[-1]

    def getX(self):
        if self.x is None:
            return self.genTimeArray()
        else:
            return self.x


class OpWfmPlotVector:
    def __init__(self):
        self.chtimes = {}    # key=(slot,channel), value=list of window start times
        self.chtend = {}     # key=(slot,channel), value=list of window end times
        self.chwindows = {}  # key=(slot,channel), value=dict of (timestamp,window)

    def getWindowsBetweenTimes( self, start, end ):
        out = []
        #print "Search : ",start,end
        for (slot,ch),times in self.chtimes.items():

            tstart = np.asarray( times ) # we use an array to have access to numpy magic
            tend   = np.asarray( self.chtend[(slot,ch)] )
            #print zip(times,self.chtend[(slot,ch)])
            # (tstart within bounds | tend within bounds |  both tstart,tend enclose bounds )
            tselect = tstart[ np.where( ( ((tstart>=start) & (tstart<=end)) | ((tend>=start) & (tend<=end)) ) | ( (tstart<=start) & (tend>=end) ) ) ] 
            #tendselect = tend[ np.where( (tend>=start) & (tend<=end)  ) ]

            for n in range(0,len(tselect)):
                out.append( self.chwindows[(slot,ch)][ tselect[n] ] )
        return out

    def getWindows( self, ch, slot ):
        windows = [] 
        if (slot,ch) in self.chwindows:
            for t,window in self.chwindows[(slot,ch)].items():
                windows.append( window )
        return windows

    def addWindow( self, cdw ):
        if (cdw.slot,cdw.ch) not in self.chtimes:
            self.chtimes[(cdw.slot,cdw.ch)] = []
            self.chtend[(cdw.slot,cdw.ch)] = []
            self.chwindows[(cdw.slot,cdw.ch)] = {}
        self.chtimes[ (cdw.slot,cdw.ch) ].append( cdw.getTimestamp() )
        self.chtend[ (cdw.slot,cdw.ch) ].append( cdw.getEndstamp() )
        self.chwindows[ (cdw.slot,cdw.ch) ][ cdw.getTimestamp() ] = cdw

    def makeWindow( self, wfm, times, slot, ch, default_color=(255,255,255,255), highlighted_color=(0,255,255,255), timepertick=None, x=None ):
        """ pass through function to OpWfmPlot constructor """
        self.addWindow( OpWfmPlot( wfm, times, slot, ch, default_color=default_color, highlighted_color=highlighted_color, timepertick=timepertick, x=x ) )
            
        
    def getNumWindows( self ):
        n = 0
        for (slot,ch),times in self.chtimes.items():
            n += len(times)
        return n

    def clear( self ):
        self.chtimes = {}    # key=(slot,channel), value=list of window start times
        self.chtend = {}     # key=(slot,channel), value=list of window end times
        self.chwindows = {}  # key=(slot,channel), value=dict of (timestamp,window)
        return
