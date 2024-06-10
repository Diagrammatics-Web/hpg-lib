class Face:
    '''Represents a face of an hourglass plabic graph.'''
    def __init__(self, id, half_hourglass, label=''):
        ''' half_hourglass: a HalfHourglass adjacent to this face with this face on its left.'''
        self.id = id
        self.label = label

        self._half_hourglasses_head = half_hourglass
        self.boundary = False
        self.initialize_half_hourglasses(half_hourglass)

    def initialize_half_hourglasses(self, hh):
        ''' Sets this face up as the face for hh and all other half hourglasses in the same leftward loop,
            as well as the twin hourglasses in the reverse direction.
            Assumes that this is a valid face.
            hh: a HalfHourglass adjacent to this face with this face on its left.'''
        self._half_hourglasses_head = hh
        self.boundary = False
        iter = hh
        while True:
            # take the sharpest left turn
            iter.left_face = self
            iter = iter.twin()
            iter.right_face = self
            iter = iter.cw_next()
            if iter.is_boundary(): self.boundary = True
            if iter == hh: return

    @staticmethod
    def is_left_face_valid(hh):
        '''Checks if the face to the left of hh is valid, meaning there is a closed cycle with no loose paths inside.'''
        start_vertex = hh._v_from
        visited = [start_vertex]

        while (hh._v_to not in visited):
            visited.append(hh._v_to)
            hh = hh._twin
            hh = hh.cw_next()

        return hh._v_to == start_vertex and visited.len() > 2

    def is_square_move_valid(self):
        ''' Verifies that this face can perform a square move. In SL4, this requires the face to be made of 4 vertices,
            alternating filled/unfilled status, with multiplicity 1 edges in between.
            Vertices with one outgoing edge are contracted, while vertices with two outgoing edges are split into two vertices.'''
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
            The multiplicities of the edges are swapped.'''
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
            if v.simple_degree() == 4: new_vertices.append(v.square_move_expand(hh, hh.ccw_next()))
            else: removed_vertices.append(v.square_move_contract(hh.cw_next()))
        
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
        return _FaceIterator(self._half_hourglasses_head)

    # TESTING
    def print_vertices(self):   
        print(str([hh.v_from().id for hh in self]))

class _FaceIterator:
    ''' Internal class for iterating over the edges of a face. Iteration occurs beginning from face._half_hourglasses_head and continues counterclockwise.
        Modification of the list while iterating can cause errors with iteration.'''
    def __init__(self, head): 
        self.iter = head
        self.head = head
        self.begin = False
        
    def __iter__(self):
        return self
        
    def __next__(self):
        if self.iter == self.head: 
            if self.begin: raise StopIteration
            else: self.begin = True
        old = self.iter
        self.iter = self.iter.twin()
        self.iter = self.iter.cw_next()
        return old