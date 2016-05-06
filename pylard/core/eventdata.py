import os,sys
from pylard.core.eventindex import EventIndex
from pylard.core.opdetdata import OpDetData
from pylard.core.tpcdata import TPCData

class EventData:
    def __init__( self, run, subrun, event, subevent=0 ):
        # remember: classes must initialize complete
        self.index   = EventIndex( run, subrun, event, subevent )
        self.opdata  = OpDetData()
        self.tpcdata = TPCData()

        
