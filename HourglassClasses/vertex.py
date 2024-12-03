r"""
Represents a vertex in an hourglass plabic graph.

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

from .halfhourglass import HalfHourglass
from .idgenerator import ID

class Vertex:
    r"""
    Represents a vertex in an hourglass plabic graph.
    A vertex can be filled (black) or unfilled (white), and is connected to other
    vertices through hourglass edges.
    When traversing an HPG, trip i turns at the ith left on an unfilled vertex
    and the ith right on a filled vertex.
    """
    def __init__(self, id, x, y, filled, boundary=False, label=''):
        r"""
        Constructs a Vertex with the given ID, x and y positions, and filled and boundary statuses.

        INPUT:

        - `id` -- an object, assumed unique, should be hashable

        - ``x`` -- float; the x-position of this Vertex

        - ``y`` -- float; the y-position of this Vertex

        - `filled` -- boolean; True for filled/black, False for unfilled/white

        - `boundary` -- boolean (default: False); True if on the boundary

        - `label` -- object (default: '')

        OUTPUT: Vertex; the constructed Vertex
        """
        self.id = id
        self.x = x
        self.y = y
        self.filled = filled
        self.boundary = boundary
        self.label = label

        r"""
        Some half hourglass around this vertex. When the graph is properly embedded,
        the vertex will attempt to maintain this as the the one making the smallest
        angle with the x-axis during insertions and deletions, but this behavior may
        not be guaranteed.
        """
        self._half_hourglasses_head = None

    def __repr__(self):
        r"""
        Returns a String representation of this Vertex, providing its ID, position, and filled status.

        OUTPUT: str

        EXAMPLES:

            sage: v = Vertex('v', 0, 0, True)
            sage: v
            Vertex v at (0, 0), filled
        """
        return "Vertex " + str(self.id) + " at (" + str(self.x) + ", " + str(self.y) + "), " + ("filled" if self.filled else "unfilled")

    def _reset_head(self):
        r"""
        Resets _half_hourglasses_head to the hourglass with the smallest angle.
        """
        while self._half_hourglasses_head.get_angle() > self._half_hourglasses_head.cw_next().get_angle():
            self._half_hourglasses_head = self._half_hourglasses_head.cw_next()

    # Hourglass construction and manipulation functions

    @classmethod
    def create_hourglass_between(cls, v1, v2, multiplicity=1):
        r"""
        Creates a half hourglass to and from `v1` and `v2`, inserting it into each vertex's hourglass list.

        INPUT:

        - `v1` -- Vertex; the vertex to create the hourglass from.

        - `v2` -- Vertex; the vertex to create the hourglass to.

        - `multiplicity` -- nonnegative integer; the multiplicity of the hourglass.

        OUTPUT: HalfHourglass; the constructed hourglass from `v1` to `v2`.

        EXAMPLES:

        Note that this function automatically constructs the hourglass's twin.

            sage: ID.reset_id()
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: Vertex.create_hourglass_between(v1, v2, 1).twin()
            HalfHourglass (ID: v1_v2_t) from v2 to v1 with multiplicity 1

        .. NOTE::

            This function is a class method.
        """
        hh_id = str(v1.id) + "_" + str(v2.id)
        hh = HalfHourglass(hh_id, v1, v2, multiplicity)
        v1._insert_hourglass(hh)
        v2._insert_hourglass(hh.twin())
        return hh

    def _insert_hourglass(self, hh):
        r"""
        Inserts a half hourglass into the hourglass list for this vertex, maintaining
        the list with the first hourglass being the one with the smallest angle counterclockwise
        from the x-axis.

        INPUT:

        - `hh` -- HalfHourglass; the HalfHourglass to insert. This hourglass should start from this vertex.

        .. WARNING::

            This function should be called only on hourglasses originating from this vertex but not already
            tracked by this vertex. It is an internal function called in create_hourglass_between and reparent.
        """
        # empty list case
        if self._half_hourglasses_head is None:
            self._half_hourglasses_head = hh
            return

        self._reset_head()

        # find first edge with greater angle, then insert_cw_next
        hh_angle = hh.get_angle()
        for iter_hh in self:
            if hh_angle < iter_hh.get_angle():
                iter_hh.insert_ccw_prev(hh)
                if iter_hh is self._half_hourglasses_head: self._half_hourglasses_head = hh
                return
        # we've run the entire loop, so angle is greater than every other edge
        self._half_hourglasses_head.append_ccw(hh)

    @classmethod
    def remove_hourglass_between(cls, v1, v2):
        r"""
        Safely removes the hourglass between `v1` and `v2` and its twin.

        INPUT:

        - `v1` -- Vertex; Assumed to have an hourglass from it to `v2`.
        - `v2` -- Vertex

        OUTPUT: HalfHourglass; the removed HalfHourglass between `v1` and `v2`.

        EXAMPLES:

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.remove_hourglass_between(v1, v2)
            sage: v1.simple_degree()
            0

        It is an error to call this function on vertices with no hourglass between them.

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: Vertex.remove_hourglass_between(v1, v2)
            ValueError: Hourglass to vertex [Vertex v2 at (0, 1), filled] does not exist.

        .. NOTE::

            This function is a class method.

        .. WARNING::

            An error will be thrown if there is no hourglass between `v1` and `v2`.
        """
        hh = v1.get_hourglass_to(v2)
        v1._remove_hourglass(hh)
        v2._remove_hourglass(hh.twin())
        return hh

    def _remove_hourglass(self, hh):
        r"""
        Safely removes the provided hourglass from this vertex's hourglass list. Does not affect its twin.

        INPUT:

        - `hh` -- HalfHourglass; assumed to be in this vertex's half hourglass list.


        """
        # assert hh.v_from() is self, "Half hourglass " + str(hh.id) + " does not belong to this vertex."
        if hh is self._half_hourglasses_head:
            self._half_hourglasses_head = self._half_hourglasses_head.ccw_next()
            if hh is self._half_hourglasses_head: # this was the only remaining hourglass
                self._half_hourglasses_head = None
        hh.remove()

    def clear_hourglasses(self):
        r"""
        Deletes all hourglasses (and their twins) attached to this vertex, essentially isolating it.

        EXAMPLES:

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 1, 0, False)
            sage: v3 = Vertex('v3', 0, 1, False)
            sage: v4 = Vertex('v4', -1, 0, False)
            sage: Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v1, v3, 1)
            sage: Vertex.create_hourglass_between(v1, v4, 1)
            sage: v1.clear_hourglasses()
            sage: v1.simple_degree()
            0
        """
        if self._half_hourglasses_head is None: return

        for hh in self:
            hh.v_to()._remove_hourglass(hh.twin())
        self._half_hourglasses_head = None # this may not be memory-safe, depending on python's garbage collection

    def get_hourglass_to(self, v_to):
        r"""
        Returns the half hourglass from this vertex to `v_to`.

        INPUT:

        - `v_to` -- Vertex

        EXAMPLES:

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 1, 0, False)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: hh is v1.get_hourglass_to(v2)
            True

        It is an error to call this function on vertices with no hourglass between them.

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: v1.get_hourglass_to(v2)
            ValueError: Hourglass to vertex [Vertex v2 at (0, 1), filled] does not exist.
        """
        for hh in self:
            if hh.v_to() is v_to: return hh
        raise ValueError("Hourglass to vertex [" + str(v_to) + "] does not exist.")

    def get_trip(self, i, output='half_strands'):
        r"""
        Traverses the graph to compute trip i and returns an array of all visited elements.

        This function is intended for boundary vertices with a single hourglass leading to the interior of the graph,
        although it will also work with interior vertices. In that case, it will use the first strand in its

        INPUT:

        - ``i`` -- positive integer; the trip number. Assumed to be an integer `\geq 1`.

        - `output` -- String (default: 'half_strands'); The data type stored in the output array. If 'half_strands', returns the
            encountered HalfStrands. If 'half_hourglasses', returns the encountered HalfHourglasses. Anything else will return
            the strand IDs.

        OUTPUT: List; see `output` parameter for details

        EXAMPLES: # TODO

        .. SEEALSO::

            :meth:`HalfStrand.get_trip`
        """
        # TODO: Fluctuating case and interior vertex algorithm
        # assert self.boundary, "Vertex " + str(self.id) + " should be on the boundary." # Not necessarily! Revise this when integrating with analyzer
        if self.total_degree() != 1: raise NotImplementedError("Fluctuating case not yet implemented for HPG trips.")

        # find the hourglass to the graph interior
        hh = self._half_hourglasses_head
        while hh.is_boundary(): hh = hh.cw_next()
        strand = hh._half_strands_head
        return strand.get_trip(i, output)

    def get_hourglasses_as_list(self):
        r"""
        Returns all hourglasses starting at this vertex in a list.

        OUTPUT: List

        EXAMPLES:

            sage: v = Vertex('v', 0, 0, False)
            sage: v.get_hourglasses_as_list()
            []

            sage: ID.reset_id()
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 1, 0, False)
            sage: v3 = Vertex('v3', 0, 1, False)
            sage: v4 = Vertex('v4', -1, 0, False)
            sage: Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v1, v3, 1)
            sage: Vertex.create_hourglass_between(v1, v4, 1)
            sage: v1.get_hourglasses_as_list()
            [HalfHourglass (ID: v1_v2) from v1 to v2 with multiplicity 1, HalfHourglass (ID: v1_v4) from v1 to v4 with multiplicity 1, HalfHourglass (ID: v1_v3) from v1 to v3 with multiplicity 1]
        """
        if (self._half_hourglasses_head is None): return []
        return self._half_hourglasses_head.get_elements_as_list()

    def get_neighbors(self):
        r"""
        Returns all adjacent vertices in a list.

        OUTPUT: List

        EXAMPLES:

            sage: v = Vertex('v', 0, 0, False)
            sage: v.get_neighbors()
            []

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 1, 0, False)
            sage: v3 = Vertex('v3', 0, 1, False)
            sage: v4 = Vertex('v4', -1, 0, False)
            sage: Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v1, v3, 1)
            sage: Vertex.create_hourglass_between(v1, v4, 1)
            sage: v1.get_neighbors()
            [Vertex v2 at (1, 0), unfilled, Vertex v3 at (0, 1), unfilled, Vertex v4 at (-1, 0), unfilled]
        """
        return [hh.v_to() for hh in self]

    def total_degree(self):
        r"""
        Returns the number of strands around this vertex.

        OUTPUT: integer

        EXAMPLES:
            sage: v = Vertex('v', 0, 0, False)
            sage: v.total_degree()
            0

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 1, 0, False)
            sage: v3 = Vertex('v3', 0, 1, False)
            sage: v4 = Vertex('v4', -1, 0, False)
            sage: Vertex.create_hourglass_between(v1, v2, 2)
            sage: Vertex.create_hourglass_between(v1, v3, 3)
            sage: Vertex.create_hourglass_between(v1, v4, 1)
            sage: v1.total_degree()
            6
        """
        count = 0
        for hh in self: count += hh.strand_count()
        return count

    def simple_degree(self):
        r"""
        Returns the number of hourglasses around this vertex.

        OUTPUT: integer

        EXAMPLES:
            sage: v = Vertex('v', 0, 0, False)
            sage: v.simple_degree()
            0

            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 1, 0, False)
            sage: v3 = Vertex('v3', 0, 1, False)
            sage: v4 = Vertex('v4', -1, 0, False)
            sage: Vertex.create_hourglass_between(v1, v2, 2)
            sage: Vertex.create_hourglass_between(v1, v3, 3)
            sage: Vertex.create_hourglass_between(v1, v4, 1)
            sage: v1.simple_degree()
            3
        """
        if (self._half_hourglasses_head is None): return 0
        return self._half_hourglasses_head.get_num_elements()

    # Vertex manipulation functions (may be deprecated/unecessary, also untested)

    def is_contractible(self):
        r"""
        """
        hh1 = self._half_hourglasses_head
        hh2 = hh1.cw_next()
        if (hh1 is not hh2.cw_next() or hh1 is hh2): return False
        if (hh1.v_to().filled and hh2.v_to().filled and not self.filled) or (not hh1.v_to().filled and not hh2.v_to().filled and self.filled):
            return False
        return True

    def contract(self):
        r"""
        """
        hh1 = self._half_hourglasses_head
        hh2 = hh1.cw_next()

        # transfer hourglasses to one vertex, delete the other
        sur_v = hh1.v_to() # surviving vertex
        del_v = hh2.v_to()

        # Store hourglasses in array for safe iteration
        hhs = [hh for hh in del_v if hh is not hh2]
        for hh in hhs:
            hh.reparent(sur_v)

        sur_v.remove_hourglass(hh1.twin())

        return (self, del_v)

    # Square move functions

    def square_move_contract(self, out_hh):
        r"""
        Contracts the vertex into the vertex it is connected to outside the face.
        Functionally, reparents all this vertex's half hourglasses to out_hh.v_to().
        This function should only be called on vertices with only one outgoing hourglass.

        INPUT:

        - `out_hh` -- HalfHourglass; the half hourglass from this vertex to the vertex it will contract into.

        OUTPUT: Vertex; itself, prepared for deletion.

        .. NOTE::

            This function is not intended to be called directly; it is used internally by Face.square_move().

        .. SEEALSO::

            :meth:`Face.square_move`
        """
        sur_v = out_hh.v_to()

        # store in an array to make iteration safe while reparenting
        hourglasses = [hh for hh in self if hh is not out_hh]
        for hh in hourglasses:
            hh.reparent(sur_v)
        sur_v._remove_hourglass(out_hh.twin())

        return self

    def square_move_expand(self, hh1, hh2):
        r"""
        Expands the vertex by creating another vertex of opposite fill and using it to take its place in the square face.
        This function should only be called on vertices with two or more outgoing hourglasses.

        INPUT:

        - `hh1` -- HalfHourglass; A half hourglass that is part of the original square face.

        - `hh2` -- HalfHourglass; A second half hourglass that is part of the original square face.

        OUTPUT: Vertex; the created vertex.

        .. NOTE::

            This function is not intended to be called directly; it is used internally by Face.square_move().

        .. SEEALSO::

            :meth:`Face.square_move`
        """
        # find the new position by just taking a weighted average
        x = (2 * self.x + hh1.v_to().x + hh2.v_to().x) / 4
        y = (2 * self.y + hh1.v_to().y + hh2.v_to().y) / 4
        new_v = Vertex(ID.get_new_id("v"), x, y, not self.filled)

        hh1.reparent(new_v)
        hh2.reparent(new_v)

        multiplicity = hh1.multiplicity() + hh2.multiplicity()
        Vertex.create_hourglass_between(self, new_v, multiplicity)

        return new_v

    def __iter__(self):
        r"""
        Iterates over this vertex's hourglasses counterclockwise (in degree order).

        OUTPUT: _DihedralIterator; Set as counterclockwise iterator

        EXAMPLES:
            sage: v = Vertex('v', 0, 0, False)
            sage: [hh.id for hh in v]
            []

            sage: ID.reset_id()
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 1, 0, False)
            sage: v3 = Vertex('v3', 0, 1, False)
            sage: v4 = Vertex('v4', -1, 0, False)
            sage: Vertex.create_hourglass_between(v1, v2, 2)
            sage: Vertex.create_hourglass_between(v1, v3, 3)
            sage: Vertex.create_hourglass_between(v1, v4, 1)
            sage: [hh.id for hh in v1]
            ['v1_v2', 'v1_v3', 'v1_v4']

        .. SEEALSO::

            :meth:`DihedralElement.iterate_counterclockwise`
        """
        if self._half_hourglasses_head is None:
            return iter([])  # Return an empty iterator
        return self._half_hourglasses_head.iterate_counterclockwise()

    # FOR TESTING PURPOSES
    def print_neighbors(self):
        if self._half_hourglasses_head is None: print("no neighbors")
        else: print(str([hh.v_to().id for hh in self]))

    def print_neighbors_and_angles(self):
        if self._half_hourglasses_head is None: print("no neighbors")
        else: print(str([(hh.v_to().id, hh.get_angle()) for hh in self]))