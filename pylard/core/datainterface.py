import abc
from pylard.core.processbase import getTheProcessManager

class DataInterface(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self,name):
        self.type = "DataInterface"
        self.name = name
        getTheProcessManager.register(self.name,self)
    
    @abc.abstractmethod
    def loadFilelist( self, filelist ):
        raise RuntimeError('need to overwrite this function')

    @abc.abstractmethod
    def processEventData( self, eventdata ):
        raise RuntimeError('need to overwrite this function')

    @abc.abstractmethod
    def getEvent( self, eventindex ):
        raise RuntimeError('need to overwrite this function')

    @abc.abstractmethod
    def getNextEvent( self ):
        raise RuntimeError('need to overwrite this function')

    @abc.abstractmethod
    def getPreviousEvent( self ):
        raise RuntimeError('need to overwrite this function')

    @abc.abstractmethod
    def getNextEventIndexOnly(self):
        # instead of pylard trying to build the meta table for each data type
        # the data interfaces should probably provide a meta table, that pylard
        # tries to keep updating on a separate thread
        raise RuntimeError('need to overwrite this function')

    
