from sage.all import Graph
from .vertex import Vertex

class HourglassPlabicGraph:
    '''Represents an hourglass plabic graph.'''
    def __init__(self):
        # dictionaries pairing IDs to vertices
        self._inner_vertices = {}
        self._boundary_vertices = {}

        self.faces = []
        
        self.layout = 'circular'

    # Construction functions

    def create_boundary(self, num):
        ''' Creates num boundary vertices, labeled from 0 to num-1, and connects them with phantom edges.
            The vertices will be unfilled. This function can only be called on an empty graph.
            num: the number of boundary vertices to create.
            '''
        assert self._inner_vertices.len() == 0 and self._boundary_vertices.len() == 0, "Cannot call create_boundary on a non-empty graph."

        for i in range(0, num):
            id = str(i)
            self._boundary_vertices[i] = Vertex(id, 10*math.sin((i+0.5)*2*math.pi/num), 10*math.cos((i+0.5)*2*math.pi/num), False, True, id)

        for i in range(0, num-1):
            self._boundary_vertices[i].create_hourglass_between(self._boundary_vertices[i+1], 0)
        hh = self._boundary_vertices[0].create_hourglass_between(self._boundary_vertices[num-1], 0)

        # TODO: Create face
            
    def create_vertex(self, v_id, label, x, y, filled, boundary=False, verify_id=False):
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
        if boundary: self._inner_vertices[v_id] = vertex
        else: self._boundary_vertices[v_id] = vertex

    def remove_vertex(self, v_id):
        self._get_vertex(v_id).clear_hourglasses()
        
    def create_hourglass(self, v1_id, v2_id, multiplicity, create_face=True, verify_face=True):
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)

        hh = v1.create_hourglass_between(v2, multiplicity)
        
        # TODO: Create faces
    
    def remove_hourglass(self, v1_id, v2_id, create_face=True, verify_face=True):
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)

        hh = v1.get_hourglass_to(v2)
        hh.remove()
        hh.twin().remove()

        # TODO: reform faces
    
    # Layout functions
    
    def make_circular(self, radius=10): # TODO: TEST
        n = len(self.boundary_vertices.values())
        for i,v in self.boundary_vertices:
            v.x = radius*math.sin((i+0.5)*2*math.pi/n)
            v.y = radius*math.cos((i+0.5)*2*math.pi/n)
            
        self.tutte_layout()
        self.layout = "circular"

    def to_graph(self, hourglass_labels=False): # TODO: VERIFY/TEST
        '''Creates an equivalent sagemath Graph. Represents strands in an hourglass in the label.'''
        vertices = inner_vertices.values() + boundary_vertices.values()
        edges = [(h.v_from.id, h.v_to.id, h.label if hourglass_labels else h.strand_count) for h in self.hourglasses.values()]
        pos = {v:(v.x,v.y) for v in vertices}
        g = Graph([vertices,edges],format='vertices_and_edges', pos=pos)
        return g

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

    def _get_vertex(id):
        ''' Internal helper function that gets the vertex with the given id from either _inner_vertices or _boundary_vertices, and throws if the id is not found.'''
        v = self._inner_vertices.get(v_id)
        if v == None: 
            v = self._boundary_vertices.get(v_id)
            if v == None: raise ValueError("id " + str(id) + " does not correspond to any vertex.")