import math
from sage.all import Graph
from .vertex import Vertex
from .face import Face
from .idgenerator import ID

class HourglassPlabicGraph:
    '''Represents an hourglass plabic graph.'''
    def __init__(self, n=0):
        # dictionaries pairing IDs to vertices and faces
        self._inner_vertices = dict()
        self._boundary_vertices = dict()
        self._faces = dict()
        
        self.layout = 'circular'
        if n > 0: self.create_boundary(n)

    # Construction functions

    def create_boundary(self, n, r=10):
        r"""
        Creates n boundary vertices, labeled from 0 to n-1, and connects them with phantom edges.
        The vertices will be unfilled. This function can only be called on an empty graph.

        INPUT:
    
        - ``n`` -- integer; the number of boundary vertices to create.
        - ``r`` -- float; the radius of the boundary.

        EXAMPLES:
    
            sage: HPG = HourglassPlabicGraph()
            sage: HPG.create_boundary()
        """
        assert self.order() == 0, "Cannot call create_boundary on a non-empty graph."

        for i in range(0, n):
            id = str(i)
            self._boundary_vertices[id] = Vertex(id, r*math.sin((i+0.5)*2*math.pi/n), r*math.cos((i+0.5)*2*math.pi/n), False, True, id)

        for i in range(0, n-1):
            Vertex.create_hourglass_between(self._boundary_vertices[str(i)], self._boundary_vertices[str(i+1)], 0)
        hh = Vertex.create_hourglass_between(self._boundary_vertices[str(n-1)], self._boundary_vertices[str(0)], 0)

        inner_face = Face("face0", hh)
        outer_face = Face("face1", hh.twin())
        self._faces[inner_face.id] = inner_face
        self._faces[outer_face.id] = outer_face
                          
    def create_vertex(self, v_id, x, y, filled, boundary=False, label='', verify_id=False):
        ''' Adds a vertex to the graph.
            v_id: The id given to the vertex. Should be unique.
            label: 
            x: The x position of the vertex
            y: The y position of the vertex
            filled: Whether the vertex is to be filled or not.
            boundary: Whether the vertex is on the boundary. Defaults to False.
            verify_id: Check whether v_id is already in use. Defaults to False.
            '''
        if verify_id and ((not boundary and v_id in self._inner_vertices) or (boundary and v_id in self._boundary_vertices)): raise ValueError("v_id already in use.")

        vertex = Vertex(v_id, x, y, filled, boundary, label)
        if boundary: self._boundary_vertices[v_id] = vertex
        else: self._inner_vertices[v_id] = vertex

    def remove_vertex(self, v_id):
        self._get_vertex(v_id).clear_hourglasses()
        if v_id in self._inner_vertices: del self._inner_vertices[v_id]
        else: del self._boundary_vertices[v_id]
        
    def create_hourglass(self, v1_id, v2_id, multiplicity):
        print("Creating hourglass between", v1_id, "and", v2_id) # TESTING
        
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)

        new_hh = Vertex.create_hourglass_between(v1, v2, multiplicity)

        # Create faces

        face = None
        # First, find an already existing reference to this hourglass's right face
        # There is a chance we are connecting two faces, so we should find the second one
        # and remove it from our list
        for hh in new_hh.iterate_right_turns():
            if hh.right_face is not None:
                if face is None: face = hh.right_face
                elif face is not hh.right_face:
                    del self._faces[hh.right_face.id]
                    break
        if face is not None:
            face.initialize_half_hourglasses(new_hh)
        # If none exists, create a new one
        else: 
            face = Face(ID.get_new_id("face"), new_hh)
            self._faces[face.id] = face

        # Either the twin's face will be the same as this, or we will need to create a new face since the old face
        # will be the same as the one reused for the hourglass and will no longer be valid
        if new_hh.twin().right_face is None:
            face = Face(ID.get_new_id("face"), new_hh.twin())
            self._faces[face.id] = face
        
    def remove_hourglass(self, v1_id, v2_id):
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)

        face1 = None
        hh1 = None
        face2 = None
        hh2 = None
        # get a new hourglass for each face the hourglass belongs to
        del_hh = v1.get_hourglass_to(v2)
        for hh in del_hh.iterate_right_turns():
            if hh is not del_hh and hh is not del_hh.twin():
                face1 = hh.right_face
                hh1 = hh
        for hh in del_hh.twin().iterate_right_turns():
            if hh is not del_hh and hh is not del_hh.twin():
                face2 = hh.right_face
                hh2 = hh
        
        del_hh = Vertex.remove_hourglass(v1, v2)

        if face1 is not None:
            face1.initialize_half_hourglasses(hh1)
        if face2 is not None and hh2.right_face is not face1: # this should only happen if deletion results in a forest
            face2.initialize_half_hourglasses(hh2)
    
    # Layout functions
    
    def make_circular(self, r=10): # TODO: TEST
        n = len(self.boundary_vertices.values())
        for i,v in self.boundary_vertices:
            v.x = r*math.sin((i+0.5)*2*math.pi/n)
            v.y = r*math.cos((i+0.5)*2*math.pi/n)
            
        self.tutte_layout()
        self.layout = "circular"

    def tutte_layout(self, error=0.01, max_iter = 1000):
        '''from https://cs.brown.edu/people/rtamassi/gdhandbook/chapters/force-directed.pdf.'''
        for i in range(max_iter):
            err = 0
            for v in self.inner_vertices():
                neighbours = v.get_neighbors()
                x_new = sum(w.x for w in neighbours)/len(neighbours)
                y_new = sum(w.y for w in neighbours)/len(neighbours)
                err += (v.x-x_new)**2 + (v.y-y_new)**2
                v.x, v.y = x_new, y_new
            if err < error:
                break

    def to_graph(self, hourglass_labels=False): # TODO: VERIFY/TEST
        '''Creates an equivalent sagemath Graph. Represents strands in an hourglass in the label.'''
        vertices = inner_vertices.values() + boundary_vertices.values()
        edges = [(h.v_from.id, h.v_to.id, h.label if hourglass_labels else h.strand_count) for h in self.hourglasses.values()]
        pos = {v:(v.x,v.y) for v in vertices}
        g = Graph([vertices,edges],format='vertices_and_edges', pos=pos)
        return g

    # Trip functions

    def get_trip(self, vertex, i, output='half_strands'):
        ''' vertex: the initial boundary Vertex; assumes multiplicity 1
            i: computes trip_i by taking the ith left at unfilled/ith right at filled
            output: if output = 'half_strands', returns an array of HalfStrands. Otherwise, returns HalfHourglasses.

            Returns the list of HalfHourglasses/HalfStrands the trip visits in order.'''

        assert vertex.is_boundary(), "vertex should be on the boundary."
        assert vertex.total_degree() == 1, "multiplicity of vertex should be 1."
        
        return vertex.get_trip(i, output)

    def get_trip_perm(self, i):
        ''' Computes the ith trip permutation.
            The trip i permutation is generated by finding where trip i sends each boundary vertex to.
            Boundary vertices are assumed to be numbered 1, 2, ..., n CW starting slightly east of due north.'''
        perm = []
        for vertex in self.boundary_vertices:
            trip = vertex.get_trip(i)
            final_vertex = trip[-1].v_to
            perm.append(self.boundary_vertices.index(w)+1)
        return perm

    def get_trip_perms(self):
        '''Returns a list [t_1, ..., t_{r-1}] where t_i is the ith trip permutation
           and r is the maximum degree of an internal vertex.'''
        r = max(v.total_degree() for v in self.inner_vertices)
        return [self.get_trip_perm(i) for i in range(1, r)]

    def _get_vertex(self, v_id):
        ''' Internal helper function that gets the vertex with the given id from either _inner_vertices or _boundary_vertices, and throws if the id is not found.'''
        v = self._inner_vertices.get(v_id)
        if v is None: 
            v = self._boundary_vertices.get(v_id)
            if v is None: raise ValueError("id " + str(v_id) + " does not correspond to any vertex.")
        return v

    def order(self):
        ''' The number of vertices in this graph.'''
        return len(self._inner_vertices) + len(self._boundary_vertices)