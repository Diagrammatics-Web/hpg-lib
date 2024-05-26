from .halfhourglass import HalfHourglass

class Vertex:
    '''Represents a vertex in an hourglass plabic graph.
        A vertex can be filled (black) or unfilled (white), and is connected to other
        vertices through hourglass edges.
        When traversing a HPG, trip i turns at the ith left on an unfilled vertex
        and the ith right on a filled vertex.'''
    def __init__(self, id, x, y, filled, boundary=False, label=''):
        '''id: an object, assumed unique, should be hashable
           (x, y) coordinates
           filled boolean: true for filled/black, false for unfilled/white
           boundary: true if on the boundary
           label: an object
           '''
        # first: true if first boundary vertex
        # last: true if last boundary vertex
        self.id = id
        self.x = x
        self.y = y
        self.filled = filled
        self.boundary = boundary
        self.first = False
        self.last = False
        self.label = label
        ''' Some half hourglass around this vertex. When the graph is properly embedded,
            the vertex will attempt to maintain this as the the one making the smallest
            angle with the x-axis during insertions and deletions, but this behavior is not guaranteed.'''
        self._half_hourglasses_head = None

    def __repr__(self):
        return "HourglassPlabicGraph Vertex object: id=%s, label=%s"%(str(self.id), str(self.label))

    def create_hourglass_between(self, v_to, strand_count):
        ''' Creates a half hourglass to and from v_to, inserting it into each vertex's hourglass list.'''
        hh = HalfHourglass(str(self.id) + "_" + str(v_to.id), self, v_to, strand_count)

        self._insert_hourglass(hh)
        v_to._insert_hourglass(hh.twin())

    def _insert_hourglass(self, hh):
        ''' Inserts a half hourglass into the hourglass list. 
            Maintains the list with the first angle being the one with the smallest angle ccw from the x-axis.'''
        # empty list case
        if self._half_hourglasses_head == None: 
            self._half_hourglasses_head = hh
            return

        # reset head
        while self._half_hourglasses_head.get_angle() > self._half_hourglasses_head.cw_prev().get_angle():
            self._half_hourglasses_head = self._half_hourglasses_head.cw_prev()
        
        # find first edge with greater angle, then insert_cw_next
        hh_angle = hh.get_angle()
        iter = self._half_hourglasses_head
        while True: # runs until first edge with greater angle found or entire list is exhausted
            if hh_angle < iter.get_angle():
                iter.insert_cw_next(hh)
                return
            # otherwise, continue iterating through loop
            iter = iter.ccw_next()
            if iter == self._half_hourglasses_head:
                # we've run the entire loop, so angle is greater than every other edge
                iter.insert_ccw_next(hh)
                return

    def get_trip(self, i, output='half_strands'):
        ''' Traverses the graph to compute trip i and returns an array of all visited half strands or half hourglasses.
            i: computes trip_i by taking the ith left at unfilled/ith right at filled
            output: if output = 'half_strands', returns an array of HalfStrands. If output = 'half_hourglasses', returns HalfHourglasses.
                    Otherwise, returns the ids of the HalfStrands.'''
        assert self.boundary, "Vertex " + self.id + " should be on the boundary."
        assert self.total_degree() == 1, "multiplicity of vertex " + self.id + " should be 1."

        visited = []
        
        # find the hourglass to the graph interior
        hh = self._half_hourglasses_head
        while hh.is_boundary(): hh = hh.cw_next()
        strand = hh._half_strands_head
        visited.append(strand if output == 'half_strands' else strand.hourglass() if output == 'half_hourglasses' else strand.id)

        vertex = strand.v_to()
        while(not vertex.boundary):
            strand = strand.twin
            if (vertex.filled): strand = strand.get_ccw_ith_element(i)
            else: strand = strand = strand.get_cw_ith_element(i)
            vertex = strand.v_to()
        visited.append(strand if output == 'half_strands' else strand.hourglass() if output == 'half_hourglasses' else strand.id)

        return visited
                
    def get_neighbors(self):
        '''Returns all adjacent vertices in a list.'''
        neighbors = []
        iter = self._half_hourglasses_head
        while True:
            neighbors.append(iter)
            iter = iter.ccw_next()
            if (iter == self._half_hourglasses_head): return
    
    def total_degree(self):
        '''Returns the number of strands around self.'''
        if (self._half_hourglasses_head == None): return 0
        return self._half_hourglasses_head._half_strands_head.get_num_elements()

    def simple_degree(self):
        '''Returns the number of hourglasses around self.'''
        if (self._half_hourglasses_head == None): return 0
        return self._half_hourglasses_head.get_num_elements()