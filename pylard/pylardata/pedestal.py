import os,sys
import numpy as np

def getpedestal( wfm, samplelength, var_threshold, verbose=False ):
    site = 0
    pastpeds = []
    while True:
        start = np.maximum(0,site*samplelength)
        end = np.minimum(len(wfm),(site+1)*samplelength)
        ave = np.mean(wfm[start:end])
        if samplelength>2:
            var = np.std(wfm[start:end])
        else:
            var = 0
        if var_threshold>var:
            if verbose:
                print "pedestal used ",site,"sites. ave=",ave," var=",var
            return ave
        else:
            pastpeds.append( var )
        if end==len(wfm):
            break
        site += 1
    if verbose:
        print "no quiet regions found!",pastpeds
    return 2048.0
