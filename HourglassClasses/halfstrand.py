from .dihedralelement import DihedralElement

class HalfStrand(DihedralElement):
    '''Represents movement along one direction of a strand of an edge in an hourglass plabic graph.'''
    
    def __init__(self, id, hourglass, twin=None):
        '''Represents movement along one direction of a strand of an edge in an hourglass plabic graph.'''
        super().__init__(id)
        self._hourglass = hourglass
        
        # the half strand representing movement in the opposite direction, between the same vertices
        self._twin = HalfStrand(str(id) + "_t", hourglass.twin(), self) if twin is None else twin

    def hourglass(self):
        '''Returns the parent hourglass of this strand.'''
        return self._hourglass

    def v_to(self):
        return self._hourglass.v_to()
    def v_from(self):
        return self._hourglass.v_from()
    def left_face(self):
        return self._hourglass.left_face()
    def right_face(self):
        return self._hourglass.right_face()

    def get_last_strand_same_hourglass(self):
        ''' Returns the last strand clockwise owned by the same parent hourglass.
            Avoid using instead of HalfHourglass._half_strands_tail.'''
        for strand in self.cw_next().iterate_clockwise():
            if strand.hourglass() is not self.hourglass() or strand == self: return strand.cw_prev()

    def get_num_strands_same_hourglass(self):
        '''Returns the number of strands owned by the same parent hourglass.'''
        return self.hourglass().strand_count()