r"""
Represents one direction of an hourglass edge in an hourglass plabic graph.

An edge is composed of strands, represented by a multiplicity, which can be traversed.

AUTHORS:

- Stefano L. Corno (2024-05-10): initial version

"""

# ****************************************************************************
#       Copyright (C) 2024 Stefano Corno <stlecorno@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

import math
from .dihedralelement import DihedralElement
from .halfstrand import HalfStrand
from .idgenerator import ID

class HalfHourglass(DihedralElement):
    r"""
    Represents movement on an edge from one vertex to another in an hourglass plabic graph.

    A HalfHourglass is always assumed to be between two Vertices and be linked to adjacent HalfHourglasses for v_from.
    """
    def __init__(self, id, v_from, v_to, multiplicity, twin=None):
        r"""
        Constructs a HalfHourglass with the given ID, between vertices v_from and v_to, and constructs `multiplicity` strands.
        Also contsructs its own twin.

        INPUT:

        - `id` -- hashable, unique object; if `None`, then created by combining `v_from` and `v_to`'s ID's.

        - `multiplicity` -- nonnegative integer; number of strands between from and to. if 0, this is an edge boundary. Assumed to be an integer `\geq 1`.

        - `twin` -- HalfHourglass (default: None); this parameter should be left blank. It is used internally to automatically construct this strand's twin.

        OUTPUT: HalfHourglass; the constructed HalfHourglass

        EXAMPLES:

        The HalfHourglass constructor automatically constructs its own twin.

            sage: hh = HalfHourglass('hh', None, None, 0)
            sage: hh.twin().id
            'hh_t'

        The HalfHourglass constructor automatically constructs HalfStrands based on `multiplicity`.

            sage: ID.reset_id()
            sage: hh = HalfHourglass('hh', None, None, 3)
            sage: hh._half_strands_head.id
            'hh_s0'

        .. WARNING::

            Do not assign any value to the twin parameter of this constructor.

            It is very unlikely you will need to directly construct HalfHourglasses; instead, use Vertex's create_hourglass_between function.
        """
        if id is None:
            id = f"h_{v_from.id}_{v_to.id}"
        super().__init__(id)
        self._v_from = v_from
        self._v_to = v_to
        self._multiplicity = multiplicity
        self.label = [] # Used by HPG for separation labeling

        # the half hourglass representing movement in the opposite direction, between the same vertices
        # twin will have swapped to/from vertices
        # only the "base" hourglass will need to set up strands
        if twin is None:
            self._twin = HalfHourglass(None, v_to, v_from, multiplicity, self)

            # Create half strands and record head/tail
            if multiplicity == 0:
                self._half_strands_head = None
                self._half_strands_tail = None
                self.twin()._half_strands_head = None
                self.twin()._half_strands_tail = None
            else:
                self._half_strands_head = HalfStrand(ID.get_new_id(f"{id}_s"), self)
                self.twin()._half_strands_head = self._half_strands_head.twin()
                for i in range(1, multiplicity): # runs multiplicity-1 times as we have already created a head strand
                    # potentially use thicken() instead of doing this manually?
                    strand = HalfStrand(ID.get_new_id(f"{id}_s"), self)
                    self._half_strands_head.append_cw(strand)
                    self.twin()._half_strands_head.append_cw(strand.twin())
                self._half_strands_tail = self._half_strands_head.cw_last()
                self.twin()._half_strands_tail = self._half_strands_tail.twin()
        else: self._twin = twin

        self._left_face = None
        self._right_face = None

    def __repr__(self):
        r"""
        Returns a String representation of this HalfHourglass, providing its ID, vertices, and multiplicity.

        OUTPUT: str

        EXAMPLES:

            sage: ID.reset_id()
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: hh.__repr__()
            'HalfHourglass between v1 to v2 with multiplicity 1'
        """
        return f"HalfHourglass (ID: {self.id}) from {'None' if self.v_from() is None else self.v_from().id} to {'None' if self.v_to() is None else self.v_to().id} with multiplicity {self.multiplicity()}"

    # Insert/remove overrides. These must be overridden as strands must be linked up as well.

    def insert_cw_next(self, element):
        r"""
        Inserts element into the list as the next clockwise element, including linking its HalfStrands.
        This function is an override of the DihedralElement implementation.

        INPUT:

        - `element` -- HalfHourglass; the element to insert.

        EXAMPLES:

        This example constructs a list of three HalfHourglasses using insert_cw_next.

            sage: ID.reset_id()
            sage: hh1 = HalfHourglass('hh1', None, None, 1)
            sage: hh2 = HalfHourglass('hh2', None, None, 1)
            sage: hh3 = HalfHourglass('hh3', None, None, 1)
            sage: hh1.insert_cw_next(hh2)
            sage: hh1.insert_cw_next(hh3)
            sage: hh1.get_elements_as_list() == [hh1, hh3, hh2]
            True

        This example demonstrates how HalfStrands are connected.

            sage: [s.id for s in hh1._half_strands_head]
            ['hh1_s0', 'hh3_s2', 'hh2_s1']

        This example demonstrates how inserting HalfHourglasses with no HalfStrands is handled properly.

            sage: hh3.remove()
            sage: hh3 = HalfHourglass('hh3', None, None, 0)
            sage: hh1.insert_cw_next(hh3)
            sage: [s.id for s in hh1._half_strands_head]
            ['hh1_s0', 'hh2_s1']

        .. NOTE::

            This function is aliased by insert_ccw_prev and append_ccw.
        """
        super().insert_cw_next(element)
        if element._half_strands_head is None: return

        # link up strands
        next_strand = element.cw_next()._get_first_strand()
        if next_strand is None: return

        prev_strand = next_strand.cw_prev()
        element._half_strands_tail.link_cw_next(next_strand)
        element._half_strands_head.link_cw_prev(prev_strand)
    # Redefinitions of aliases necessary for inherited class override
    insert_ccw_prev = insert_cw_next # alias
    append_ccw = insert_cw_next # alias

    def insert_ccw_next(self, element):
        r"""
        Inserts element into the list as the next counterclockwise element, including linking its HalfStrands.
        This function is an override of the DihedralElement implementation.

        INPUT:

        - `element` -- HalfHourglass; the element to insert.

        EXAMPLES:

        This example constructs a list of three HalfHourglasses using insert_ccw_next.

            sage: ID.reset_id()
            sage: hh1 = HalfHourglass('hh1', None, None, 1)
            sage: hh2 = HalfHourglass('hh2', None, None, 1)
            sage: hh3 = HalfHourglass('hh3', None, None, 1)
            sage: hh1.insert_ccw_next(hh2)
            sage: hh1.insert_ccw_next(hh3)
            sage: hh1.get_elements_as_list() == [hh1, hh2, hh3]
            True

        This example demonstrates how HalfStrands are connected.

            sage: [s.id for s in hh1._half_strands_head]
            ['hh1_s0', 'hh2_s1', 'hh3_s2']

        This example demonstrates how inserting HalfHourglasses with no HalfStrands is handled properly.

            sage: hh3.remove()
            sage: hh3 = HalfHourglass('hh3', None, None, 0)
            sage: hh1.insert_ccw_next(hh3)
            sage: [s.id for s in hh1._half_strands_head]
            ['hh1_s0', 'hh2_s1']

        .. NOTE::

            This function is aliased by insert_cw_prev and append_cw.
        """
        super().insert_ccw_next(element)
        if element._half_strands_head is None: return

        # link up strands - same procedure as for insert_cw_next
        next_strand = element.cw_next()._get_first_strand()
        if next_strand is None: return

        prev_strand = next_strand.cw_prev()
        element._half_strands_tail.link_cw_next(next_strand)
        element._half_strands_head.link_cw_prev(prev_strand)
    # Redefinitions of aliases necessary for inherited class override
    insert_cw_prev = insert_ccw_next # alias
    append_cw = insert_ccw_next # alias

    def remove(self):
        r"""
        Removes this HalfHourglass from its list, including unlinking its HalfStrands.
        The element will also become its own list to facilitate reuse.
        This function is an override of the DihedralElement implementation.

        EXAMPLES:

            sage: hh1 = HalfHourglass('hh1', None, None, 1)
            sage: hh2 = HalfHourglass('hh2', None, None, 1)
            sage: hh3 = HalfHourglass('hh3', None, None, 1)
            sage: hh1.insert_ccw_next(hh2)
            sage: hh1.insert_ccw_next(hh3)
            sage: hh2.remove()
            sage: [hh for hh in hh1] == [hh1, hh3]
            True

        This example demonstrates how HalfStrands are automatically relinked upon removal.

            sage: hh1._half_strands_head.get_num_elements()
            2
        """
        if self._half_strands_head is not None:
            self._half_strands_head.cw_prev().link_cw_next(self._half_strands_tail.cw_next())
            self._half_strands_head.link_cw_prev(self._half_strands_tail)
        super().remove()

    def reparent(self, v):
        r"""
        Changes this half hourglass's v_from to v, performing all appropriate bookkeeping.

        INPUT:

        - `v` -- Vertex; The new vertex this hourglass should come from.

        EXAMPLES:

            sage: ID.reset_id()
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: v3 = Vertex('v3', 1, 0, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: hh.reparent(v3)
            sage: hh
            HalfHourglass (ID: v1_v2) from v3 to v2 with multiplicity 1
        """
        self.v_from()._remove_hourglass(self)
        self._v_from = v
        self.id = f"h_{self._v_from.id}_{self._v_to.id}"
        v._insert_hourglass(self)

        # Reinsert twin as it may now have swapped places
        self.twin().v_from()._remove_hourglass(self.twin())
        self.twin()._v_to = v
        self.twin().id = f"h_{self._v_to.id}_{self._v_from.id}"
        self.twin().v_from()._insert_hourglass(self.twin())


    # Strand modification and accessor functions

    def add_strand(self):
        r"""
        Adds a strand to itself and its twin in the last position clockwise.
        Will not work on phantom edges (edges with no strands).

        EXAMPLES:

            sage: ID.reset_id()
            sage: hh = HalfHourglass('hh', None, None, 1)
            sage: hh.add_strand()
            sage: [s.id for s in hh._half_strands_head]
            ['hh_s0', 'hh_1']

        It is an error to add_strand on a phantom edge.

            sage: hh = HalfHourglass('hh', None, None, 0)
            sage: hh.add_strand()
            RuntimeError: Cannot add a strand to a phantom/boundary edge.

        .. NOTE::

            This function is aliased by thicken.
        """
        if (self.is_phantom()): raise RuntimeError("Cannot add a strand to a phantom/boundary edge.")

        new_strand = HalfStrand(ID.get_new_id(str(self.id) + "_"), self)
        self._half_strands_tail.insert_cw_next(new_strand)
        self._half_strands_tail.twin().insert_cw_next(new_strand.twin())
        self._half_strands_tail = new_strand
        self.twin()._half_strands_tail = new_strand.twin()

        self._multiplicity += 1
        self.twin()._multiplicity += 1
    thicken = add_strand # alias

    def remove_strand(self):
        r"""
        Removes the clockwise last strand for itself and its twin.
        Will not work on phantom edges or on edges with only one strand left.

        EXAMPLES:

            sage: ID.reset_id()
            sage: hh = HalfHourglass('hh', None, None, 2)
            sage: hh.remove_strand()
            sage: [s.id for s in hh._half_strands_head]
            ['hh_s0']

        It is an error to remove_strand on an edge with only one strand.

            sage: hh.remove_strand()
            RuntimeError: Cannot remove a strand from an edge with only one strand.

        It is an error to remove_strand on a phantom edge.

            sage: hh = HalfHourglass('hh', None, None, 0)
            sage: hh.remove_strand()
            RuntimeError: Cannot remove a strand to a phantom/boundary edge.

        .. NOTE::

            This function is aliased by thin.
        """
        if (self.strand_count() <= 1):
            if self.is_phantom(): raise RuntimeError("Cannot remove a strand from a phantom/boundary edge.")
            else: raise RuntimeError("Cannot remove a strand from an edge with only one strand.")

        self._half_strands_tail = self._half_strands_tail.cw_prev()
        self.twin()._half_strands_tail = self.twin()._half_strands_tail.cw_prev()
        self._half_strands_tail.cw_next().remove()
        self.twin()._half_strands_tail.cw_next().remove()

        self._multiplicity -= 1
        self.twin()._multiplicity -= 1
    thin = remove_strand # alias

    def _get_first_strand(self):
        r"""
        Returns the first strand clockwise around v_from relative to this hourglass.
        Typically will return _half_strands_head, unless its multiplicity is 0.
        If there are no strands among adjacent hourglasses, None will be returned instead.

        OUTPUT: HalfStrand

        EXAMPLES:

            sage: ID.reset_id()
            sage: hh1 = HalfHourglass('hh1', None, None, 1)
            sage: hh1.insert_cw_next(HalfHourglass('hh2', None, None, 1))
            sage: hh1._get_first_strand().id
            'hh1_s0'

        This example demonstrates when the hourglass owns no strands.

            sage: hh1 = HalfHourglass('hh1', None, None, 0)
            sage: hh1.insert_cw_next(HalfHourglass('hh2', None, None, 1))
            sage: hh1._get_first_strand().id
            'hh2_s2'
        """
        if self._half_strands_head is not None: return self._half_strands_head
        for hh in self:
            if hh.strand_count() > 0: return hh._half_strands_head
        return None

    # Accessors

    def v_from(self):
        r"""
        Returns the vertex this HalfHourglass traverses from.

        OUTPUT: Vertex

        EXAMPLES:

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: hh.v_from().id
            'v1'
        """
        return self._v_from

    def v_to(self):
        r"""
        Returns the vertex this HalfHourglass traverses to.

        OUTPUT: Vertex

        EXAMPLES:

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: hh.v_to().id
            'v2'
        """
        return self._v_to

    def left_face(self):
        r"""
        Returns the Face on the left of this HalfHourglass.

        OUTPUT: Face

        EXAMPLES:

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: face = Face('face', hh)
            sage: hh.left_face().id
            'face'
        """
        return self._left_face

    def right_face(self):
        r"""
        Returns the Face on the left of this HalfHourglass.

        OUTPUT: Face

        EXAMPLES:

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: face = Face('face', hh)
            sage: hh.left_face().id
            'face'
        """
        return self._right_face

    def multiplicity(self):
        r"""
        Returns the number of strands owned by this hourglass.

        OUTPUT: integer

        EXAMPLES:

            sage: hh = HalfHourglass('hh', None, None, 1)
            sage: hh.multiplicity()
            1

            sage: hh.thicken()
            sage: hh.multiplicity()
            2

        .. NOTE::

            This function is aliased by strand_count.
        """
        return self._multiplicity
    strand_count = multiplicity # alias

    def is_boundary(self):
        r"""
        Returns True if this hourglass is on the boundary (or otherwise has multiplicity 0).

        OUTPUT: boolean

        EXAMPLES:

            sage: hh = HalfHourglass('hh', None, None, 1)
            sage: hh.is_boundary()
            False

            sage: hh = HalfHourglass('hh', None, None, 0)
            sage: hh.is_boundary()
            True

        .. NOTE::

            This function is aliased by is_phantom.
        """
        return self._multiplicity == 0
    is_phantom = is_boundary # alias

    def get_angle(self):
        r"""
        Returns the angle between the vector from v_from to v_to and the x-axis.
        Returned value is between 0 and 2pi.

        OUTPUT: float

        EXAMPLES:

            sage: hh = Vertex.create_hourglass_between(Vertex('v1', 0, 0, True), Vertex('v2', 1, 0, True), 1)
            sage: hh.get_angle()
            0.0

            sage: hh = Vertex.create_hourglass_between(Vertex('v1', 1, 1, True), Vertex('v2', -1, -1, True), 1)
            sage: hh.get_angle()
            3.9269908169872414

        This example demonstrates output close to 2pi.

            sage: hh = Vertex.create_hourglass_between(Vertex('v1', 0, 0, True), Vertex('v2', 1, -0.01, True), 1)
            sage: hh.get_angle()
            6.273185640492921
        """
        angle = math.atan2(self.v_to().y - self.v_from().y, self.v_to().x - self.v_from().x)
        if angle < 0:
            angle += 2 * math.pi
        return angle

    def iterate_left_turns(self):
        r"""
        Iterates over the left turns of this HalfHourglass.
        This can be used to find the HalfHourglasses in the left face of this HalfHourglass.

        OUTPUT: _TurnIterator; set to iterate left turns

        EXAMPLES:

        This example constructs a face and iterates over its hourglasses.

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 1, 0, True)
            sage: v3 = Vertex('v3', 1, 1, True)
            sage: v4 = Vertex('v4', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v2, v3, 1)
            sage: Vertex.create_hourglass_between(v3, v4, 1)
            sage: Vertex.create_hourglass_between(v4, v1, 1)
            sage: [ihh.id for ihh in hh.iterate_left_turns()]
            ['v1_v2', 'v2_v3', 'v3_v4', 'v4_v1']

        This can also be used to iterate the hourglasses of an unbounded face.

            sage: [ihh.id for ihh in hh.twin().iterate_left_turns()]
            ['v1_v2_t', 'v4_v1_t', 'v3_v4_t', 'v2_v3_t']

        This example demonstrates what happens when iterating over a single hourglass not connected to anything.

            sage: v3.clear_hourglasses()
            sage: v4.clear_hourglasses()
            sage: [ihh.id for ihh in hh.iterate_left_turns()]
            ['v1_v2', 'v1_v2_t']
        """
        return _TurnIterator(self, False)

    def iterate_right_turns(self):
        r"""
        Iterates over the right turns of this HalfHourglass.
        This can be used to find the HalfHourglasses in the right face of this HalfHourglass.

        OUTPUT: _TurnIterator; set to iterate right turns

        EXAMPLES:

        This example constructs a face and iterates over its hourglasses.

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', -1, 0, True)
            sage: v3 = Vertex('v3', -1, 1, True)
            sage: v4 = Vertex('v4', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v2, v3, 1)
            sage: Vertex.create_hourglass_between(v3, v4, 1)
            sage: Vertex.create_hourglass_between(v4, v1, 1)
            sage: [ihh.id for ihh in hh.iterate_right_turns()]
            ['v1_v2', 'v2_v3', 'v3_v4', 'v4_v1']

        This can also be used to iterate the hourglasses of an unbounded face.

            sage: [ihh.id for ihh in hh.twin().iterate_right_turns()]
            ['v1_v2_t', 'v4_v1_t', 'v3_v4_t', 'v2_v3_t']

        This example demonstrates what happens when iterating over a single hourglass not connected to anything.

            sage: v3.clear_hourglasses()
            sage: v4.clear_hourglasses()
            sage: [ihh.id for ihh in hh.iterate_right_turns()]
            ['v1_v2', 'v1_v2_t']
        """
        return _TurnIterator(self, True)

    def iterate_strands(self):
        r"""
        Iterates over the HalfStrands owned by this HalfHourglass, in clockwise order.

        OUTPUT: _StrandIterator

        EXAMPLES:

            sage: ID.reset_id()
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 2)
            sage: [s.id for s in hh.iterate_strands()]
            ['v1_v2_s0', 'v1_v2_s1', 'v1_v2_s2']

        This will only iterate over the strands owned by this HalfHourglass, even if there are other adjacent strands.

            sage: v3 = Vertex('v3', 0, -1, True)
            sage: Vertex.create_hourglass_between(v1, v3, 2)
            sage: [s.id for s in hh.iterate_strands()]
            ['v1_v2_s0', 'v1_v2_s1', 'v1_v2_s2']

        This example demonstrates what happens when iterating over an hourglass with no strands.

            sage: hh = HalfHourglass('hh', None, None, 0)
            sage: [s.id for s in hh.iterate_strands()]
            []
        """
        return _StrandIterator(self)

class _TurnIterator:
    r"""
    Internal class for iterating left and right turns. A left/right turn is computed by
    taking an hourglass's twin's cw/ccw_next element.
    Modification of the list while iterating can cause errors with iteration.
    """
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
        self.iter = self.iter.right_turn() if self.turn_right else self.iter.left_turn()
        return old

class _StrandIterator:
    r"""
    Internal class for iterating over the strands owned by this hourglass.
    """
    def __init__(self, hh):
        self.hh = hh
        self.iter = hh._half_strands_head
        self.end_strand = hh._half_strands_tail.cw_next() if hh._half_strands_head is not None else None
        # We only care about looping around if the head and tail are linked
        self.begin = self.iter is not self.end_strand

    def __iter__(self):
        return self

    def __next__(self):
        # Iteration immediately ends if hh has no strands
        if self.iter is None: raise StopIteration
        if self.iter is self.end_strand:
            if self.begin: raise StopIteration
            else: self.begin = True

        old = self.iter
        self.iter = self.iter.cw_next()
        return old


