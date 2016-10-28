import os,sys
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import collada
import numpy as np
from collections import OrderedDict
from pylard.display.solidstreewidget import SolidsTreeWidget


class DetectorDisplay(gl.GLViewWidget) :
    def __init__(self, use_cache=True, cache_dir="./pylardcache", 
                 daefile=os.path.dirname(__file__)+"/../config/microboone_32pmts_nowires_cryostat.dae"):
        super(DetectorDisplay,self).__init__()
        self.treeitems = OrderedDict()
        self.daefile = daefile
        self.load_geometry( self.daefile )

        # user items (this tracks items. is tree widget displayed by detcontrol widget)
        self.user_items = {} # dict of name and visitem
        self.user_item_checkboxes = {} # dict of name and checkbox governing if active
        self.drawn_user_items = []
        self.user_item_tree = pg.TreeWidget()
        self.user_item_tree.setColumnCount(2)
        

    def setMainWindow( self, window ):
        self.themainwindow = window

    def setControlWidget( self, control ):
        self.control = control

    def load_geometry( self, daefile ):
        # Make list of solids
        self.solids = self.read_daecollada( daefile )
        # Widget to turn solids on/off
        self.solidswidget = SolidsTreeWidget( self.solids )
        self.solidswidget.treeWidget.itemChanged.connect( self.solidsListChanged )

        # generate the mesh and load 3D widget
        self.vertices, self.indices = self.flatten_solids( self.solids )
        self.geo_meshdata = gl.MeshData( vertexes=self.vertices, faces=self.indices )
        self.geo_meshitem = gl.GLMeshItem( meshdata=self.geo_meshdata, drawEdges=True, drawFaces=False, color=(1.0,1.0,1.0,1.0), smooth=False )
        self.geo_meshitem.rotate( 90, 1, 0, 0 )
        self.setCameraPosition(distance=15000)
        self.addItem( self.geo_meshitem )

    def read_daecollada( self, daefile ):
        try:
            geom = collada.Collada( daefile )
        except:
            raise RuntimeError("Could not read DAE/COLLADA file")
        
        #solids = {}
        solids = OrderedDict()
        mesh = collada.Collada( daefile )
        boundgeom = list(mesh.scene.objects('geometry'))
        for geom in boundgeom:
            solidname = geom.original.name.split("0x")[0]
            if solidname not in solids:
                solids[solidname] = {"vertices":[],"indices":[] }
                
            boundprimitives = list(geom.primitives())
            for boundprim in boundprimitives:
                triset = boundprim.triangleset()
                solids[solidname]["vertices"].append( triset.vertex )
                solids[solidname]["indices"].append( triset.vertex_index )

        return solids

    def flatten_solids( self, solids ):
        vertices = []
        indices = []
        nvertices = 0
        for solid in solids:
            # first we check if we should draw the solid
            if self.solidswidget.solids_state[solid]==False:
                #print solid,"is off"
                continue
            for n,(solid_vertices,solid_indices) in enumerate(zip(solids[solid]["vertices"],solids[solid]["indices"])):
                #print solid,"prim #%d, nvertices=%d, offset=%d" % ( n, len(solid_vertices),nvertices)
                #print solid_indices
                solid_indices_copy = np.copy( solid_indices )
                solid_indices_copy += nvertices
                nvertices += len(solid_vertices)
                vertices.append( solids[solid]["vertices"][n] )
                indices.append( solid_indices_copy )
        return np.concatenate(vertices), np.concatenate(indices)

    def solidsListChanged(self):
        self.vertices, self.indices = self.flatten_solids( self.solids )
        self.geo_meshdata.setVertexes(verts=self.vertices)
        self.geo_meshdata.setFaces(faces=self.indices)
        self.geo_meshitem.meshDataChanged()
            
    def addVisItem( self, name, visitem ):
        self.user_items[name] = visitem
        self.user_item_checkboxes[name] = QtGui.QCheckBox('')
        self.map_user_checkboxes2name[self.user_item_checkboxes[name]] = name
        self.user_item_checkboxes[name].setChecked(False)
        # connect to signal
        # multiple sub-objects!
        if type(visitem) is list:
            self.user_subitem_cbxs[name] = []
            for ix,subitem in enumerate(visitem):                    
                self.user_subitem_cbxs[name].append( QtGui.QCheckBox('') )
                self.user_subitem_cbxs[name][ix].setChecked(False)

        # make tree widget item
        item = pg.TreeWidgetItem(['',name])
        item.setWidget(0,self.user_plot_checkboxes[name])
        self.user_items.addTopLevelItem( item )

        if type(visitem) is list:
            for ix in range(0,len(visitem)):
                subitem = visitem[ix]
                if hasattr(subitem,"uservisname"):
                    subname = subitem.uservisname+"_%d"%(ix)
                else:
                    subname = name+"_%d"%(ix)
                subitem = pg.TreeWidgetItem([subname])
                item.addChild(subitem)
                self.user_items.setItemWidget( subitem, 1, self.user_subitem_cbxs[name][ix] )
        
    def clearVisItems( self ):
        for name in self.drawn_user_items:
            self.removeItem( self.user_items[name] )
        self.drawn_user_items = []
        self.user_items = {}
        self.user_item_checkboxes = {}

    def drawUserItems(self):
        for name,visitem in self.user_items.items():
            if self.user_item_checkboxes[name].isChecked():
                # draw this
                if name not in self.drawn_user_items:
                    self.addItem( visitem )
                    self.drawn_user_items.append( name )
                else:
                    # already drawn
                    continue
            else:
                if name in self.drawn_user_items:
                    # remove from the viewer
                    self.removeItem( visitem )
                    self.drawn_user_items.remove(name)
                else:
                    # not currently drawn, so keep moving
                    continue

    
                
