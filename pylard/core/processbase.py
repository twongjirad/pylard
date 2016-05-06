import abc
from pylard.core.processmanager import getTheProcessManager

class ProcessBase(object):
    __metaclass__ = abc.ABCMeta
    def __init__(name,self):
        self.type = "Process"
        self.name = name
        getTheProcessManager.register(self.name,self)
    
    @abc.abstractmethod
    def processEventData( EventData ):
        raise RuntimeError('need to overwrite this function')
