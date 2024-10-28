from .dihedralelement import DihedralElement

class HalfStrand(DihedralElement):
    '''Represents movement along one direction of a strand of an edge in an hourglass plabic graph.'''
    
    def __init__(self, id, hourglass, twin=None):
        '''Represents movement along one direction of a strand of an edge in an hourglass plabic graph.'''
        super().__init__(id)
        self._hourglass = hourglass
        
        # the half strand representing movement in the opposite direction, between the same vertices
        self._twin = HalfStrand(str(id) + "_t", hourglass.twin(), self) if twin is None else twin

    def __repr__(self):
        return "Strand " + str(self.get_index_in_hourglass()) + " (ID: " + str(self.id) + ") from " + str(self.v_from().id) + " to " + str(self.v_to().id)

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

    def get_index_in_hourglass(self):
        '''Returns the index of this strand in its parent hourglass, starting at 0 from the hourglass's _half_strand_head.'''
        i = 0
        for s in self.hourglass().iterate_strands():
            if s is self:
                return i
            i += 1

    def get_ith_trip_turn(self, i):
        print("get_ith_trip_turn(", i, ") called on ", self) # TESTING
        val = self.get_ith_right(i) if self.v_to().filled else self.get_ith_left(i)
        print("get_ith_trip_turn(", i, ") returned ", val) # TESTING
        return val

    def invert_ith_trip_turn(self, i):
        return self.get_cw_ith_element(i).twin() if self.v_from().filled else self.get_ccw_ith_element(i).twin()

    def get_trip(self, i, output='half_strands'):
        ''' Traverses the graph to compute trip i and returns an array of all visited half strands or half hourglasses.
            Can be called on any strand, even non-boundary strands; will find the entire trip regardless.
            i: computes trip_i by taking the ith left at unfilled/ith right at filled
            output: if output = 'half_strands', returns an array of HalfStrands. If output = 'half_hourglasses', returns HalfHourglasses.
                    Otherwise, returns the ids of the HalfStrands.'''
        #print("get_trip(" + str(i) + ") called on ", self) # TESTING
        trip_value = (lambda strand : strand) if output == 'half_strands' else (lambda strand : strand.hourglass()) if output == 'half_hourglasses' else (lambda strand : strand.id)

        visited = list()
        # Keep track of visited strands to avoid isolated trips. This is only possible if not starting on the boundary, as trip traversal is invertible.
        # An isolated trip occurs when a trip starting at an interior strand never reaches the boundary.
        visited_set = set()
        # Only check for membership in visited_set if we don't start on the boundary.
        is_valid = (lambda strand : not strand.v_to().boundary) if self.v_from().boundary else (lambda strand : not strand.v_to().boundary and strand not in visited_set)
        # Only add strand to visited_set if we don't start on the boundary. Note that the second lambda returns a tuple of (None, None) while still executing both functions.
        add_data = (lambda strand : visited.append(trip_value(strand))) if self.v_from().boundary else (lambda strand: (visited.append(trip_value(strand)), visited_set.add(strand)))
        
        strand = self
        while is_valid(strand):
            add_data(strand)
            strand = strand.get_ith_trip_turn(i)
        # Add the last strand leading to the boundary. Not necessary if we are in an isolated trip.
        if strand not in visited_set:
            add_data(strand)
        # If we are in an isolated trip, no further work is necessary.
        else:  
            #print("Final trip: ", visited) # TESTING
            return visited

        # We may need to find the other direction of the trip if we didn't start on the boundary.
        if (not self.v_from().boundary):
            
            strand = self.invert_ith_trip_turn(i)
            prepend_visited = [trip_value(strand)]
            
            while not strand.v_from().boundary:
                strand = strand.invert_ith_trip_turn(i)
                prepend_visited.append(trip_value(strand))
            
            prepend_visited.reverse()
            visited = prepend_visited + visited

        #print("Final trip: ", visited) # TESTING
        return visited