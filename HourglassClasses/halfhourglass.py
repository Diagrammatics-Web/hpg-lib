import math
from .dihedralelement import DihedralElement
from .halfstrand import HalfStrand

class HalfHourglass(DihedralElement):
    ''' Represents part of an edge from one vertex to another in an hourglass plabic graph.
        When iterating over strands, the head strand is the most counterclockwise.'''
    def __init__(self, id, v_from, v_to, multiplicity, label='', twin=None):
        ''' id: an object, assumed unique, should be hashable
            multiplicity: number of strands between from and to. if 0, this is an edge boundary
            label: an object'''
        super().__init__(id)
        self._v_from = v_from
        self._v_to = v_to
        self.label = label
        
        # the half hourglass representing movement in the opposite direction, between the same vertices
        # twin will have swapped to/from vertices
        # only the "base" hourglass will need to set up strands
        if twin == None:
            self._twin = HalfHourglass("twin_" + str(id), v_to, v_from, multiplicity, '', self)

            # Create half strands
            if multiplicity == 0: 
                self._half_strands_head = None
                self._twin._half_strands_head = None
            else:
                self._half_strands_head = HalfStrand(str(id) + "_s0", self)
                self._twin._half_strands_head = self._half_strands_head.twin()
                for i in range(1, multiplicity):
                    strand = HalfStrand(str(id) + "_s" + str(i), self)
                    self._half_strands_head.append_cw(strand)
                    self._twin._half_strands_head.append_cw(strand.twin())
        else: self._twin = twin

        self.left_face = None
        self.right_face = None

    # Insert/remove overrides. These must be overridden as strands must be linked up as well.

    def insert_cw_next(self, element):
        super().insert_cw_next(element)
        if element._half_strands_head == None: return

        # link up strands
        next_strand = element.cw_next()._get_first_strand()
        prev_strand = next_strand.cw_prev() if next_strand != None else None
        if next_strand != None: element._half_strands_head.cw_last().set_cw_next(next_strand)
        if prev_strand != None: element._half_strands_head.set_cw_prev(prev_strand)

    def insert_ccw_next(self, element):
        super().insert_ccw_next(element)
        if element._half_strands_head == None: return

        # link up strands - same procedure as for insert_cw_next
        next_strand = element.cw_next()._get_first_strand()
        prev_strand = next_strand.cw_prev() if next_strand != None else None
        if next_strand != None: element._half_strands_head.cw_last().set_cw_next(next_strand)
        if prev_strand != None: element._half_strands_head.set_cw_prev(prev_strand)

    def remove(self):
        if self._half_strands_head != None:
            iter = self._half_strands_head
            ''' either list is empty, we will remove iter when it is 
             its own cw_next (see DihedralElement.remove()), or 
             we will eventually run into another hourglass's strands'''
            while iter.cw_next() != None and iter.hourglass() == self: 
                iter = iter.cw_next()
                iter.cw_prev().remove()
        super().remove()

    # Strand modification and accessor functions
    
    def add_strand(self):
        ''' Adds a strand to itself (and its twin) in the last position clockwise.
            Will not work on phantom edges.'''
        if (self.is_phantom()): return
            
        last_strand = self._half_strands_head.get_last_strand_same_hourglass()
        new_strand = HalfStrand(str(id) + "_s", self) # warning: ID will not be unique
        last_strand.insert_cw_next(new_strand)
        last_strand.twin().insert_cw_next(new_strand.twin())
    def thicken(self): # alias
        self.add_strand()

    def remove_strand(self):
        ''' Removes the clockwise last strand for itself and its twin.
            Will not work on phantom edges or on edges with only 1 strand left.'''
        if (self.strand_count() <= 1): return 
            
        last_strand = self._half_strands_head.get_last_strand_same_hourglass()
        last_strand.remove()
        last_strand.twin().remove()
    def thin(self): # alias
        self.remove_strand()

    def _get_first_strand(self):
        ''' Returns the first strand clockwise around v_from relative to this hourglass.
            Typically will return _half_strands_head, unless its multiplicity is 0.'''
        return self._half_strands_head if self._half_strands_head != None or self._v_from.total_degree() == 0 else self._cw_next._get_first_strand()

    # End strand accessor and modification functions

    def v_from(self):
        return self._v_from
    def v_to(self):
        return self._v_to

    def strand_count(self):
        if self.is_phantom(): return 0
        return self._half_strands_head.get_num_strands_same_hourglass()
    def multiplicity(self): #alias
        return self.strand_count()
    
    def is_phantom(self):
        return self._half_strands_head == None
    def is_boundary(self): # alias for is_phantom
        return is_phantom()

    def get_angle(self):
        ''' Returns the angle between the vector from v_from to v_to and the x-axis.
            Returned value is between 0 and 2pi.'''
        angle = math.atan2(self._v_to.y-self._v_from.y, self._v_to.x-self._v_from.x)
        if angle < 0:
            angle += 2 * math.pi
        return angle