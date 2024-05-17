import math

class HalfHourglass:
    ''' Represents part of an edge from one vertex to another in an hourglass plabic graph.
        Strands are represented by the strand_count member, which can be considered a multiplicity/edge weight.
        When "iterating" over strands, the first (0th) strand is the most counterclockwise.'''
    def __init__(self, id, v_from, v_to, strand_count, label='', twin=None):
        ''' id: an object, assumed unique, should be hashable
            strand_count: number of strands between from and to. if 0, this is an edge boundary
            label: an object
        '''
        self.id = id
        self.v_from = v_from
        self.v_to = v_to
        self.strand_count = strand_count
        self.label = label

        # the half hourglass representing movement in the opposite direction, between the same vertices
        self.twin = twin
        # set up twin with swapped to/from vertices
        if (twin == None):
            self.twin = HalfHourglass("twin_" + str(id), v_to, v_from, strand_count, '', self)
            
        self.cw_next = self
        self.ccw_next = self

    def add_strand(self):
        # do not thicken phantom edges
        if (self.strand_count > 0): 
            self.strand_count += 1
            self.twin.strand_count += 1
    def thicken(self): # alias of add_strand
        self.add_strand()

    def remove_strand(self):
        # do not thin phantom edges
        if (self.strand_count > 1): 
            self.strand_count -= 1
            self.twin.strand_count -= 1
    def thin(self): # alias of remove_strand
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

    def get_cw_ith_strand(self, i, strand_i):
        ''' Returns the HalfHourglass and strand index i strands clockwise over around v_from.
            This corresponds to the ith left from the incoming strand.
            i: how many strands to travel. Relates to trip i.
            strand_i: the index of the incoming strand to start from. Recall that the first (0th) strand is the most counterclockwise.'''
        if strand_i + i < strand_count: return self, strand_i + i
        else: return self.cw_next.get_cw_ith_strand(i - self.strand_count + strand_i, 0)

    def get_ccw_ith_strand(self, i, strand_i):
        ''' Returns the HalfHourglass and strand index i strands counterclockwise over around v_from.
            This corresponds to the ith right from the incoming strand.
            i: how many strands to travel. Relates to trip i.
            strand_i: the index of the incoming strand to start from. Recall that the first (0th) strand is the most counterclockwise.'''
        if strand_i - i >= 0: return self, strand_i - i
        else: return self.ccw_next.get_ccw_ith_strand(i - strand_i, self.ccw_next.strand_count)  
    
    def is_phantom(self):
        return self.strand_count == 0
    def is_boundary(self): # alias for is_phantom
        return is_phantom()

    def get_angle(self):
        ''' Returns the angle between the vector from v_from to v_to and the x-axis.
            Returned value is between 0 and 2pi.'''
        angle = math.atan2(self.v_to.y-self.v_from.y, self.v_to.x-self.v_from.x)
        if angle < 0:
            angle += 2 * math.pi
        return angle