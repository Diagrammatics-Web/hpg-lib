class Face:
    ''' Represents a face of an hourglass plabic graph.
        A face can be infinite.'''
    def __init__(self, id, half_hourglass, label=''):
        ''' half_hourglass: a HalfHourglass adjacent to this face with this face on its right.'''
        self.id = id
        self.label = label

        self._half_hourglasses_head = half_hourglass
        self.boundary = False
        self.initialize_half_hourglasses(half_hourglass)

    def initialize_half_hourglasses(self, hh):
        ''' Sets this face up as the face for hh and all other half hourglasses in the same rightward loop,
            as well as the twin hourglasses in the reverse direction.
            hh: a HalfHourglass adjacent to this face with this face on its right.'''
        self._half_hourglasses_head = hh
        self.boundary = False
        for iter_hh in self:
            iter_hh.right_face = self
            iter_hh.twin().left_face = self
            if iter_hh.is_boundary(): self.boundary = True

    def is_square_move_valid(self):
        ''' Verifies that this face can perform a square move. In SL4, this requires the face to be made of 4 vertices,
            alternating filled/unfilled status, with multiplicity 1 edges in between.
            In a square move, vertices with one outgoing edge are contracted, while vertices with two outgoing edges are split into two vertices.'''
        count = 0
        should_be_filled = not self._half_hourglasses_head.v_from().filled # this check may be unecessary depending on the assumptions on the graph
        for hh in self:
            #checks
            if hh.multiplicity() != 1: return False
            if hh.v_to().filled != should_be_filled: return False
            if count > 4: return False
            # iterate
            count += 1
            should_be_filled = not should_be_filled
        return True

    def is_benzene_move_valid(self):
        ''' Verifies that this face can perform a square move. This requires the face to have an even number of
            vertices, with alternating filled/unfilled status, and with edges of alternating 1 or 2 multiplicity in between.
            In a benzene move, the multiplicities of the edges are swapped.'''
        count = 0
        should_be_filled = not self._half_hourglasses_head.v_from().filled # this check may be unecessary depending on the assumptions on the graph
        expected_mult = 1 if self._half_hourglasses_head.strand_count() == 1 else 2
        for hh in self:
            #checks
            if hh.multiplicity() != expected_mult: return False
            if hh.v_to().filled != should_be_filled: return False
            # iterate
            count += 1
            should_be_filled = not should_be_filled
            expected_mult = 3 - expected_mult # maps 2 -> 1 and 1 -> 2
        return count % 2 == 0
        
    def square_move(self):
        ''' Performs a square move on this face. Vertices with one outgoing edge are contracted, while vertices with two outgoing edges are split into two vertices.
            To verify that this move will be valid, call is_square_move_valid().
            OUTPUT: A tuple of arrays; the first is of created vertices that result from this move, the second is of all removed vertices.'''
        new_vertices = []
        removed_vertices = []
        ret_tuple = (new_vertices, removed_vertices)

        # diagnose vertices and perform expansion or contraction as necessary
        hourglasses = [hh for hh in self] # cache half hourglasses for safe iteration
        for hh in hourglasses:
            v = hh.v_from()
            if v.simple_degree() == 4: new_vertices.append(v.square_move_expand(hh, hh.cw_next()))
            else: removed_vertices.append(v.square_move_contract(hh.ccw_next()))
        
        return ret_tuple

    def benzene_move(self):
        ''' Performs a benzene move on this face. The multiplicities of its edges are swapped between 1 and 2.
            To verify that this move will be valid, call is_benzene_move_valid().'''
        thicken = self._half_hourglasses_head.strand_count() == 1
        for hh in self:
            if thicken: hh.thicken()
            else: hh.thin()
            thicken = not thicken

    def __iter__(self):
        '''Returns a HalfHourglass._TurnIterator. Iteration occurs beginning from face._half_hourglasses_head and continues clockwise.'''
        return self._half_hourglasses_head.iterate_right_turns()

    # TESTING
    def print_vertices(self):   
        print(str([hh.v_from().id for hh in self]))