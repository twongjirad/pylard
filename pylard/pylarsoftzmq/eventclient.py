import os,sys,time
import zmq, zmq.ssh
import bz2
import lz4
import numpy as np
import cStringIO
import threading

class DataProducts:
    def __init__(self, name, nchunks, eventid ):
        self.name = name
        self.eventid = eventid
        self.nchunks = nchunks
        self.chunks = {}
        self.array = None
        self.complete = False
        self.compression = None
        self.server_name = None
    def getarray(self):
        if self.array==None:
            # reassmble data
            data_stream = ""
            for n in xrange(0,nchunks):
                if self.compression==None:
                    data_stream += event_chunks[n]
                elif self.compression=="lz":
                    data_stream += lz4.loads( event_chunks[n] )
                else:
                    raise RuntimeError('unrecognized compression option "%s"'%(self.compression))
            # convert into numpy array
            data = cStringIO.StringIO( data_stream )
            self.array = np.load( data )
        return self.array
    def getPercentComplete(self):
        return float(len(self.chunks))/float(self.nchunks)*100.0        

class EventData:
    def __init__( self, filename, runid, eventid, dataproductslist=None ):
        self.filename = filename
        self.runid = runid
        self.eventid = eventid
        self.fulfilled = False
        self.dataproducts = {}
        if dataproductslist!=None:
            for products in dataproductslist:
                self.dataproducts[products] = None
    def update(self):
        self.fulfilled = True
        for name,product in self.dataproducts.items():
            if product==None or not product.complete:
                self.fulfilled = False
                print name," is not complete"
                break
            else:
                print name," is complete"
        return self.fulfilled
    def isFilled(self):
        return self.update()


class Request:
    def __init__( self, filename, first_run, first_event, nevents, dataproductlist ):
        self.filename = filename
        self.first_run = first_run
        self.first_event = first_event
        self.nevents = nevents
        self.dataproductlist = dataproductlist
        self.data = {}
        self.fulfilled = False
        self.finish_thread = False
        for event in xrange(self.first_event,self.first_event+self.nevents):
            self.data[ ( self.first_run, event ) ] = EventData( self.filename, self.first_run, self.first_event, self.dataproductlist )
    def numberStored(self):
        return len(self.event_data)
    def update(self):
        self.fulfilled = True
        for event in self.data:
            if not self.data[event].isFilled():
                self.fulfilled = False
                print event," not finished"
                break
            else:
                print event," finished"
    def setfulfilled(self):
        mylock = threading.Lock()
        mylock.acquire()
        self.fulfilled = True
        mylock.release()
    def getfulfilled(self):
        self.update()
        return self.fulfilled
        

def request_event( socket, request ):
    # initialize request
    request_file = b"%s"%(request.filename)
    request_firstrun = b"%d"%(request.first_run)
    request_firstevent = b"%d"%(request.first_event)
    request_nevents = b"%d"%(request.nevents)
    product_set = []
    for event,eventdata in request.data.items():
        for name,product in eventdata.dataproducts.items():
            if name not in product_set:
                product_set.append( name )
    str_request_products=""
    for product in product_set:
        str_request_products += product
        if product!=product_set[-1]:
            str_request_products += ":"
    print str_request_products
    request_products = b"%s"%(str_request_products)
    try:
        socket.send_multipart( [str(request.filename).strip(), str(request.first_run), str(request.first_event), str(request.nevents), str_request_products] )
        reply = socket.recv_multipart()
    except:
        print "trouble communicating with socket"
        return None
    if reply[0]=="LARSOFT_LAUNCHED":
        print "Request received. Retreiving data..."
    else:
        print "Nothing received"
        return None

    # time transfer
    tstart = time.time()

    # loop over events, dataproducts in request
    while not request.getfulfilled():
        # ask for event data product
        socket.send_multipart([b"REQUEST_EVENT",b"%d:%d"%(request.first_run, request.first_event)])
        msg = socket.recv_multipart()
        if msg[0]=="REQUEST_COMPLETE":
            print "Finished sending ",eventid,name
            break
        elif msg[0]=="WAITING_FOR_LARSOFT":
            time.sleep(5)
            continue
        elif "EVENTINFO:" in msg[0]:
            print "Server wants to send an event.: ",msg[0]
            # get event info 
            event_name = msg[0].split(":")[1]
            event_runid = int(msg[0].split(":")[2])
            event_eventid = int(msg[0].split(":")[3])
            event_product = msg[0].split(":")[4]
            compression = msg[0].split(":")[5]
            nchunks = int(msg[0].split(":")[6])
            event_data = request.data[ (event_runid, event_eventid ) ]

            # create event data product
            data = DataProducts( event_product, nchunks, event_eventid )
            event_data.dataproducts[ event_product ] = data
            data.server_name = event_name
            data.compression = compression

            # Get data product chunks
            while len(data.chunks)<nchunks:
                for n in xrange(0,nchunks):
                    if n in data.chunks:
                        continue
                    chunk_request = "CHUNK%d:%s:%s:%d"%(n,data.server_name,event_product,data.eventid)
                    print "asking for chunk: ",chunk_request
                    socket.send_multipart([chunk_request])
                    reply = socket.recv_multipart()
                    print "reply: ",reply[0]
                    chunkid = int(reply[0].split(":")[0][len("CHUNK"):])
                    data.chunks[chunkid] = lz4.loads( reply[1] ) # decompress
                print "Chunks after loop: ",len(data.chunks)
            # indicate data product is complete
            data.complete = True
            complete = True
        event_data.update()
        # end of while not complete loop
        # tell server event is done
    print "REQUEST FINISHED"
    socket.send_multipart(["COMPLETE:%s"%(str(request.filename).strip())])
    ok = socket.recv_multipart()
    print "event transfer time: ",time.time()-tstart," seconds."
    tstart = time.time()
    request.finish_thread = True
    return

def dummy_request( socket, request ):
    print "dummy request sleeping for 10 seconds. ",id(request)
    n = 0
    lock = threading.Lock()
    while n<10: 
        time.sleep(0.1)
        for event in xrange(request.first_event, request.first_event+request.nevents):
            eventdata = request.data[ (request.first_run, event ) ]
            for name,product in eventdata.dataproducts.items():
                lock.acquire()
                if product==None:
                    eventdata.dataproducts[name] = DataProducts( name, 10 )
                eventdata.dataproducts[name].chunks[n] = 1.0
                if len( eventdata.dataproducts[name].chunks ) == eventdata.dataproducts[name].nchunks:
                    eventdata.dataproducts[name].complete = True
                print "dummy chunk update: ",len( eventdata.dataproducts[name].chunks ), eventdata.dataproducts[name].complete
                lock.release()
            eventdata.update()
        request.update()
        n += 1
        print "dummy update. request complete=",request.getfulfilled()
    request.setfulfilled()
    request.finish_thread = True
    return

class EventClient:
    def __init__( self, server_list=["uboonegpvm02.fnal.gov:5555"],sshusername=None, timeout=10, offline_test=False ):
        self.ssh_username = sshusername
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.set( zmq.RATE, 1000 )
        self.servers = []
        self.timeout = timeout
        self.requests = [] # list containing (Request, Thread) pairs
        self.offline_test = offline_test
        for server in server_list:
            if offline_test:
                continue # skip for offline test
            self.connectSocket( server, timeout=timeout )
    def connectSocket( self, server, timeout=10 ):
        try:
            portnum = int( server.split(":")[1] )
        except:
            print "could not open server: ",server
            return

        if self.ssh_username:
            sshuser = self.ssh_username+"@"+server.split(":")[0]
            status = zmq.ssh.tunnel_connection( self.socket, "tcp://"+server, sshuser, timeout=timeout )
            print status
            self.servers.append( server )
        else:
            (url,tunnel) = zmq.connect( self.socket, "tcp://"+server )
            self.servers.append( server )
    def getEventInfo( self, filename, first_run, first_event, nevents ):
        request = Request(  filename, first_run, first_event, nevents, ["RawDigits"] )
        thread = threading.Thread( target=request_event, args=(self.socket, request ), daemon=True )
        thread.start()
        self.requests.append( (requests,thread) )
        
    def processRequest( self, request ):
        if self.offline_test:
            thread = threading.Thread( target=dummy_request, args=(self.socket, request ) )
        else:
            thread = threading.Thread( target=request_event, args=(self.socket, request ) )
        thread.start()
        

if __name__=="__main__":
    client = EventClient( sshusername="tmw" )
    request = Request( "/uboone/data/users/tmw/chromasim_data/single_gen_uboone.root", 
                       1, 1, 1, 
                       ["OpticalRawDigits"] )
    client.processRequest( request )
