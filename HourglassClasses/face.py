r"""
TODO
TODO
TODO

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
            iter_hh._right_face = self
            iter_hh.twin()._left_face = self
            if iter_hh.is_boundary(): self.boundary = True

    # Moves

    # Square move

    def is_square_move_valid(self, r=4):
        ''' Verifies that this face can perform a square move. The face should have 4 vertices,
            alternating filled/unfilled status. The sum of the multiplicities of connecting hourglasses should equal r.
            In a square move, vertices with one outgoing edge are contracted, while vertices with two outgoing edges
            are split into two vertices connected by an hourglass of sufficient multiplicity.'''
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
        ''' Performs a square move on this face. Vertices with one outgoing edge are contracted, while vertices with two outgoing edges are split into two vertices.
            To verify that this move will be valid, call is_square_move_valid().
            OUTPUT: A tuple of arrays: the first is of created vertices that result from this move, the second is of all removed vertices.'''
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
        ''' Verifies that this face can perform a square move. In SL4, this requires the face to be made of 4 vertices,
            alternating filled/unfilled status, with multiplicity 1 edges in between.
            In a square move, vertices with one outgoing edge are contracted, while vertices with two outgoing edges are split into two vertices.'''
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
        ''' Performs a square move on this face, assuming the graph is in SL4. Vertices with one outgoing edge are contracted,
            while vertices with two outgoing edges are split into two vertices.
            To verify that this move will be valid, call is_square_move4_valid().
            OUTPUT: A tuple of arrays: the first is of created vertices that result from this move, the second is of all removed vertices.'''
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

    def is_cycle_valid(self, start_hh):
        ''' Verifies that this face can perform a cycle move. This requires the face to have an even number of
            vertices, with alternating filled/unfilled status. Each other hourglass starting from start_hh should have
            a multiplicity greater than 1.
            In a cycle move, hourglasses starting from start_hh are alternatively thickened and thinned.
            start_hh: The starting hourglass in this face.'''
        if start_hh.right_face() is not self:
            if start_hh.left_face() is self: start_hh = start_hh.twin()
            else: raise ValueError("start_hh does not belong to this face!")

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

    def cycle(self, start_hh):
        ''' Performs a cycle move on this face. Its edges are alternatingly thinned and thickened,
            starting from start_hh.
            To verify that this move will be valid, call is_cycle_valid(start_hh).'''
        if start_hh.right_face() is not self: start_hh = start_hh.twin()

        thicken = False
        for hh in start_hh.iterate_right_turns():
            if thicken: hh.thicken()
            else: hh.thin()
            thicken = not thicken

    # Benzene move

    def is_benzene_move_valid(self):
        ''' Verifies that this face can perform a square move. This requires the face to have an even number of
            vertices, with alternating filled/unfilled status, and with edges of alternating 1 or 2 multiplicity in between.
            In a benzene move, the multiplicities of the edges are swapped.'''
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
