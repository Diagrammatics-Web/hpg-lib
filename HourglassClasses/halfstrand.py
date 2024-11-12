r"""
Represents one direction of a strand in an hourglass plabic graph.

A strand is part of an hourglass edge that can be traversed.

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

from .dihedralelement import DihedralElement

class HalfStrand(DihedralElement):
    r"""
    Represents movement along one direction of a strand of an edge in an hourglass plabic graph.

    A HalfStrand is always assumed to be owned by a HalfHourglass and to have a twin HalfStrand;
    violating these assumptions may lead to crashes or infinite loops. HalfStrands should not
    typically be instantiated on their own, and are instead managed by higher level classes.
    """
    
    def __init__(self, id, hourglass, twin=None):
        r"""
        Constructs a HalfStrand with the given ID, owned by the provided HalfHourglass, and its twin.

        INPUT:

        - `id` -- hashable, unique object

        - `hourglass` -- HalfHourglass; the owning half hourglass. This HalfStrand will travel in the same direction.

        - `twin` -- HalfStrand (default: None); this parameter should be left blank. It is used internally to automatically construct this strand's twin.

        OUTPUT: HalfStrand; the constructed HalfStrand

        EXAMPLES:

        The HalfHourglass class automatically manages its strands; do not directly construct strands, as this example does.
        
            sage: hh = HalfHourglass('hh', None, None, 0)
            sage: hs = HalfStrand('1', hh)
            sage: hs.twin().id
            '1_t'

        .. WARNING::

            Do not assign any value to the twin parameter of this constructor.

            It is very unlikely you will need to directly construct HalfStrands; instead, use HalfHourglass's thicken(), thin(), and __init__() functions.
        """
        super().__init__(id)
        self._hourglass = hourglass
        
        # the half strand representing movement in the opposite direction, between the same vertices
        self._twin = HalfStrand(str(id) + "_t", hourglass.twin() if hourglass is not None else None, self) if twin is None else twin

    def __repr__(self):
        r"""
        Returns a String representation of this HalfStrand, providing its index, ID, and vertices.

        OUTPUT: str

        EXAMPLES:
        
            sage: ID.reset_id()
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: hh._half_strands_head.__repr__()
            'Strand 0 (ID: v1_v2_s0) from v1 to v2'
        """
        return "HalfStrand " + str(self.get_index_in_hourglass()) + " (ID: " + str(self.id) + ") from " + ("None" if self.v_from() is None else str(self.v_from().id)) + " to " + ("None" if self.v_to() is None else str(self.v_to().id))

    def hourglass(self):
        r"""
        Returns the parent hourglass of this strand.

        OUTPUT: HalfHourglass

        EXAMPLES:

            sage: hh = HalfHourglass('hh', None, None, 1)
            sage: hh._half_strands_head.hourglass().id
            'hh'
        """
        return self._hourglass

    def v_to(self):
        r"""
        Returns the vertex this HalfStrand traverses to.

        OUTPUT: Vertex
        
        EXAMPLES:
        
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: hh._half_strands_head.v_to().id
            'v2'
        """
        return self._hourglass.v_to()
        
    def v_from(self):
        r"""
        Returns the vertex this HalfStrand traverses from.

        OUTPUT: Vertex
        
        EXAMPLES:
        
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: hh._half_strands_head.v_from().id
            'v1'
        """
        return self._hourglass.v_from()
        
    def left_face(self):
        r"""
        Returns the Face on the left of this HalfStrand.

        OUTPUT: Face
        
        EXAMPLES:
        
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: face = Face('face', hh)
            sage: hh._half_strands_head.left_face().id
            'face'
        """
        return self._hourglass.left_face()
        
    def right_face(self):
        r"""
        Returns the Face on the left of this HalfStrand.

        OUTPUT: Face
        
        EXAMPLES:   
        
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: face = Face('face', hh)
            sage: hh._half_strands_head.left_face().id
            'face'
        """
        return self._hourglass.right_face()

    def get_last_strand_same_hourglass(self):
        r"""
        Returns the clockwise last strand owned by the same parent hourglass.

        OUTPUT: HalfStrand

        EXAMPLES:

            sage: ID.reset_id()
            sage: v1 = Vertex('v1', 0, 0, True)
            sage: v2 = Vertex('v2', 0, 1, True)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 5)
            sage: hh._half_strands_head.get_last_strand_same_hourglass()
            'Strand 4 (ID: v1_v2_s4) from v1 to v2'

        .. WARNING::
        
           Avoid using. Instead, use hourglass()._half_strands_tail if possible. Runtime: O(n)
        """
        for strand in self.cw_next().iterate_clockwise():
            if strand.hourglass() is not self.hourglass() or strand == self: return strand.cw_prev()

    def get_num_strands_same_hourglass(self):
        r"""
        Returns the number of strands owned by the same parent hourglass.

        OUTPUT: integer

        EXAMPLES:
        
            sage: hh = HalfHourglass('hh', None, None, 6)
            sage: hh._half_strands_head.get_num_strands_same_hourglass()
            6

        .. NOTE::

            Internally calls hourglass().strand_count(). Use that instead if possible.
        """
        return self.hourglass().strand_count()

    def get_index_in_hourglass(self):
        r"""
        Returns the index of this strand in its parent hourglass.
        
        Indexing starts at 0 from the hourglass's _half_strand_head and proceeds clockwise.

        OUTPUT: integer

        EXAMPLES:
        
            sage: hh = HalfHourglass('hh', None, None, 6)
            sage: hh._half_strands_head.get_index_in_hourglass()
            0
            
            sage: hh = HalfHourglass('hh', None, None, 6)
            sage: hh._half_strands_head.get_cw_ith_element(3).get_index_in_hourglass()
            3

        .. NOTE::

            Runtime: O(n)
        """
        i = 0
        for s in self.hourglass().iterate_strands():
            if s is self:
                return i
            i += 1

    def get_ith_trip_turn(self, i):
        r"""
        Helper function returning the correct turn for trip i on this strand.

        INTPUT:

            - ``i`` -- positive integer; the trip number. Assumed to be an integer `\geq 1`.

        OUTPUT: HalfStrand

        .. SEEALSO::

            :func:`get_trip`
        """
        return self.get_ith_right(i) if self.v_to().filled else self.get_ith_left(i)

    def invert_ith_trip_turn(self, i):
        r"""
        Helper function returning the strand that turns onto this strand on trip i.

        INTPUT:

            - ``i`` -- positive integer; the trip number. Assumed to be an integer `\geq 1`.

        OUTPUT: HalfStrand

        .. SEEALSO::

            :func:`get_trip`
        """
        return self.get_cw_ith_element(i).twin() if self.v_from().filled else self.get_ccw_ith_element(i).twin()

    def get_trip(self, i, output='half_strands'):
        r"""
        Traverses the graph to compute trip i and returns an array of all visited elements.

        A trip is computed by turning right at filled vertices and turning left at unfilled vertices. This process is 
        repeated until the boundary is reached or an isolated trip is identified.
        The ith trip specifies that the ith right/left is taken; that is, the ith strand counterclockwise/clockwise.
        Can be called on any strand, even non-boundary strands. This function will find the entire trip regardless.

        INPUT:
        
            - ``i`` -- positive integer; the trip number. Assumed to be an integer `\geq 1`.

            - `output` -- String (default: 'half_strands'); The data type stored in the output array. If 'half_strands', returns the
                encountered HalfStrands. If 'half_hourglasses', returns the encountered HalfHourglasses. Anything else will return
                the strand IDs.
            
        OUTPUT: List; see `output` parameter for details

        EXAMPLES: # TODO

        .. NOTE::

            This function runs slower if called on an internal strand as it will require additional overhead to detect isolated trips.

            This function assumes a "properly formed" hourglass plabic graph.

            Runtime: O(rn), where r is the valence of the graph.
        """
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
        return visited