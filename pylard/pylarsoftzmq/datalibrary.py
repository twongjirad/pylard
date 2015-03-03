import os,sys,time


class DataLibrary:
    def __init__(self):
        self.library = {} # dictionary storing events by ( filename, runid, eventid, dataproduct )
    def addEventData(self, eventdata ):
        # input is event data
        for product in eventdata.dataproducts:
            if eventdata.dataproducts[ product ]!=None:
                self.library[ ( eventdata.filename, eventdata.runid, eventdata.eventid, product ) ] = eventdata.dataproducts[ product ]
        return len(self.library)
    def addRequestData(self, request):
        for event in request.data:
            eventdata =request.data[event]
            for name,product in eventdata.dataproducts.items():
                if product!=None:
                    self.library[ ( eventdata.filename, eventdata.runid, eventdata.eventid, name ) ] = product
        return len(self.library)
    def removeDuplicatesFromRequest( self, request ):
        eventrm = []
        for event in request.data:
            eventdata = request.data[event]
            removelist = []
            for name,product in eventdata.dataproducts.items():
                if ( eventdata.filename, eventdata.runid, eventdata.eventid, name ) in self.library:
                    removelist.append( name )
            for item in removelist:
                del eventdata.dataproducts[item]
            if len(eventdata.dataproducts)==0:
                eventrm.append( event )
        for event in eventrm:
            del request.data[event]
        return len( request.data )
                    
