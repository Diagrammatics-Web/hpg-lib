import math

class HalfHourglass:
    '''Represents part of an edge from one vertex to another in an hourglass plabic graph.'''
    def __init__(self, id, v_from, v_to, strand_count, label='', twin=None):
        '''id: an object, assumed unique, should be hashable
           strand_count: number of strands between from and to. if 0, this is an edge boundary
           label: an object
        '''
        self.id = id
        self.v_from = v_from
        self.v_to = v_to
        self.strand_count = strand_count
        self.label = label

        # set up twin with swapped to/from vertices
        self.twin = twin
        if (twin == None):
            self.twin = HalfHourglass("twin_" + str(id), v_to, v_from, strand_count, '', self)
            
        self.cw_next = self
        self.ccw_next = self

    def add_strand(self):
        self.strand_count += 1
        self.twin.strand_count += 1
    def thicken(self): # alias
        self.add_strand()

    def remove_strand(self):
        # hourglass must have at least one strand 
        if (self.strand_count > 1): 
            self.strand_count -= 1
            self.twin.strand_count -= 1
    def thin(self): # alias
        self.remove_strand()

    def insert_cw_next(self, hh):
        hh.ccw_next = self
        hh.cw_next = self.cw_next
        self.cw_next.ccw_next = hh
        self.cw_next = hh

    def insert_ccw_next(self, hh):
        hh.cw_next = self
        hh.ccw_next = self.ccw_next
        self.ccw_next.cw_next = hh
        self.ccw_next = hh

    def is_phantom(self):
        return self.strand_count == 0

    def get_angle(self):
        ''' returns the angle between the vector from v_from to v_to and the x-axis.
        returns value between 0 and 2pi.'''
        angle = math.atan2(self.v_to.y-self.v_from.y, self.v_to.x-self.v_from.x)
        if angle < 0:
            angle += 2 * math.pi
        return angle