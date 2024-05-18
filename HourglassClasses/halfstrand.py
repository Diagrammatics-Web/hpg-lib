from dihedralelement import DihedralElement

class HalfStrand(DihedralElement):
    def __init__(self, id, hourglass, twin=None):
        '''Represents movement along one direction of a strand of an edge in an hourglass plabic graph.'''
        self.id = id
        self._hourglass = hourglass
        
        # the half strand representing movement in the opposite direction, between the same vertices
        self._twin = HalfStrand("twin_" + str(id), hourglass.twin(), self) if twin == None else twin

    def hourglass(self):
        return self._hourglass

    def v_to(self):
        return self._hourglass.v_to()

    def v_from(self):
        return self._hourglass.v_from()