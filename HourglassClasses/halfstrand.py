from .dihedralelement import DihedralElement

class HalfStrand(DihedralElement):
    def __init__(self, id, hourglass, twin=None):
        '''Represents movement along one direction of a strand of an edge in an hourglass plabic graph.'''
        super().__init__(id)
        self._hourglass = hourglass
        
        # the half strand representing movement in the opposite direction, between the same vertices
        self._twin = HalfStrand("twin_" + str(id), hourglass.twin(), self) if twin == None else twin

    def hourglass(self):
        return self._hourglass

    def v_to(self):
        return self._hourglass.v_to()

    def v_from(self):
        return self._hourglass.v_from()

    def get_last_strand_same_hourglass(self):
        '''Returns the last strand clockwise owned by the same parent hourglass.'''
        iter = self.cw_next()
        # Eventually, we will reach another hourglass or loop back around
        while iter.hourglass() == self.hourglass() and iter != self:
            iter = iter.cw_next()
        return iter.cw_prev()

    def get_num_strands_same_hourglass(self):
        '''Returns the number of strands owned by the same parent hourglass.
         Assumes you are beginning from the most counterclockwise strand for this hourglass.'''
        count = 1
        iter = self.cw_next()
        # Eventually, we will reach another hourglass or loop back around
        while iter.hourglass() == self.hourglass() and iter != self:
            count += 1
            iter = iter.cw_next()
        return count