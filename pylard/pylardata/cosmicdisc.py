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
        self.times = []
        self.windows = {}

    def getWindowsBetweenTimes( self, start, end ):
        self.times.sort()
        t = np.asarray( self.times ) # we use an array to have access to numpy magic
        tselect = t[ np.where( (t>=start) & (t<=end) ) ]
        out = []
        for n in range(0,len(tselect)):
            out.append( self.windows[ tselect[n] ] )
        return out

    def addWindow( self, cdw ):
        self.times.append( cdw.time )
        self.windows[ cdw.time ] = cdw
            
        
    def getNumWindows( self ):
        return len(self.times)
