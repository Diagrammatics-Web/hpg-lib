class Face:
    '''Represents a face of an hourglass plabic graph.'''
    def __init__(self, id, label, half_hourglass):
         '''half_hourglass: a HalfHourglass adjacent to this face with this face on its left.'''
        self.id = id
        self.label = label

        self._half_hourglasses_head = half_hourglass
        self.boundary = False
        self.initialize_half_hourglasses(half_hourglass)

    def initialize_half_hourglasses(self, hh):
        ''' Sets itself up as the face for hh and all other half hourglasses in the same leftward loop,
            as well as the twin hourglasses in the reverse direction.
            Assumes that following hh creates a cycle.
            hh: a HalfHourglass adjacent to this face with this face on its left.'''
        self._half_hourglasses_head = hh
        self.boundary = False
        iter = hh
        while True:
            iter.left_face = self
            iter = iter.twin()
            iter.right_face = self
            iter = iter.cw_next()
            if iter.is_boundary(): self.boundary = True
            if iter == hh: break