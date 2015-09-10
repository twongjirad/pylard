import numpy as np


class CosmicDiscWindow:
    def __init__( self, wfm, slot, ch, time, color=None ):
        """
        class storing cosmic discriminator window data
        
        inputs:
        ------
        wfm: numpy array storing ADC counts
        ch: FEMCH number
        time: time of event -- ambiguous, let user decide what time means
        sample: tick
        color: vector for pyqtgraph to draw color
        """
        self.wfm = wfm
        self.slot = slot
        self.ch = ch
        self.time = time
        if color is not None:
            self.color = color
        else:
            self.color = (255,255,255,255)


class CosmicDiscVector:
    def __init__(self):
        self.chtimes = {}
        self.chwindows = {}

    def getWindowsBetweenTimes( self, start, end ):
        out = []
        for ch,times in self.chtimes.items():
            times.sort()
            t = np.asarray( times ) # we use an array to have access to numpy magic
            tselect = t[ np.where( (t>=start) & (t<=end) ) ]

            for n in range(0,len(tselect)):
                out.append( self.chwindows[ch][ tselect[n] ] )
        return out

    def addWindow( self, cdw ):
        if cdw.ch not in self.chtimes:
            self.chtimes[cdw.ch] = []
            self.chwindows[cdw.ch] = {}
        self.chtimes[cdw.ch].append( cdw.time )
        self.chwindows[ cdw.ch ][ cdw.time ] = cdw
            
        
    def getNumWindows( self ):
        n = 0
        for ch,times in self.chtimes.items():
            n += len(times)
        return n
