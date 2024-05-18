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
        # this is a circularly double linked list of half hourglasses, connected using
        # ccw_next and cw_next. the first element should be the one making the smallest
        # angle with the x-axis.
        self._half_hourglasses_head = None

    def __repr__(self):
        return "HourglassPlabicGraph Vertex object: id=%s, label=%s"%(str(self.id), str(self.label))

    def create_hourglass_between(self, v_to, strand_count):
        ''' Creates a half hourglass to and from v_to, inserting it into each vertex's hourglass list.'''
        hh = HalfHourglass(str(self.id) + "_" + str(v_to.id), self, v_to, strand_count)

        self._insert_hourglass(hh)
        v_to._insert_hourglass(hh.twin)

    def _insert_hourglass(self, hh):
        '''Inserts hh into the hourglass list. Maintains the list with the first angle being the one with the smallest angle ccw from the x-axis.'''
        # empty list case
        if (self._half_hourglasses_head == None): 
            self._half_hourglasses_head = hh
            return
        
        # find first edge with greater angle, then insert_cw_next
        hh_angle = hh.get_angle()
        iter = self._half_hourglasses_head
        while True: # runs until first edge with greater angle found or entire list is exhausted
            if (hh_angle < iter.get_angle()):
                iter.insert_cw_next(hh)
                return
            # otherwise, continue iterating through loop
            iter = iter.ccw_next
            if (iter == self._half_hourglasses_head):
                # we've run the entire loop, so angle is greater than every other edge
                iter.insert_ccw_next(hh)
                return

    def get_trip(self, i):
        '''Traverses the graph to compute trip i and returns an array of all visited half hourglasses.'''
        assert self.boundary, "vertex should be on the boundary."
        assert self.total_degree() == 1, "multiplicity of vertex should be 1."

        # return the array of visited hourglasses
        hourglasses = []

        # find the hourglass to the graph interior
        hh = self._half_hourglasses_head
        while hh.strand_count != 1: hh = hh.cw_next()
        hourglasses.append(hh)

        vertex = hh.v_to
        strand_index = 0
        while(not vertex.boundary):
            # get the next hourglass and its strand
            # note that the ith strand of the hourglass is the ith strand of its twin
            hh = hh.twin
            if (vertex.filled): hh, strand_index = hh.get_get_ccw_ith_strand(i, strand_index)
            else: hh, strand_index = hh.get_get_cw_ith_strand(i, strand_index)
            vertex = hh.v_to
            hourglasses.append(hh)

        return hourglasses
                
    def get_neighbors(self):
        '''Returns all adjacent vertices in a list.'''
        neighbors = []
        iter = self._half_hourglasses_head
        while True:
            neighbors.append(iter)
            iter = iter.ccw_next
            if (iter == self._half_hourglasses_head): return
    
    def total_degree(self):
        '''Returns the number of strands around self.'''
        if (self._half_hourglasses_head == None): return 0
        return self_half_hourglasses_head.get_num_elements()

    def simple_degree(self):
        '''Returns the number of hourglasses around self.'''
        if (self._half_hourglasses_head == None): return 0
            
        count = 1
        iter = self._half_hourglasses_head.cw_next
        while(iter != self._half_hourglasses_head):
            count += 1
            iter = iter.cw_next
        return count