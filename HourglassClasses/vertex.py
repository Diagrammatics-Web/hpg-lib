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

        
    def insert_hourglass(self, hourglass):
        ''' Inserts a half hourglass into the list, sorted based on arctan.'''
        hh_angle = hourglass.get_angle()
        iter = self._half_hourglasses
        while(hh_angle > iter.angle):
            iter = iter.ccw_next
        
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
            count ++
            iter = iter.cw_next
        return count