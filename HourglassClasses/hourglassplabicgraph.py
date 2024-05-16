from sage.all import Graph

class HourglassPlabicGraph:
     '''Represents an hourglass plabic graph.'''
    def __init__(self):
        self.inner_vertices = []
        self.boundary_vertices = []
        
        self.layout = 'circular'

    def make_circular(self, radius=10):
        n = len(self.boundary_vertices)
        for i,v in self.boundary_vertices:
            v.x = radius*math.sin((i+0.5)*2*math.pi/n)
            v.y = radius*math.cos((i+0.5)*2*math.pi/n)
            
        self.tutte_layout()
        self.layout = "circular"

    def to_graph(self, hourglass_labels=False):
        '''Creates an equivalent sagemath Graph. Represents strands in an hourglass in the label.'''
        vertices = inner_vertices + boundary_vertices
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

    def get_trip(self, v_from, i, output='half_strands'):
        '''v_from: the initial boundary Vertex; assumes multiplicity 1
           i: computes trip_i by taking the ith left at unfilled/ith right at filled

           Returns the list of HalfStrands the trip visits in order.'''
        v = v_from
        e = v.get_half_strands()[0] # Assumes multiplicity 1!
        return e.get_trip(i, output)

    def get_trip_perm(self, trip_idx):
        '''Computes the trip_idx'th trip permutation as usual.
           Returns a permutation where the boundary vertices are numbered
           1, 2, ..., n CCW from slightly east of due north.'''
        prom = []
        for i in range(len(self.boundary_vertices)):
            v = self.boundary_vertices[i]
            trip = self.get_trip(v, trip_idx)
            w = trip[-1].v_to
            prom.append(self.boundary_vertices.index(w)+1)
        return prom

    def get_trip_perms(self):
        '''Returns a list [t_1, ..., t_{r-1}] where t_i is the ith trip permutation
           and r is the maximum degree of an internal vertex.'''
        r = max(v.total_degree() for v in self.vertices.values() if v.is_interior_vertex())
        return [self.get_trip_perm(i) for i in range(1, r)]