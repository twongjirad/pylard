import os,sys
import pyqtgraph.opengl as gl
import collada
import numpy as np
from collections import OrderedDict
from pylard.pylardisplay.solidstreewidget import SolidsTreeWidget


class DetectorDisplay(gl.GLViewWidget) :
    def __init__(self, use_cache=True, cache_dir="./cache"):
        super(DetectorDisplay,self).__init__()
        self.treeitems = OrderedDict()

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
        
    
