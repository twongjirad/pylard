import os,sys
import zmq, zmq.ssh
import bz2
import lz4
import numpy as np
import cStringIO
import threading

class DataProducts:
    def __init__(self, name, nchunks ):
        self.name = name
        self.nchunks = nchunks
        self.chunks = {}
        self.array = None
    def getarray(self):
        if self.array==None:
            data_stream = ""
            for n in xrange(0,nchunks):
                data_stream += event_chunks[n]
                data = cStringIO.StringIO( data_stream )
            self.array = np.load( data )
        return self.array
        

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

class Request:
    def __init__( self, filename, first_run, first_event, nevents, dataproductlist ):
        self.filename = filename
        self.first_run = first_run
        self.first_event = first_event
        self.nevents = nevents
        self.dataproductlist = dataproductlist
        self.data = {}
        self.fulfilled = False
        for event in xrange(self.first_event,self.first_event+self.nevents):
            self.data[ ( self.first_run, event ) ] = EventData( self.filename, self.first_run, self.first_event, self.dataproductlist )
    def numberStored(self):
        return len(self.event_data)

def request_event( socket, request ):
    # initialize request
    request_file = b"%s"%(request.filename)
    request_firstrun = b"%d"%(request.first_run)
    request_firstevent = b"%d"%(request.first_event)
    request_nevents = b"%d"%(request.nevents)
    socket.send_multipart([request_file, request_firstrun, request_firstevent, request_nevents])
    reply = socket.recv_multipart()
    if reply[0]=="LARSOFT_LAUNCHED":
        print "Request received. Retreiving data..."
    else:
        print "Nothing received"
        return None

    # get event data
    tstart = time.time()
    while request.numberStored()<nevents:
        socket.send_multipart([b"REQUEST_EVENT"])
        msg = socket.recv_multipart()
        if msg[0]=="DONE":
            print "We're done."
            break
        elif msg[0]=="EMPTY_QUEUE":
            time.sleep(1)
            continue
        elif "EVENTINFO:" in msg[0]:
            print "Server wants to send an event.: ",msg[0]
            # get event in chunks
            event_name = msg[0].split(":")[1]
            event_runid = msg[0].split(":")[2]
            event_eventid = msg[0].split(":")[3]
            compression = msg[0].split(":")[4]
            event_data = EventData( request.filename, event_runid, event_eventid )

            # get event data products
            nchunks = int(msg[0].split(":")[5])
            data = dataproduct( "RawDigits", nchunks )
            while len(data.chunks)<nchunks:
                for n in xrange(0,nchunks):
                    if n in event_chunks:
                        continue
                    request = "CHUNK%d:%s"%(n,event_name)
                    #print "request: ",request
                    socket.send_multipart([request])
                    reply = socket.recv_multipart()
                    #print "reply: ",reply[0]
                    chunkid = int(reply[0].split(":")[0][len("CHUNK"):])
                    data.chunks[chunkid] = lz4.loads( reply[1] ) # decompress
                print "Chunks after loop: ",len(data.chunks)
            event_data.dataproducts["RawDigits"] = data

            # tell server event is done
            socket.send_multipart(["COMPLETE:"+event_name])
            ok = socket.recv_multipart()
            print "event transfer time: ",time.time()-tstart," seconds."
            
            # put event data into request
            request.data[ (event_runid, event_eventid ) ] = event_data
            tstart = time.time()
    return

class EventClient:
    def __init__( self, server_list=["uboonegpvm02.fnal.gov:5555"],sshusername=None, timeout=10, offline_test=False ):
        self.ssh_username = sshusername
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.servers = []
        self.timeout = timeout
        self.requests = []
        self.threads = []
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
            (url,tunnel) = zmq.ssh.tunnel_connection( self.socket, "tcp://"+server, sshuser, timeout=timeout )
            self.servers.append( server )
        else:
            (url,tunnel) = zmq.connect( self.socket, "tcp://"+server )
            self.servers.append( server )
    def getEventInfo( self, filename, first_run, first_event, nevents ):
        request = Request(  filename, first_run, first_event, nevents, ["RawDigits"] )
        thread = threading.Thread( target=request_event, args=(self.socket, request ) )
        thread.start()
        self.requests.append( requests )
        self.threads.append( thread )
        
        


