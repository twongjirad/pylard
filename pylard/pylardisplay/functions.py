import numpy as np

def getFlashSize(PE):

    # PE scale to range from 10 -> 200
    # anything outside of this scale
    # will be given the min/max value
    # size of marker on plot to go from
    # 4 -> 30. We scale linearly.

    PEmax = 800.
    PEmin = 30.
    sizemax = 25.
    sizemin = 3.

    if (PE > PEmax): return sizemax
    if (PE < PEmin): return sizemin
    
    size = sizemin + ((PE-PEmin)/(PEmax-PEmin)) * (sizemax-sizemin)

    return size
 
