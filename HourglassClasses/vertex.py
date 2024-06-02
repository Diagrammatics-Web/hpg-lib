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

    def create_hourglass_between(self, v_to, multiplicity):
        ''' Creates a half hourglass to and from v_to, inserting it into each vertex's hourglass list.
            v_to: The vertex to create the hourglass to.
            multiplicity: the number of strands on the edge.
            OUTPUT: The constructed hourglass.
            '''
        hh = HalfHourglass(str(self.id) + "_" + str(v_to.id), self, v_to, multiplicity)

        self._insert_hourglass(hh)
        v_to._insert_hourglass(hh.twin())

        return hh

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
        for iter_hh in self._half_hourglasses_head.iterate_clockwise():
            if hh_angle < iter_hh.get_angle():
                iter_hh.insert_cw_next(hh)
                return
        # we've run the entire loop, so angle is greater than every other edge
        self._half_hourglasses_head.insert_ccw_next(hh)

    def _remove_hourglass(self, hh):
        "Safely removes the provided hourglass from this vertex's hourglass list."
        assert hh.v_from() == self, "Half hourglass " + str(hh.id) + " does not belong to this vertex."
        if hh == self._half_hourglasses_head:
            self._half_hourglasses_head = self._half_hourglasses_head.ccw_next()
            if hh == self._half_hourglasses_head:
                self._half_hourglasses_head == None
        hh.remove()

    def clear_hourglasses(self):
        ''' Deletes all hourglasses (and their twins) attached to this vertex.'''
        if self._half_hourglasses_head == None: return # hacky, there should be a cleaner way to do this
        while self._half_hourglasses_head.cw_next() != None:
            self._half_hourglasses_head = self._half_hourglasses_head.cw_next()
            self._half_hourglasses_head.cw_prev().twin().remove()
            self._half_hourglasses_head.cw_prev().remove()
        self._half_hourglasses_head = None
    
    def get_hourglass_to(self, v_to):
        for hh in self._half_hourglasses_head.iterate_clockwise():
            if hh.v_to() == v_to: return hh
        raise ValueError("Hourglass to vertex " + v_to.id() + " does not exist.")

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
        while not vertex.boundary:
            strand = strand.twin
            strand = strand.get_ccw_ith_element(i) if vertex.filled else strand.get_cw_ith_element(i)
            vertex = strand.v_to()
        visited.append(strand if output == 'half_strands' else strand.hourglass() if output == 'half_hourglasses' else strand.id)

        return visited
                
    def get_neighbors(self):
        '''Returns all adjacent vertices in a list.'''
        return [hh.v_to() for hh in self._half_hourglasses_head.iterate_clockwise()]
    
    def total_degree(self):
        '''Returns the number of strands around this vertex.'''
        if (self._half_hourglasses_head == None): return 0
        s = self._half_hourglasses_head._get_first_strand()
        return 0 if s == None else s.get_num_elements()

    def simple_degree(self):
        '''Returns the number of hourglasses around this vertex.'''
        if (self._half_hourglasses_head == None): return 0
        return self._half_hourglasses_head.get_num_elements()

    # Vertex manipulation functions

    def is_contractible(self):
        hh1 = self._half_hourglasses_head
        hh2 = hh1.cw_next()
        # Check if vertex is contractible
        if (hh1 != hh2.cw_next() or hh1 == hh2): return false
        if (hh1.v_to().filled and hh2.v_to().filled and not self.filled) or (not hh1.v_to().filled and not hh2.v_to().filled and self.filled):
            return false
        return true
    
    def contract(self):
        hh1 = self._half_hourglasses_head
        hh2 = hh1.cw_next()

        # transfer hourglasses to one vertex, delete the other
        rem_v = hh1.v_to() #remaining
        del_v = hh2.v_to()

        hh = del_v._half_hourglasses_head
        while hh.v_from() != rem_v:
            if hh == hh2.twin(): continue
            
            hh_next = hh.cw_next()
            hh._v_from = rem_v
            rem_v._insert_hourglass(hh)
            hh = hh_next

        rem_v.remove_hourglass(hh1.twin())

    # Square move functions

    def square_move_contract(self, hh):
        raise NotImplementedError("square_move_contract not yet implemented")

    def square_move_expand(self, hh1, hh2):
        raise NotImplementedError("square_move_expand not yet implemented")



















