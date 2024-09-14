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

    def get_ith_trip_turn(self, i):
        return self.get_ith_right(i) if self.v_to().filled else self.get_ith_left(i)

    def invert_ith_trip_turn(self, i):
        return self.get_cw_ith_element(i).twin() if self.v_from().filled else self.get_ccw_ith_element(i).twin()

    def get_trip(self, i, output='half_strands'):
        ''' Traverses the graph to compute trip i and returns an array of all visited half strands or half hourglasses.
            Can be called on any strand, even non-boundary strands; will find the entire trip regardless.
            i: computes trip_i by taking the ith left at unfilled/ith right at filled
            output: if output = 'half_strands', returns an array of HalfStrands. If output = 'half_hourglasses', returns HalfHourglasses.
                    Otherwise, returns the ids of the HalfStrands.'''

        visited = [self]

        strand = self
        while not strand.v_to().boundary:
            strand = strand.get_ith_trip_turn(i)
            visited.append(strand if output == 'half_strands' else strand.hourglass() if output == 'half_hourglasses' else strand.id)

        # We may need to find the other direction of the trip
        if not self.v_from().boundary:
            strand = self.invert_ith_trip_turn(i)
            prepend_visited = [strand]
            
            while not strand.v_from().boundary:
                strand = strand.invert_ith_trip_turn(i)
                prepend_visited.append(strand if output == 'half_strands' else strand.hourglass() if output == 'half_hourglasses' else strand.id)
            
            prepend_visited.reverse()
            visited = prepend_visited + visited

        return visited