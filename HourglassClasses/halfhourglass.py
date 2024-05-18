import math
from dihedralelement import DihedralElement

class HalfHourglass(DihedralElement):
    ''' Represents part of an edge from one vertex to another in an hourglass plabic graph.
        When iterating over strands, the head strand is the most counterclockwise.'''
    def __init__(self, id, v_from, v_to, multiplicity, label='', twin=None):
        ''' id: an object, assumed unique, should be hashable
            multiplicity: number of strands between from and to. if 0, this is an edge boundary
            label: an object'''
        super().__init__(self)
        self.id = id
        self._v_from = v_from
        self._v_to = v_to
        self.label = label
        
        # the half hourglass representing movement in the opposite direction, between the same vertices
        # twin will have swapped to/from vertices
        # only the "base" hourglass will need to set up strands
        if twin == None:
            self._twin = HalfHourglass("twin_" + str(id), v_to, v_from, strand_count, '', self)

            # Create half strands
            if multiplicity == 0: 
                self._half_strands_head = None
                self._twin._half_strands_head = None
            else:
                self._half_strands_head = HalfStrand(str(id) + "_s0", self)
                self._twin._half_strands_head = self._half_strands_head.twin()
                for i in range(1, multiplicity):
                    strand = HalfStrand(str(id) + "_s" + i, self)
                    self._half_strands_head.append_cw(strand)
                    self._twin._half_strands_head.append_cw(strand.twin())
        else: self._twin = twin

    # Insert/remove overrides. These must be overridden as strands must be linked up as well.

    def insert_cw_next(self, element):
        super().insert_cw_next(element)
        if element._half_strands_head == None: return

        # link up strands
        next_strand = element.cw_next().get_first_strand()
        prev_strand = next_strand.cw_prev() if next_strand != None else None
        if next_strand != None: element._half_strands_head.cw_last().set_cw_next(next_strand)
        if prev_strand != None: element._half_strands_head.set_cw_prev(prev_strand)

    def insert_cw_next(self, element):
        super().insert_cw_next(element)
        if element._half_strands_head == None: return

        # link up strands
        next_strand = element.cw_next().get_first_strand()
        prev_strand = next_strand.cw_prev() if next_strand != None else None
        if next_strand != None: element._half_strands_head.cw_last().set_cw_next(next_strand)
        if prev_strand != None: element._half_strands_head.set_cw_prev(prev_strand)

    def remove(self):
        if self_half_strands_head != None:
            iter = self_half_strands_head
            while iter.hourglass() == self and iter.cw_next() != iter: 
                iter = iter.cw_next()
                iter.cw_prev().remove()
        super().remove()

    # Strand modification and accessor functions
    
    def add_strand(self): #TODO
        ''' Adds a strand to itself in the last position clockwise.
            Will not work on phantom edges.'''
        if (self.is_phantom()): return
        self.strand_count += 1
        self.twin.strand_count += 1
    def thicken(self): # alias of add_strand
        self.add_strand()

    def remove_strand(self): #TODO
        ''' Removes the clockwise last strand.
            Will not work on phantom edges or on edges with only 1 strand left.'''
        if (self.strand_count <= 1): return 
        self.strand_count -= 1
        self.twin.strand_count -= 1
    def thin(self): # alias of remove_strand
        self.remove_strand()

    def get_cw_ith_strand(self, i, strand_i): #TODO
        ''' Returns the HalfHourglass and strand index i strands clockwise over around v_from.
            This corresponds to the ith left from the incoming strand.
            i: how many strands to travel. Relates to trip i.
            strand_i: the index of the incoming strand to start from. Recall that the first (0th) strand is the most counterclockwise.'''
        if strand_i + i < strand_count: return self, strand_i + i
        else: return self._cw_next.get_cw_ith_strand(i - self.strand_count + strand_i, 0)

    def get_ccw_ith_strand(self, i, strand_i): #TODO
        ''' Returns the HalfHourglass and strand index i strands counterclockwise over around v_from.
            This corresponds to the ith right from the incoming strand.
            i: how many strands to travel. Relates to trip i.
            strand_i: the index of the incoming strand to start from. Recall that the first (0th) strand is the most counterclockwise.'''
        if strand_i - i >= 0: return self, strand_i - i
        else: return self._ccw_next.get_ccw_ith_strand(i - strand_i, self.ccw_next.strand_count)  

    def get_first_strand(self):
        ''' Returns the first strand clockwise around v_from relative to this hourglass.
            Typically will return _half_strands_head, unless its multiplicity is 0.'''
        return self._half_strands_head if self._half_strands_head != None or self._v_from.total_degree() == 0 else self._cw_next.get_first_strand()

    # End strand accessor and modification functions

    def v_from(self):
        return self._v_from
    def v_to():
        return self._v_to

    def strand_count(self): #TODO
        pass
    def multiplicity(self): #alias
        return self.strand_count()
    
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