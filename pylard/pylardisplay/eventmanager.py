import os,sys, time
from pyqtgraph import QtCore, QtGui
from pylard.pylarsoftzmq.eventclient import Request, EventClient
from pylard.pylarsoftzmq.datalibrary import DataLibrary

class RequestMonitor(QtCore.QObject):
    # This class is responsible for monitoring the progress
    # of a ZMQ request and sending the status to the eventtree widget.
    # it will be launched on a thread and stops once a request 
    # has been fulfilled.
    finished = QtCore.pyqtSignal()
    monitorupdate = QtCore.pyqtSignal()

    def __init__(self, request, zmqclient, treewidget):
        super( RequestMonitor, self ).__init__()
        self.request = request
        self.zmqclient = zmqclient
        self.treewidget = treewidget
        self.isFinished = False

    @QtCore.pyqtSlot()
    def monitorRequestStatus(self):
        requestfinished = False
        while not requestfinished:
            print "checking request status", self.request.fulfilled, id(self.request)
            #requestfinished, completioninfo  = self.zmqclient.getRequestStatus( self.request )
            #self.updateTreeWidget( self.request )
            requestfinished = self.request.fulfilled
            self.monitorupdate.emit()
            time.sleep(1)

        self.isFinished = True
        self.finished.emit()

class EventManager( QtGui.QWidget ):
    def __init__(self):
        super( EventManager, self ).__init__()
        self.setupUI()
        self.zmqclient = EventClient(sshusername="tmw",offline_test=True) # ZMQ client for requestig LArSoft data
        self.requests = [] # list containing ( Request, RequestMonitor )
        self.library = DataLibrary()
        # setup eventtree
        column = 0
        self.eventTree.setColumnCount(2)
        self.eventTree.setColumnWidth(0,200)
        self.eventTree.setColumnWidth(1,100)
        self.et_loaded = QtGui.QTreeWidgetItem( self.eventTree.invisibleRootItem(), ["Loaded from ZMQ client"] )
        self.et_loaded.setData(column, QtCore.Qt.UserRole, "filename")
        self.et_loaded.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
        self.et_loaded.setExpanded (True)
        self.et_cached = QtGui.QTreeWidgetItem( self.eventTree.invisibleRootItem(), ["In Cache"] )
        self.et_cached.setData(column, QtCore.Qt.UserRole, "filename")
        self.et_fileitems = {}  # dictionary to store event tree items by filename
        self.et_eventitems = {} # dictionary of event tree items for event data. key: (filename,runid,eventid)
        self.et_dataproducts = {} # dictionary of event tree items for event data. key: (filename,runid,eventid). stores dictionary of data products and their treeitems


    def submitRequest(self):
        # gather nature of request
        productlist = []
        for name in self.data_checkboxes:
            #print name,": ",self.data_checkboxes[name].isChecked()
            if self.data_checkboxes[name].isChecked():
                productlist.append( name )
        request = Request( self.filename_input.text(), 
                           int(self.input_first_run.text()),
                           int(self.input_first_event.text()),
                           int(self.input_nevents.text()),
                           productlist )
        # check if we already have it
        if not self.input_reload.isChecked():
            nnewproducts = self.library.removeDuplicatesFromRequest( request )
            if nnewproducts==0:
                return
    
        # register in tree
        self.addRequestToTreeWidget( request )

        # send it over to pylarsoftzmq
        self.zmqclient.processRequest( request )

        # monitor request
        reqmon = RequestMonitor( request, self.zmqclient, self.eventTree )
        reqmon_thread = QtCore.QThread()
        reqmon.moveToThread( reqmon_thread )
        reqmon_thread.started.connect( reqmon.monitorRequestStatus )
        reqmon.finished.connect( reqmon_thread.quit )
        reqmon.finished.connect( self.finishRequest )
        reqmon.monitorupdate.connect( lambda: self.updateFromMonitor( request ) )
        reqmon_thread.start()

        # add it to our request list
        self.requests.append( (request, reqmon, reqmon_thread ) )
        
    def finishRequest(self):
        # get data. remove requests from queue
        for (request, reqmon, reqthread) in self.requests:
            if reqmon.isFinished:
                self.library.addRequestData( request )
                self.requests.remove( (request, reqmon, reqthread) )
                print "Event request finished. Remaning: ",len(self.requests)

    def addRequestToTreeWidget( self, request ):
        # break down by file and event
        filename = request.filename
        column = 0
        if filename not in self.et_fileitems:
            self.et_fileitems[filename] = QtGui.QTreeWidgetItem( self.et_loaded, [filename] )
            self.et_fileitems[filename].setData(column, QtCore.Qt.UserRole, filename)
            self.et_fileitems[filename].setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
            self.et_fileitems[filename].setFirstColumnSpanned(True)
            self.et_fileitems[filename].setExpanded(True)
            
        for (run_id, event_id) in request.data:
            item_key = (filename,run_id,event_id)
            if item_key not in self.et_eventitems:
                self.et_eventitems[item_key] = QtGui.QTreeWidgetItem( self.et_fileitems[filename], ["Run %d, Event %d"%(run_id, event_id)] )
                self.et_eventitems[item_key].setExpanded(True)
            eventdata = request.data[(run_id, event_id)]
            for name,product in eventdata.dataproducts.items():
                if item_key not in self.et_dataproducts:
                    self.et_dataproducts[item_key] = {}
                if name not in self.et_dataproducts[item_key]:
                    self.et_dataproducts[item_key][name] = QtGui.QTreeWidgetItem( self.et_eventitems[item_key], [name,"0.0% complete"],QtCore.Qt.DisplayRole )
                    self.et_dataproducts[item_key][name].setExpanded(True)
                else:
                    # rerunning. just reset counter.
                    self.et_dataproducts[item_key][name].setText(1, "0.0% complete" )

    def updateFromMonitor( self, request ):
        print "Req. Monitor wants to update.",id(request)
        for ievent in xrange( request.first_event, request.first_event+request.nevents ):
            for event, eventdata in request.data.items():
                for name,product in eventdata.dataproducts.items():
                    if product==None:
                        continue
                    pct = product.getPercentComplete()
                    item_key = ( request.filename, request.first_run, ievent )
                    print name,pct
                    self.et_dataproducts[ item_key ][ name ].setText( 1, "%.1f%% complete"%(pct))

    def setupUI(self):
        layout = QtGui.QVBoxLayout()
        # event tree
        self.eventTree = QtGui.QTreeWidget()
        self.eventTree.setHeaderHidden(True)
        layout.addWidget(  self.eventTree )
        # fileinput
        self.finputWidget = QtGui.QWidget()
        finput_layout = QtGui.QHBoxLayout()
        finput_label = QtGui.QLabel("LArSoft File")
        self.filename_input = QtGui.QLineEdit("/uboone/data/users/tmw/chromasim_data/single_gen_uboone.root")
        finput_layout.addWidget( finput_label )
        finput_layout.addWidget( self.filename_input )
        self.finputWidget.setLayout( finput_layout )
        layout.addWidget( self.finputWidget )
        # event range input
        self.rangeWidget = QtGui.QWidget()
        range_layout = QtGui.QHBoxLayout()
        range_runlabel = QtGui.QLabel("First Run")
        range_evtlabel = QtGui.QLabel("First Event")
        range_numlabel = QtGui.QLabel("Number of Events")
        self.input_first_run = QtGui.QLineEdit("1")
        self.input_first_event = QtGui.QLineEdit("1")
        self.input_nevents = QtGui.QLineEdit("1")
        self.input_reload = QtGui.QCheckBox("Reload events")
        range_layout.addWidget( range_numlabel )
        range_layout.addWidget( self.input_nevents )
        range_layout.addWidget( range_runlabel )
        range_layout.addWidget( self.input_first_run )
        range_layout.addWidget( range_evtlabel )
        range_layout.addWidget( self.input_first_event )
        range_layout.addWidget( self.input_reload )
        self.rangeWidget.setLayout( range_layout )
        layout.addWidget( self.rangeWidget )

        cache_widget = QtGui.QWidget()
        self.loadcache_checkbox = QtGui.QCheckBox("Load from Cache")
        self.storecache_checkbox = QtGui.QCheckBox("Store in Cache")
        layout_cache = QtGui.QHBoxLayout()
        layout_cache.addWidget( self.loadcache_checkbox )
        layout_cache.addWidget( self.storecache_checkbox )
        cache_widget.setLayout( layout_cache )
        layout.addWidget( cache_widget )

        # data products check boxes
        # TODO: Allow for data product customization
        self.data_checkboxes = {}
        for dataproduct in ["RawDigits","ROI","OpdetFEM", "OpFlash"]:
            self.data_checkboxes[dataproduct] = QtGui.QCheckBox(dataproduct)
            layout.addWidget( self.data_checkboxes[dataproduct] )
        self.data_checkboxes["RawDigits"].setChecked(True)
        # submit button
        self.submit_request = QtGui.QPushButton( "Submit" )
        self.submit_request.clicked.connect( self.submitRequest )
        layout.addWidget( self.submit_request )

        self.setLayout( layout )
        
