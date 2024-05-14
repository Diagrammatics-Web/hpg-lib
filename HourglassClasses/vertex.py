import halfhourglass

class Vertex:
    '''Represents a vertex in an hourglass plabic graph.'''
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
        self._half_hourglasses = None

    def __repr__(self):
        return "HourglassPlabicGraph Vertex object: id=%s, label=%s"%(str(self.id), str(self.label))

    def create_hourglass_to(self, v_to, strand_count):
       pass 
        
    def insert_hourglass(self, hh):
        ''' Inserts a half hourglass into the list. Maintains the list with the first angle being the one with the smallest angle ccw from the x-axis.'''
        # empty list case
        if (self._half_hourglasses == None): 
            self._half_hourglasses = hh
            return
        
        # find first edge with greater angle, then insert_cw_next
        hh_angle = hh.get_angle()
        iter = self._half_hourglasses
        while True: # runs until first edge with greater angle found or entire list is exhausted
            if (hh_angle < iter.get_angle()):
                iter.insert_cw_next(hh)
                return
            # otherwise, continue iterating through loop
            iter = iter.ccw_next
            if (iter == self.half_hourglasses):
                # we've run the entire loop, so angle is greater than every other edge
                iter.insert_ccw_next(hh)
                return
                
        
    def total_degree(self):
        '''Returns the number of strands around self.'''
        if (self._half_hourglasses == None):
            return 0
            
        count = self._half_hourglasses.strand_count
        iter = self._half_hourglasses.cw_next
        while(iter != self._half_hourglasses):
            count += iter.strand_count
            iter = iter.cw_next
        return count

    def simple_degree(self):
        '''Returns the number of hourglasses around self.'''
        if (self._half_hourglasses == None):
            return 0
            
        count = 1
        iter = self._half_hourglasses.cw_next
        while(iter != self._half_hourglasses):
            count += 1
            iter = iter.cw_next
        return count