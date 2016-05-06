from pyqtgraph.Qt import QtCore, QtGui

# Role of this class to be the bridge between the GUI and
#  the data. It also manages the processes that operate on the data.


class ProcessManager:
    def __init__(self):
        self.registered_processes = {}
        
    def registerProcess( name, process_class ):
        self.registered_processes[name] = process_class
        print "Registered Process: ",name," of Type: ",process_class.type()


# Singleton structure. This will probably be my undoing
_gProcessMan = ProcessManager()
def getTheProcessManager():
    return _gProcessMan
