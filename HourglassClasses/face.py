r"""
Represents a face in an hourglass plabic graph.

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

class Face:
    r"""
    Represents a face of an hourglass plabic graph.
    A face can be unbounded.
    A Face is simply a reference to a collection of edges/vertices, and does not actually
    directly manage them. This should instead be done though an HourglassPlabicGraph.
    """
    def __init__(self, id, half_hourglass, outer=False):
        r"""
        Constructs a Face with the given ID to the right of the given half hourglass.

        INPUT:

        - `id` -- hashable, unique object

        - `half_hourglass` -- HalfHourglass; a HalfHourglass adjacent to this face with this face on its right.

        - `outer` -- boolean; determines if this face is an outer face; default `False`

        OUTPUT: Face; the constructed Face

        EXAMPLES:

            sage: v1 = Vertex('v1', 0, 0, False)
            sage: v2 = Vertex('v2', 0, 1, False)
            sage: v3 = Vertex('v3', 1, 1, False)
            sage: v4 = Vertex('v4', 1, 0, False)
            sage: Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v2, v3, 1)
            sage: Vertex.create_hourglass_between(v3, v4, 1)
            sage: hh = Vertex.create_hourglass_between(v4, v1, 1)
            sage: face = Face('face', hh)
            sage: [hh.v_to().id for hh in face]
            ['v1', 'v2', 'v3', 'v4']

        This example verifies that the face is on the correct side of the hourglass.

            sage: v5 = Vertex('v5', 2, 0, False)
            sage: Vertex.create_hourglass_between(v4, v5, 1)
            sage: face = Face('face', hh)
            sage: [hh.v_to().id for hh in face]
            ['v1', 'v2', 'v3', 'v4']

        .. NOTE::

            Constructing a Face does not actually construct any of its vertices or edges; instead, these
            are already assumed to exist. The Face simply allows you to unify them.
        """
        self.id = id

        self._half_hourglasses_head = half_hourglass
        self.boundary = False
        self.outer = outer
        self.initialize_half_hourglasses(half_hourglass)

    def __repr__(self):
        r"""
        Returns a String representation of this Face, providing its ID.

        OUTPUT: str

        EXAMPLES:
            sage: v1 = Vertex('v1', 0, -1, True)
            sage: v2 = Vertex('v2', 1, 0, False)
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: f = Face('face', hh)
            sage: f.__repr__()
            'Face face'
        """
        return f"Face {self.id}"

    def initialize_half_hourglasses(self, hh):
        r"""
        Sets this face as the right face for hh and all other half hourglasses in the
        same rightward loop, as well as the left face for all twin hourglasses in the
        reverse direction.

        INPUT:

        - `hh` -- HalfHourglass; a HalfHourglass with this face on its right.

        EXAMPLES:

        Note that initialize_half_hourglasses is called internally by the constructor.
        This example demonstrates how initialize_half_hourglasses can be used when
        modifying the edges of a face.

            sage: v1 = Vertex('v1', 0, 0, False)
            sage: v2 = Vertex('v2', 0, 1, False)
            sage: v3 = Vertex('v3', 1, 1, False)
            sage: v4 = Vertex('v4', 1, 0, False)
            sage: Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v2, v3, 1)
            sage: hh = Vertex.create_hourglass_between(v3, v1, 1)
            sage: face = Face('face', hh)
            sage: Vertex.remove_hourglass_between(v3, v1)
            sage: Vertex.create_hourglass_between(v3, v4, 1)
            sage: hh = Vertex.create_hourglass_between(v4, v1, 1)
            sage: face.initialize_half_hourglasses(hh)
            sage: [hh.v_to().id for hh in face]
            ['v1', 'v2', 'v3', 'v4']
        """
        self._half_hourglasses_head = hh
        self.boundary = False
        for iter_hh in self:
            iter_hh._right_face = self
            iter_hh.twin()._left_face = self
            if iter_hh.is_boundary(): self.boundary = True

    # Moves

    # Square move

    def is_square_move_valid(self, r=4):
        r"""
        Verifies that this face can perform a square move.

        In order to perform a square move, the face should have 4 vertices, alternating
        filled/unfilled status. The sum of the multiplicities of the hourglasses of this
        face should equal r.
        In a square move, vertices with one outgoing edge are contracted, while vertices
        with two outgoing edges are split into two vertices connected by an hourglass of
        sufficient multiplicity to maintain r-valence.

        INPUT:

        - ``r`` -- positive integer (default: 4); the valence of the graph. Assumed to be an integer `\geq 1`.

        OUTPUT: Boolean; whether the face can perform a square move.

        EXAMPLES:

        This example explicitly constructs a face where a square move is valid.

            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 1, 1, True)
            sage: v4 = Vertex(4, 0, 1, False)
            sage: extras = [Vertex(5, -1, -1, False), Vertex(6, 2, -1, True), Vertex(7, 2, 1, False), Vertex(8, 1, 2, False), Vertex(9, 0, 2, True), Vertex(10, -1, 1, True), Vertex(11, -2, -1, True), Vertex(12, -1, -2, True), Vertex(13, 2, -2, False), Vertex(14, 3, -1, False)]
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v2, v3, 1)
            sage: Vertex.create_hourglass_between(v3, v4, 1)
            sage: Vertex.create_hourglass_between(v4, v1, 1)
            sage: Vertex.create_hourglass_between(v1, extras[0], 2)
            sage: Vertex.create_hourglass_between(v2, extras[1], 2)
            sage: Vertex.create_hourglass_between(v3, extras[2], 1)
            sage: Vertex.create_hourglass_between(v3, extras[3], 1)
            sage: Vertex.create_hourglass_between(v4, extras[4], 1)
            sage: Vertex.create_hourglass_between(v4, extras[5], 1)
            sage: Vertex.create_hourglass_between(extras[0], extras[6], 1)
            sage: Vertex.create_hourglass_between(extras[0], extras[7], 1)
            sage: Vertex.create_hourglass_between(extras[1], extras[8], 1)
            sage: Vertex.create_hourglass_between(extras[1], extras[9], 1)
            sage: face = Face('face', hh.twin())
            sage: face.is_square_move_valid()
            True

        We modify the face so it clearly cannot perform a square move.

            sage: Vertex.create_hourglass_between(v3, v1, 1)
            sage: face.initialize_half_hourglasses(hh.twin())
            sage: face.is_square_move_valid()
            False
        """
        count = 0
        multiplicity_sum = 0
        should_be_filled = not self._half_hourglasses_head.v_from().filled # this check may be unecessary depending on the assumptions on the graph
        for hh in self:
            # Checks
            if hh.v_to().filled != should_be_filled: return False
            if count > 4: return False
            multiplicity_sum += hh.multiplicity()
            # Iterate
            count += 1
            should_be_filled = not should_be_filled
        return (multiplicity_sum == r)

    def square_move(self, r=4):
        r"""
        Performs a square move on this face.
        In a square move, vertices with one outgoing edge are contracted, while vertices
        with two outgoing edges are split into two vertices connected by an hourglass of
        sufficient multiplicity to maintain r-valence.

        INPUT:

        - ``r`` -- positive integer (default: 4); the valence of the graph. Assumed to be an integer `\geq 1`.

        OUTPUT: Array Tuple; the first is of created vertices that result from this move, the second is of all removed vertices.

        EXAMPLES:

        This example constructs a face and performs a square move on it.

            sage: ID.reset_id()
            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 1, 1, True)
            sage: v4 = Vertex(4, 0, 1, False)
            sage: extras = [Vertex(5, -1, -1, False), Vertex(6, 2, -1, True), Vertex(7, 2, 1, False), Vertex(8, 1, 2, False), Vertex(9, 0, 2, True), Vertex(10, -1, 1, True), Vertex(11, -2, -1, True), Vertex(12, -1, -2, True), Vertex(13, 2, -2, False), Vertex(14, 3, -1, False)]
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v2, v3, 1)
            sage: Vertex.create_hourglass_between(v3, v4, 1)
            sage: Vertex.create_hourglass_between(v4, v1, 1)
            sage: Vertex.create_hourglass_between(v1, extras[0], 2)
            sage: Vertex.create_hourglass_between(v2, extras[1], 2)
            sage: Vertex.create_hourglass_between(v3, extras[2], 1)
            sage: Vertex.create_hourglass_between(v3, extras[3], 1)
            sage: Vertex.create_hourglass_between(v4, extras[4], 1)
            sage: Vertex.create_hourglass_between(v4, extras[5], 1)
            sage: Vertex.create_hourglass_between(extras[0], extras[6], 1)
            sage: Vertex.create_hourglass_between(extras[0], extras[7], 1)
            sage: Vertex.create_hourglass_between(extras[1], extras[8], 1)
            sage: Vertex.create_hourglass_between(extras[1], extras[9], 1)
            sage: face = Face('face', hh.twin())
            sage: face.square_move()
            sage: [hh.v_from().id for hh in face]
            [6, 5, 'v16', 'v19']

        .. WARNING::

            This function may crash or otherwise corrupt the graph if a square move is
            not valid. Use `is_square_move_valid` before to ensure this is possible.

        .. SEEALSO::

            :meth:`Face.is_square_move_valid`
            :meth:`Vertex.square_move_expand`
            :meth:`Vertex.square_move_contract`
        """
        new_vertices = []
        removed_vertices = []

        # diagnose vertices and perform expansion or contraction as necessary
        hourglasses = [hh for hh in self] # cache half hourglasses for safe iteration
        for hh in hourglasses:
            v = hh.v_from()
            if v.simple_degree() > 3: new_vertices.append(v.square_move_expand(hh, hh.cw_next()))
            else: removed_vertices.append(v.square_move_contract(hh.ccw_next()))

        # "Swap" multiplicities of hourglasses
        # TODO: Actually swap these hourglasses rather than using thicken/thin
        target_multiplicities = [hh.right_turn().right_turn().multiplicity() for hh in hourglasses]
        for i in range(0, len(hourglasses)):
            hh = hourglasses[i]
            while hh.multiplicity() > target_multiplicities[i]: hh.thin()
            while hh.multiplicity() < target_multiplicities[i]: hh.thicken()

        return new_vertices, removed_vertices

    # SL4 Square move (should operate identically to square_move(r=4))

    def is_square_move4_valid(self):
        r"""
        Verifies that this face can perform a square move in SL4.

        In order to perform a square move, the face should have 4 vertices, alternating
        filled/unfilled status. Each hourglass in this face should have multiplicity 1.
        In a square move, vertices with one outgoing edge are contracted, while vertices
        with two outgoing edges are split into two vertices.

        OUTPUT: Boolean; whether the face can perform a square move.

        EXAMPLES:

        This example constructs a face where a square move is valid.

            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 1, 1, True)
            sage: v4 = Vertex(4, 0, 1, False)
            sage: extras = [Vertex(5, -1, -1, False), Vertex(6, 2, -1, True), Vertex(7, 2, 1, False), Vertex(8, 1, 2, False), Vertex(9, 0, 2, True), Vertex(10, -1, 1, True), Vertex(11, -2, -1, True), Vertex(12, -1, -2, True), Vertex(13, 2, -2, False), Vertex(14, 3, -1, False)]
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v2, v3, 1)
            sage: Vertex.create_hourglass_between(v3, v4, 1)
            sage: Vertex.create_hourglass_between(v4, v1, 1)
            sage: Vertex.create_hourglass_between(v1, extras[0], 2)
            sage: Vertex.create_hourglass_between(v2, extras[1], 2)
            sage: Vertex.create_hourglass_between(v3, extras[2], 1)
            sage: Vertex.create_hourglass_between(v3, extras[3], 1)
            sage: Vertex.create_hourglass_between(v4, extras[4], 1)
            sage: Vertex.create_hourglass_between(v4, extras[5], 1)
            sage: Vertex.create_hourglass_between(extras[0], extras[6], 1)
            sage: Vertex.create_hourglass_between(extras[0], extras[7], 1)
            sage: Vertex.create_hourglass_between(extras[1], extras[8], 1)
            sage: Vertex.create_hourglass_between(extras[1], extras[9], 1)
            sage: face = Face('face', hh.twin())
            sage: face.is_square_move4_valid()
            True

        We modify the face so it clearly cannot perform a square move.

            sage: Vertex.create_hourglass_between(v3, v1, 1)
            sage: face.initialize_half_hourglasses(hh.twin())
            sage: face.is_square_move4_valid()
            False

        .. NOTE::

            The output of this function should be identical to Face.square_move(r=4).
        """
        count = 0
        should_be_filled = not self._half_hourglasses_head.v_from().filled # this check may be unecessary depending on the assumptions on the graph
        for hh in self:
            # Checks
            if hh.multiplicity() != 1: return False
            if hh.v_to().filled != should_be_filled: return False
            if count > 4: return False
            # Iterate
            count += 1
            should_be_filled = not should_be_filled
        return True

    def square_move4(self):
        r"""
        Performs a square move on this face, assuming the graph is in SL4.
        In a square move, vertices with one outgoing edge are contracted, while vertices
        with two outgoing edges are split into two vertices.

        OUTPUT: Array Tuple; the first is of created vertices that result from this move, the second is of all removed vertices.

        EXAMPLES:

        This example constructs a face and performs a square move on it.

            sage: ID.reset_id()
            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 1, 1, True)
            sage: v4 = Vertex(4, 0, 1, False)
            sage: extras = [Vertex(5, -1, -1, False), Vertex(6, 2, -1, True), Vertex(7, 2, 1, False), Vertex(8, 1, 2, False), Vertex(9, 0, 2, True), Vertex(10, -1, 1, True), Vertex(11, -2, -1, True), Vertex(12, -1, -2, True), Vertex(13, 2, -2, False), Vertex(14, 3, -1, False)]
            sage: hh = Vertex.create_hourglass_between(v1, v2, 1)
            sage: Vertex.create_hourglass_between(v2, v3, 1)
            sage: Vertex.create_hourglass_between(v3, v4, 1)
            sage: Vertex.create_hourglass_between(v4, v1, 1)
            sage: Vertex.create_hourglass_between(v1, extras[0], 2)
            sage: Vertex.create_hourglass_between(v2, extras[1], 2)
            sage: Vertex.create_hourglass_between(v3, extras[2], 1)
            sage: Vertex.create_hourglass_between(v3, extras[3], 1)
            sage: Vertex.create_hourglass_between(v4, extras[4], 1)
            sage: Vertex.create_hourglass_between(v4, extras[5], 1)
            sage: Vertex.create_hourglass_between(extras[0], extras[6], 1)
            sage: Vertex.create_hourglass_between(extras[0], extras[7], 1)
            sage: Vertex.create_hourglass_between(extras[1], extras[8], 1)
            sage: Vertex.create_hourglass_between(extras[1], extras[9], 1)
            sage: face = Face('face', hh.twin())
            sage: face.square_move4()
            sage: [hh.v_from().id for hh in face]
            [6, 5, 'v16', 'v19']

        .. WARNING::

            This function may crash or otherwise corrupt the graph if a square move is
            not valid. Use `is_square_move4_valid` before to ensure this is possible.

        .. SEEALSO::

            :meth:`Face.is_square_move4_valid`
            :meth:`Vertex.square_move_expand`
            :meth:`Vertex.square_move_contract`
        """
        new_vertices = []
        removed_vertices = []

        # diagnose vertices and perform expansion or contraction as necessary
        hourglasses = [hh for hh in self] # cache half hourglasses for safe iteration
        for hh in hourglasses:
            v = hh.v_from()
            if v.simple_degree() == 4: new_vertices.append(v.square_move_expand(hh, hh.cw_next()))
            else: removed_vertices.append(v.square_move_contract(hh.ccw_next()))

        return new_vertices, removed_vertices

    # Cycle

    def is_cycle_valid(self, start_hh, inverse=False):
        r"""
        Verifies that this face can perform a cycle move.
        This requires the face to have an even number of vertices, with alternating filled/unfilled
        status. Each other hourglass starting from start_hh should have a multiplicity greater than 1.
        In a cycle move, hourglasses starting from start_hh are alternatively thinned and thickened.

        INPUT:

        - `start_hh` -- HalfHourglass; An hourglass in this face. This hourglass will be thinned.
                        If `None`, defaults to this face's head HalfHourglass.

        - `inverse` -- boolean; default `False`; reverses the usual cycling operation if `True`

        OUTPUT: Boolean, whether a cycle can be performed on this face.

        EXAMPLES:

        This example constructs a face for which a cycle move is valid.

            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 2, 1, True)
            sage: v4 = Vertex(4, 1, 2, False)
            sage: v5 = Vertex(5, 0, 2, True)
            sage: v6 = Vertex(6, -1, 1, False)
            sage: Vertex.create_hourglass_between(v2, v1, 1)
            sage: Vertex.create_hourglass_between(v3, v2, 2)
            sage: Vertex.create_hourglass_between(v4, v3, 1)
            sage: Vertex.create_hourglass_between(v5, v4, 2)
            sage: Vertex.create_hourglass_between(v6, v5, 1)
            sage: hh = Vertex.create_hourglass_between(v1, v6, 2)
            sage: face = Face("face", hh)
            sage: face.is_cycle_valid(hh)
            True
        """
        if start_hh is None:
            start_hh = self._half_hourglasses_head

        if start_hh.right_face() is not self:
            if start_hh.left_face() is self: start_hh = start_hh.twin()
            else: raise ValueError("start_hh does not belong to this face.")

        if inverse:
            start_hh = start_hh.right_turn()
        
        count = 0
        should_be_filled = not start_hh.v_from().filled
        check_mult = True
        for hh in start_hh.iterate_right_turns():
            # Checks
            if check_mult and hh.multiplicity() <= 1: return False
            if hh.v_to().filled != should_be_filled: return False
            # Iterate
            count += 1
            should_be_filled = not should_be_filled
            check_mult = not check_mult
        return count % 2 == 0

    def cycle(self, start_hh, inverse=False):
        r"""
        Performs a cycle move on this face. Its edges are alternatingly thinned and thickened,
        starting from start_hh.

        INPUT:

        - `start_hh` -- HalfHourglass; An hourglass in this face. This hourglass will be thinned.
                        If `None`, defaults to this face's head HalfHourglass.
        
        - `inverse` -- boolean; default `False`; reverses the usual cycling operation if `True`

        EXAMPLES:

        This example constructs a face for which a cycle move is valid.

            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 2, 1, True)
            sage: v4 = Vertex(4, 1, 2, False)
            sage: v5 = Vertex(5, 0, 2, True)
            sage: v6 = Vertex(6, -1, 1, False)
            sage: Vertex.create_hourglass_between(v2, v1, 1)
            sage: Vertex.create_hourglass_between(v3, v2, 2)
            sage: Vertex.create_hourglass_between(v4, v3, 1)
            sage: Vertex.create_hourglass_between(v5, v4, 2)
            sage: Vertex.create_hourglass_between(v6, v5, 1)
            sage: hh = Vertex.create_hourglass_between(v1, v6, 2)
            sage: face = Face("face", hh)
            sage: prev_mults = [hh.multiplicity() for hh in face]
            sage: face.cycle(hh)
            sage: (prev_mults, [hh.multiplicity() for hh in face])
            ([2, 1, 2, 1, 2, 1], [1, 2, 1, 2, 1, 2])

        .. WARNING::

            This function may crash or otherwise corrupt the graph if a cycle is
            not valid. Use `is_cycle_valid` before to ensure this is possible.

        .. SEEALSO::

            :meth:`Face.is_cycle_valid`
        """
        if start_hh is None:
            start_hh = self._half_hourglasses_head
        
        if start_hh.right_face() is not self: start_hh = start_hh.twin()

        if inverse:
            start_hh = start_hh.right_turn()

        thicken = False
        for hh in start_hh.iterate_right_turns():
            if thicken: hh.thicken()
            else: hh.thin()
            thicken = not thicken

    # Benzene move

    def is_benzene_move_valid(self):
        r"""
        Verifies that this face can perform a benzene move.
        This requires the face to have an even number of vertices, with alternating
        filled/unfilled status, and with edges of alternating 1 or 2 multiplicity in between.
        In a benzene move, the multiplicities of consecutive edges are swapped.

        OUTPUT: Boolean; whether this face can perform a benzene move.

        EXAMPLES:

        This example constructs a face for which a benzene move is valid.

            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 2, 1, True)
            sage: v4 = Vertex(4, 1, 2, False)
            sage: v5 = Vertex(5, 0, 2, True)
            sage: v6 = Vertex(6, -1, 1, False)
            sage: Vertex.create_hourglass_between(v2, v1, 1)
            sage: Vertex.create_hourglass_between(v3, v2, 2)
            sage: Vertex.create_hourglass_between(v4, v3, 1)
            sage: Vertex.create_hourglass_between(v5, v4, 2)
            sage: Vertex.create_hourglass_between(v6, v5, 1)
            sage: hh = Vertex.create_hourglass_between(v1, v6, 2)
            sage: face = Face("face", hh)
            sage: face.is_benzene_move_valid()
            True

        .. NOTE::

            A benzene move is a special case of a cycle. This should be equivalent to
            calling is_cycle_valid(hh), where hh is a multiplicity 2 edge, and the face
            meets all listed criteria for a benzene move.

        .. SEEALSO::

            :meth:`Face.is_cycle_valid`
        """
        count = 0
        should_be_filled = not self._half_hourglasses_head.v_from().filled # this check may be unecessary depending on the assumptions on the graph
        expected_mult = 1 if self._half_hourglasses_head.strand_count() == 1 else 2
        for hh in self:
            # Checks
            if hh.multiplicity() != expected_mult: return False
            if hh.v_to().filled != should_be_filled: return False
            # Iterate
            count += 1
            should_be_filled = not should_be_filled
            expected_mult = 3 - expected_mult # maps 2 -> 1 and 1 -> 2
        return count % 2 == 0

    def benzene_move(self):
        r"""
        Performs a benzene move on this face.
        The multiplicities of its edges are swapped between 1 and 2.

        EXAMPLES:

        This example constructs a face for which a benzene move is valid.

            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 2, 1, True)
            sage: v4 = Vertex(4, 1, 2, False)
            sage: v5 = Vertex(5, 0, 2, True)
            sage: v6 = Vertex(6, -1, 1, False)
            sage: Vertex.create_hourglass_between(v2, v1, 1)
            sage: Vertex.create_hourglass_between(v3, v2, 2)
            sage: Vertex.create_hourglass_between(v4, v3, 1)
            sage: Vertex.create_hourglass_between(v5, v4, 2)
            sage: Vertex.create_hourglass_between(v6, v5, 1)
            sage: hh = Vertex.create_hourglass_between(v1, v6, 2)
            sage: face = Face("face", hh)
            sage: prev_mults = [hh.multiplicity() for hh in face]
            sage: face.benzene_move()
            sage: (prev_mults, [hh.multiplicity() for hh in face])
            ([2, 1, 2, 1, 2, 1], [1, 2, 1, 2, 1, 2])

        .. NOTE::

            A benzene move is a special case of a cycle. This should be equivalent to
            calling cycle(hh), where hh is a multiplicity 2 edge, and the face
            meets all listed criteria for a benzene move.

        .. WARNING::

            This function may crash or otherwise corrupt the graph if a benzene move is
            not valid. Use `is_benzene_move_valid` before to ensure this is possible.

        .. SEEALSO::

            :meth:`Face.is_benzene_move_valid`
            :meth:`Face.cycle`
        """
        thicken = self._half_hourglasses_head.strand_count() == 1
        for hh in self:
            if thicken: hh.thicken()
            else: hh.thin()
            thicken = not thicken

    def __iter__(self):
        r"""
        Iterates over the hourglasses in this face. Iteration occurs beginning from face._half_hourglasses_head and continues clockwise.

        OUTPUT: HalfHourglass._TurnIterator; set to iterate right turns.

        EXAMPLES:

        This can be used to iterate over the vertices of this face.

            sage: v1 = Vertex(1, 0, 0, True)
            sage: v2 = Vertex(2, 1, 0, False)
            sage: v3 = Vertex(3, 2, 1, True)
            sage: v4 = Vertex(4, 1, 2, False)
            sage: v5 = Vertex(5, 0, 2, True)
            sage: v6 = Vertex(6, -1, 1, False)
            sage: Vertex.create_hourglass_between(v2, v1, 1)
            sage: Vertex.create_hourglass_between(v3, v2, 2)
            sage: Vertex.create_hourglass_between(v4, v3, 1)
            sage: Vertex.create_hourglass_between(v5, v4, 2)
            sage: Vertex.create_hourglass_between(v6, v5, 1)
            sage: hh = Vertex.create_hourglass_between(v1, v6, 2)
            sage: face = Face("face", hh)
            sage: [hh.v_to().id for hh in face]
            [6, 5, 4, 3, 2, 1]
        """
        return self._half_hourglasses_head.iterate_right_turns()

    def vertices(self):
        '''Iterates over the vertices of this face in clockwise order from an arbitrary starting point.'''
        for hh in self:
            yield hh.v_from()

    # TESTING
    def print_vertices(self):
        print(str([hh.v_from().id for hh in self]))
