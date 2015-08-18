import numpy as np

class OpDataPlottable(object):
    def __init__(self):
        pass

    def getData(self):
        raise RuntimeError('need to overwrite this function')
        return None
        
