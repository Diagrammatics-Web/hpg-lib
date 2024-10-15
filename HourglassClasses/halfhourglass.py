import math
from .dihedralelement import DihedralElement
from .halfstrand import HalfStrand
from .idgenerator import ID

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
        self._multiplicity = multiplicity
        self.label = label
        
        # the half hourglass representing movement in the opposite direction, between the same vertices
        # twin will have swapped to/from vertices
        # only the "base" hourglass will need to set up strands
        if twin is None:
            self._twin = HalfHourglass(str(id) + "_t", v_to, v_from, multiplicity, '', self)

            # Create half strands and record head/tail
            if multiplicity == 0: 
                self._half_strands_head = None
                self._half_strands_tail = None
                self._twin._half_strands_head = None
                self._twin._half_strands_tail = None
            else:
                self._half_strands_head = HalfStrand(ID.get_new_id(str(id) + "_s"), self)
                self._twin._half_strands_head = self._half_strands_head.twin()
                for i in range(1, multiplicity): # runs multiplicity-1 times as we have already created a head strand
                    # potentially use thicken() instead of doing this manually?
                    strand = HalfStrand(ID.get_new_id(str(id) + "_s"), self)
                    self._half_strands_head.append_cw(strand)
                    self._twin._half_strands_head.append_cw(strand.twin())
                self._half_strands_tail = self._half_strands_head.cw_last()
                self._twin._half_strands_tail = self._half_strands_tail.twin()
        else: self._twin = twin
        
        self._left_face = None
        self._right_face = None

    def __repr__(self):
        return "HalfHourglass between " + str(self.v_from().id) + " to " + str(self.v_to().id) + " with multiplicity " + str(self.multiplicity())

    # Insert/remove overrides. These must be overridden as strands must be linked up as well.

    def insert_cw_next(self, element):
        super().insert_cw_next(element)
        if element._half_strands_head is None: return

        # link up strands
        next_strand = element.cw_next()._get_first_strand()
        prev_strand = next_strand.cw_prev() if next_strand is not None else None
        if next_strand is not None: 
            element._half_strands_tail.link_cw_next(next_strand)
            element._half_strands_head.link_cw_prev(prev_strand)

    def insert_ccw_next(self, element):
        super().insert_ccw_next(element)
        if element._half_strands_head is None: return

        # link up strands - same procedure as for insert_cw_next
        next_strand = element.cw_next()._get_first_strand()
        prev_strand = next_strand.cw_prev() if next_strand is not None else None
        if next_strand is not None: 
            element._half_strands_tail.link_cw_next(next_strand)
            element._half_strands_head.link_cw_prev(prev_strand)

    def remove(self):
        if self._half_strands_head is not None:
            self._half_strands_head.cw_prev().link_cw_next(self._half_strands_tail.cw_next())
            self._half_strands_head.link_cw_prev(self._half_strands_tail)
        super().remove()

    # Strand modification and accessor functions
    
    def add_strand(self):
        ''' Adds a strand to itself and its twin in the last position clockwise.
            Will not work on phantom edges.'''
        if (self.is_phantom()): raise RuntimeError("Cannot add a strand to a phantom/boundary edge.")
            
        new_strand = HalfStrand(ID.get_new_id(str(id) + "_"), self)
        self._half_strands_tail.insert_cw_next(new_strand)
        self._half_strands_tail.twin().insert_cw_next(new_strand.twin())
        self._half_strands_tail = new_strand
        self._twin._half_strands_tail = new_strand.twin()

        self._multiplicity += 1
        self._twin._multiplicity += 1
    def thicken(self): # alias
        self.add_strand()

    def remove_strand(self):
        ''' Removes the clockwise last strand for itself and its twin.
            Will not work on phantom edges or on edges with only 1 strand left.'''
        if (self.strand_count() <= 1): 
            if self.is_phantom(): raise RuntimeError("Cannot remove a strand from a phantom/boundary edge.") 
            else: raise RuntimeError("Cannot remove a strand from an edge with only one strand.")
            
        self._half_strands_tail = self._half_strands_tail.cw_prev()
        self._twin._half_strands_tail = self._twin._half_strands_tail.cw_prev()
        self._half_strands_tail.cw_next().remove()
        self._twin._half_strands_tail.cw_next().remove()
        
        self._multiplicity -= 1
        self._twin._multiplicity -= 1
    def thin(self): # alias
        self.remove_strand()

    def _get_first_strand(self):
        ''' Returns the first strand clockwise around v_from relative to this hourglass.
            Typically will return _half_strands_head, unless its multiplicity is 0.'''
        return self._half_strands_head if self._half_strands_head is not None or self._v_from.total_degree() == 0 else self._cw_next._get_first_strand()

    # Accessors

    def v_from(self):
        return self._v_from
    def v_to(self):
        return self._v_to
    def left_face(self):
        return self._left_face
    def right_face(self):
        return self._right_face

    def reparent(self, v):
        '''Changes this half hourglass's v_from to v, along with associated bookkeeping.'''
        self._v_from = v
        self.twin()._v_to = v

        self.remove() 
        
        v._insert_hourglass(self)

    def multiplicity(self):
        '''Returns the number of strands owned by this hourglass.'''
        return self._multiplicity
    def strand_count(self): # alias
        return self.multiplicity()
    
    def is_boundary(self):
        '''Returns True if this hourglass is on the boundary (or otherwise has multiplicity 0).'''
        return self._multiplicity == 0
    def is_phantom(self): # alias
        return self.is_boundary()

    def get_angle(self):
        ''' Returns the angle between the vector from v_from to v_to and the x-axis.
            Returned value is between 0 and 2pi.'''
        angle = math.atan2(self._v_to.y-self._v_from.y, self._v_to.x-self._v_from.x)
        if angle < 0:
            angle += 2 * math.pi
        return angle

    def iterate_left_turns(self):
        return _TurnIterator(self, False)
        
    def iterate_right_turns(self):
        return _TurnIterator(self, True)

class _TurnIterator:
    ''' Internal class for iterating left and right turns. A left/right turn is computed by
        taking an hourglass's twin's cw/ccw_next element.
        Modification of the list while iterating can cause errors with iteration.'''
    def __init__(self, head, turn_right): 
        self.head = head
        self.iter = head
        self.begin = False
        self.turn_right = turn_right
        
    def __iter__(self):
        return self
        
    def __next__(self):
        if self.iter is self.head:
            if self.begin: raise StopIteration
            else: self.begin = True
                
        old = self.iter
        if self.turn_right: self.iter = self.iter.right_turn()
        else: self.iter = self.iter.left_turn()
        return old   