r"""
Represents an hourglass plabic graph.

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
from sage.graphs.graph import Graph
from .vertex import Vertex
from .face import Face
from .idgenerator import ID

class HourglassPlabicGraph:
    r"""
    Represents an hourglass plabic graph (HPG).
    An hourglass plabic graph has filled or unfilled vertices.
    It has weights (multiplicities) on its edges (hourglasses), represented by strands.
    Hourglass plabic graphs can be traversed. To traverse, choose a trip number i and
    start at some strand. Traverse the strand, which is mirrored to the other side as
    it moves from one vertex to another. Take the ith right at a filled vertex, and the
    ith left at an unfilled vertex. Continue until the boundary is reached.
    """
    def __init__(self, n=0, filling=True, r=10):
        r"""
        Constructs an Hourglass Plabic Graph.

        INPUT:

        - ``n`` -- nonnegative integer (default: `0`); the number of boundary vertices to create. If 0, does not initialize any vertices.

        - ``filling`` -- boolean or boolean iterable (default: ``True``); Whether the vertices should be filled. If an iterable, the filled/unfilled statuses of the boundary vertices, starting from 0.

        - ``r`` -- float (default: `10`); the radius of the boundary.

        EXAMPLES:

            sage: HPG = HourglassPlabicGraph()
            sage: HPG.order()
            0

            sage: HPG = HourglassPlabicGraph(8)
            sage: HPG.order()
            8

        .. NOTE::

            If ``n>0``, internally calls `construct_boundary(n, filling, r)`.
        """
        # dictionaries pairing IDs to vertices and faces
        self._inner_vertices = dict()
        self._boundary_vertices = dict()
        self._faces = dict()

        self.layout = 'circular'
        if n > 0: self.construct_boundary(n, filling, r)

    def __eq__(self, other):
        r"""
        Tests for equality between two HPGs.
        Equality is considered to be an embedded planar graph isomorphism.

        INPUT:

        - `other` -- object; The object to test against.

        OUTPUT: Boolean; returns True if and only if `other` is an HPG and is isomorphic to this HPG.

        EXAMPLES:

        This example constructs two isomorphic HPGs and tests equality.

            hpg1 = HourglassPlabicGraph()
            hpg1.construct_face(6, [2, 1, 2, 1, 2, 1])
            hpg2 = HourglassPlabicGraph()
            hpg2.construct_face(6, [2, 1, 2, 1, 2, 1])
            hpg1.__eq__(hpg2)
            True

        This example demonstrates that edge multiplicities are relevant to isomorphism.
        See the WARNING for issues with testing otherwise isomorphic graphs with different orientations.

            hpg1 = HourglassPlabicGraph()
            hpg1.construct_face(6, [2, 1, 2, 1, 2, 1])
            hpg2 = HourglassPlabicGraph()
            hpg2.construct_face(6, [1, 2, 1, 2, 1, 2])
            hpg1.__eq__(hpg2)
            False

        This example uses two clearly non-isomorphic graphs.

            hpg1 = HourglassPlabicGraph()
            hpg1.construct_face(6, [2, 1, 2, 1, 2, 1])
            hpg2 = HourglassPlabicGraph()
            hpg2.construct_face(4, [2, 1, 2, 1])
            hpg1.__eq__(hpg2)
            False

        .. WARNING::

            The test for isomorphism assumes graphs are also "oriented" the same way; that is,
            their ID 0 boundary vertex is in the same place.

            This test also fails if there are isolated components.

            This function is not intended to be used on non "properly formed" HPGs, and may fail or crash.

        .. SEEALSO::

            :meth:`HourglassPlabicGraph.is_isomorphic`
        """
        return isinstance(other, HourglassPlabicGraph) and self.is_isomorphic(other)

    def __neq__(self, other):
        r"""
        Tests for inequality between two HPGs.
        Equality is considered to be an embedded planar graph isomorphism.

        INPUT:

        - `other` -- object; The object to test against.

        OUTPUT: Boolean; returns True if and only if `other` is not an HPG or is non-isomorphic to this HPG.

        .. SEEALSO::

            :meth:`HourglassPlabicGraph.__eq__`
        """
        return not self.__eq__(other)

    def traverse(self):
        r"""
        Traverses this HPG through a breadth-first search beginning from the first boundary vertex.
        (Is this actually BFS?)

        OUTPUT: A tuple;
            The first element is an array of visited HalfHourglasses (including twins) in BFS order.
            The second element is an array of visited HalfHourglasses with repetitions as they are revisited.
            The third element is an array of visited Vertices in BFS order.
            The fourth element is an array of visited Vertices with repetitions as they are revisited.
        """
        if len(self._boundary_vertices) <= 1: return (None, None)

        # Find edge into the graph; this is assumed to be the first hourglass from the
        # first boundary vertex into the graph
        hh = self._get_hourglass_by_id(0, len(self._boundary_vertices) - 1).ccw_next()

        half_hourglasses_visited = [hh]
        half_hourglass_history = [hh]
        vertices_visited = []
        vertex_history = []

        # Perform breadth-first search to traverse the graph
        i = 0
        while i < len(half_hourglasses_visited):
            hh = half_hourglasses_visited[i]
            hh_twin = hh.twin()
            hh_next = hh.cw_next()
            v = hh.v_from()
            if hh_twin not in half_hourglasses_visited:
                half_hourglasses_visited.append(hh_twin)
            half_hourglass_history.append(hh_twin)

            if hh_next not in half_hourglasses_visited:
                half_hourglasses_visited.append(hh_next)
            half_hourglass_history.append(hh_next)

            if v not in vertices_visited:
                vertices_visited.append(v)
            vertex_history.append(v)

            i += 1

        return half_hourglasses_visited, half_hourglass_history, vertices_visited, vertex_history

    def __hash__(self):
        r"""
        Computes the hash value of this object.

        OUTPUT: Integer; the hash value of the object.

        EXAMPLES:

            sage: hpg = HourglassPlabicGraph(8)
            sage: hpg.__hash__()
            2932925276731088263

        Ensure the hash value does not change for equal objects:

            sage: hpg1 = HourglassPlabicGraph(6)
            sage: hpg2 = HourglassPlabicGraph(6)
            sage: hpg1.__hash__() == hpg2.__hash__()
            True
        """
        hh_visited, hh_history, v_visited, v_history = self.traverse()
        hh_hash = tuple((hh_visited.index(hh), hh.multiplicity()) for hh in hh_history)
        v_hash = tuple((v_visited.index(v), v.filled) for v in v_history)
        return hash((hh_hash, v_hash))

    def is_isomorphic(self, other):
        r"""
        Tests for a planar graph isomorphism between this graph and other.

        INPUT:

        - `other` -- HourglassPlabicGraph; The graph to test against.

        OUTPUT: Boolean; returns True if and only if `other` is isomorphic to this.

        EXAMPLES:

        This example constructs two isomorphic HPGs and tests equality.

            hpg1 = HourglassPlabicGraph()
            hpg1.construct_face(6, [2, 1, 2, 1, 2, 1])
            hpg2 = HourglassPlabicGraph()
            hpg2.construct_face(6, [2, 1, 2, 1, 2, 1])
            hpg1.is_isomorphic(hpg2)
            True

        This example demonstrates that edge multiplicities are relevant to isomorphism.
        See the WARNING for issues with testing otherwise isomorphic graphs with different orientations.

            hpg1 = HourglassPlabicGraph()
            hpg1.construct_face(6, [2, 1, 2, 1, 2, 1])
            hpg2 = HourglassPlabicGraph()
            hpg2.construct_face(6, [1, 2, 1, 2, 1, 2])
            hpg1.is_isomorphic(hpg2)
            False

        This example uses two clearly non-isomorphic graphs.

            hpg1 = HourglassPlabicGraph()
            hpg1.construct_face(6, [2, 1, 2, 1, 2, 1])
            hpg2 = HourglassPlabicGraph()
            hpg2.construct_face(4, [2, 1, 2, 1])
            hpg1.is_isomorphic(hpg2)
            False

        .. WARNING::

            The test for isomorphism assumes graphs are also "oriented" the same way; that is,
            their ID 0 boundary vertex is in the same place.

            This test also fails if there are isolated components.

            This function is not intended to be used on non "properly formed" HPGs, and may fail or crash.
        """
        self_hh_visited, self_hh_history, self_v_visited, self_v_history = self.traverse()
        other_hh_visited, other_hh_history, other_v_visited, other_v_history = other.traverse()

        if len(self_v_visited) != len(other_v_visited) or len(self_v_history) != len(other_v_history):
            return False

        v_iso = set(zip(self_v_visited, other_v_visited))
        v_check = set(zip(self_v_history, other_v_history))

        if v_iso != v_check or any(a.filled != b.filled for a, b in v_iso):
            return False

        if len(self_hh_visited) != len(other_hh_visited) or len(self_hh_history) != len(other_hh_history):
            return False

        hh_iso = set(zip(self_hh_visited, other_hh_visited))
        hh_check = set(zip(self_hh_history, other_hh_history))

        if hh_iso != hh_check or any(a.multiplicity() != b.multiplicity() for a, b in hh_iso):
            return False

        return True

    # Construction functions

    def construct_boundary(self, n, filling=True, r=10):
        r"""
        Creates n boundary vertices, labeled from 0 to n-1, and connects them with phantom edges.
        The vertices will be set to filling. This function can only be called on an empty graph.

        INPUT:

        - ``n`` -- positive integer; the number of boundary vertices to create.

        - ``filling`` -- boolean or boolean iterable (default: ``True``); Whether the vertices should be filled. If an iterable, the filled/unfilled statuses of the boundary vertices, starting from 0.

        - ``r`` -- float (default: `10`); the radius of the boundary.

        EXAMPLES:

            sage: HPG = HourglassPlabicGraph()
            sage: HPG.construct_boundary(8)
            sage: HPG.order()
            8

        It is an error to call this function on a non-empty graph.

            sage: HPG = HourglassPlabicGraph(10)
            sage: HPG.construct_boundary(10)
            AssertionError: Cannot call construct_boundary on a non-empty graph.
        """
        assert self.order() == 0, "Cannot call construct_boundary on a non-empty graph."

        for i in range(0, n):
            self._boundary_vertices[i] = Vertex(i, r*math.sin((i+0.5)*2*math.pi/n), r*math.cos((i+0.5)*2*math.pi/n), filling if isinstance(filling, bool) else filling[i], True)

        for i in range(0, n-1):
            Vertex.create_hourglass_between(self._boundary_vertices[i], self._boundary_vertices[i+1], 0)
        hh = Vertex.create_hourglass_between(self._boundary_vertices[n-1], self._boundary_vertices[0], 0)

        inner_face = Face(ID.get_new_id("face"), hh)
        outer_face = Face(ID.get_new_id("face"), hh.twin())
        self._faces[inner_face.id] = inner_face
        self._faces[outer_face.id] = outer_face

    def construct_face(self, n, multiplicities, r=10):
        r"""
        Initializes an hourglass plabic graph with n boundary vertices at a radius of r and an inner face of n vertices connected to the boundary.
        The vertices on the boundary and the vertices on the face will alternate in filled/unfilled status. The multiplicities of the hourglasses
        between the face vertices is specified using the multiplicities array.
        This function can only be called on an empty graph.

        INPUT:

        - ``n`` -- integer; the number of boundary vertices and face vertices to create each. Must be even.

        - `multiplicities` -- positive int array; the multiplicities of the hourglasses between internal vertices.

        - ``r`` -- float; the radius of the boundary. Defaults to 10.

        EXAMPLES:

            sage: HPG = HourglassPlabicGraph()
            sage: HPG.construct_face(6, [2, 1, 2, 1, 2, 1])
            sage: print(HPG.get_trip_perms())
            [['4', '3', '0', '5', '2', '1'], ['3', '4', '5', '0', '1', '2'], ['2', '5', '4', '1', '0', '3']]

        It is an error to call this function on a non-empty graph.

            sage: HPG = HourglassPlabicGraph(10)
            sage: HPG.construct_face(6, [2, 1, 2, 1, 2, 1])
            AssertionError: Cannot call construct_boundary on a non-empty graph.
        """
        assert n % 2 == 0, "n must be an even number."

        fillings = [i % 2 == 1 for i in range(0, n)]
        self.construct_boundary(n, fillings, r)

        r *= 0.6
        last_id = None
        first_id = None

        for i in range(0, n):
            v_id = i + n
            self.create_vertex(v_id, r*math.sin((i+0.5)*2*math.pi/n), r*math.cos((i+0.5)*2*math.pi/n), not fillings[i], False, v_id)

            # Hourglass to boundary
            self.create_hourglass_by_id(v_id, i, 1)
            if first_id is None:
                first_id = v_id
            else:
                # Hourglass to previous vertex in face
                self.create_hourglass_by_id(v_id, last_id, multiplicities[i-1])
                if i == n - 1:
                    # Hourglass from last to first vertex in face
                    self.create_hourglass_by_id(v_id, first_id, multiplicities[i])
            last_id = v_id

    def create_vertex(self, v_id, x, y, filled, boundary=False, verify_id=False):
        r"""
        Adds a vertex with the given parameters to the graph and returns it.

        INPUT:
        
        - `v_id` -- hashable, unique object; The id given to the vertex.
        
        - ``x`` -- float; The x position of the vertex
        
        - ``y`` -- float; The y position of the vertex
        
        - `filled` -- Boolean; Whether the vertex is to be filled or not.
        
        - `boundary` -- Boolean (default: `False`); Whether the vertex is on the boundary.
        
        - `verify_id` -- Boolean (default: `False`); Check whether v_id is already in use.

        OUTPUT: Vertex

        EXAMPLES:

            sage: HPG = HourglassPlabicGraph(6)
            sage: HPG.create_vertex(6, 0, 0, True)
            Vertex 6 at (0, 0), filled

        It is problematic to create a vertex with an existing ID, but no error will be thrown unless `verify_id` is `True`.

            sage: HPG.create_vertex(6, 0, 1, False, False, None, True)
            ValueError: v_id already in use.

        .. NOTE::

            This function is intended primarily for creating interior vertices. To easily set up a boundary
            with proper IDs, use `construct_boundary` or `construct_face`.
        """
        if verify_id and ((not boundary and v_id in self._inner_vertices) or (boundary and v_id in self._boundary_vertices)): raise ValueError(f"v_id {v_id} already in use.")

        vertex = Vertex(v_id, x, y, filled, boundary)
        if boundary: self._boundary_vertices[v_id] = vertex
        else: self._inner_vertices[v_id] = vertex
        return vertex

    def remove_vertex_by_id(self, v_id):
        r"""
        Removes the vertex with the given ID (and all connected hourglasses).

        INPUT:

        - `v_id` -- object; The ID of the vertex to remove.

        EXAMPLES:

            sage: HPG = HourglassPlabicGraph(6)
            sage: HPG.remove_vertex_by_id(5)
            sage: HPG.order()
            5

        It is an error to try to remove a vertex not in the graph.

            sage: HPG.remove_vertex_by_id('nonexistent_id')
            ValueError: id 5 does not correspond to any vertex.

        .. NOTE::

            This function internally looks up the vertex ID, then calls remove_vertex.
            It is equivalent to calling HPG.remove_vertex(HPG._get_vertex(vid)).
        """
        del_vertex = self._get_vertex(v_id)
        self.remove_vertex(del_vertex)

    def remove_vertex(self, del_vertex):
        r"""
        Removes the provided vertex (and all connected hourglasses).

        INPUT:

        - `v_id` -- object; The ID of the vertex to remove.

        EXAMPLES:

            sage: HPG = HourglassPlabicGraph(6)
            sage: del_v = HPG._get_vertex(5)
            sage: HPG.remove_vertex(del_v)
            sage: HPG.order()
            5

        It is an error to try to remove a vertex not in the graph.

            sage: HPG.remove_vertex_by_id('nonexistent_id')
            ValueError: The provided vertex is not in the graph.
        """
        # Store hourglasses in a list to avoid issues with removing
        # elements while iterating over dihedral element
        if del_vertex.id in self._inner_vertices: del self._inner_vertices[del_vertex.id]
        elif del_vertex.id in self._boundary_vertices: del self._boundary_vertices[del_vertex.id]
        else: raise ValueError("The provided vertex is not in the graph.")
        
        del_hourglasses = del_vertex.get_hourglasses_as_list()
        for hh in del_hourglasses:
            self._remove_hourglass_internal(hh, del_vertex, hh.v_to())

    def create_hourglass_by_id(self, v1_id, v2_id, multiplicity=1):
        r"""
        Creates an hourglass (two HalfHourglasses) between the vertices
        identified by `v1_id` and `v2_id`, and returns it.

        INPUT:

        - `v1_id` -- object; the ID of the first Vertex.
        
        - `v2_id` -- object; the ID of the second Vertex.
        
        - `multiplicity` -- nonnegative integer; multiplicity of the constructed hourglass.. Assumed to be an integer `\geq 1`.

        OUTPUT: HalfHourglass; the HalfHourglass from `v1_id` to `v2_id`.

        EXAMPLES:

            TODO
        """
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)

        return self.create_hourglass(v1, v2, multiplicity)

    def create_hourglass(self, v1, v2, multiplicity=1):
        r"""
        Creates an hourglass (two HalfHourglasses) between v1 and v2, and returns it.

        INPUT:

        - `v1` -- Vertex; the first Vertex.
        
        - `v2` -- Vertex; the second Vertex.
        
        - `multiplicity` -- nonnegative integer; multiplicity of the constructed hourglass.. Assumed to be an integer `\geq 1`.

        OUTPUT: HalfHourglass; the HalfHourglass from `v1` to `v2`.

            TODO

        .. NOTE:

            This function also generates the necessary faces that would be created by this edge.
        """
        new_hh = Vertex.create_hourglass_between(v1, v2, multiplicity)

        # Create faces

        face = None
        # First, find an already existing reference to this hourglass's right face
        # There is a chance we are connecting two faces, so we should find the second one
        # and remove it from our list
        for hh in new_hh.iterate_right_turns():
            if hh.right_face() is not None:
                if face is None: face = hh.right_face()
                elif face is not hh.right_face():
                    del self._faces[hh.right_face().id]
                    break
        if face is not None:
            face.initialize_half_hourglasses(new_hh)
        # If none exists, create a new one
        else:
            face = Face(ID.get_new_id("face"), new_hh)
            self._faces[face.id] = face

        # Either the twin's face will be the same as this, or we will need to create a new face since the old face
        # will be the same as the one reused for the hourglass and will no longer be valid
        if new_hh.twin().right_face() is None:
            face = Face(ID.get_new_id("face"), new_hh.twin())
            self._faces[face.id] = face

        return new_hh

    def remove_hourglass_by_id(self, v1_id, v2_id):
        r"""
        Removes the hourglass between the vertices identified by `v1_id` and `v2_id`.

        INPUT:

        - `v1_id` -- object; the ID of the first Vertex.
        
        - `v2_id` -- object; the ID of the second Vertex.

        EXAMPLES:

            TODO
        """
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)
        self.remove_hourglass(v1, v2)

    def remove_hourglass(self, v1, v2):
        r"""
        Removes the hourglass between the vertices `v1` and `v2`.

        INPUT:

        - `v1` -- Vertex; the first Vertex.
        
        - `v2` -- Vertex; the second Vertex.

        EXAMPLES:

            TODO
        """
        self._remove_hourglass_internal(self._get_hourglass(v1, v2), v1, v2)

    def _remove_hourglass_internal(self, del_hh, v1, v2):
        r"""
        An internal function to assist in removing hourglasses. Do not use; instead use `remove_hourglass_by_id` or `remove_hourglass`.
        """
        face1 = None
        hh1 = None
        face2 = None
        hh2 = None
        # get a new hourglass for each face the hourglass belongs to
        for hh in del_hh.iterate_right_turns():
            if hh is not del_hh and hh is not del_hh.twin() and hh.right_face() is not None:
                face1 = hh.right_face()
                hh1 = hh
                break
        for hh in del_hh.twin().iterate_right_turns():
            if hh is not del_hh and hh is not del_hh.twin() and hh.right_face() is not None:
                face2 = hh.right_face()
                hh2 = hh
                break

        Vertex.remove_hourglass_between(v1, v2)

        if face1 is not None:
            face1.initialize_half_hourglasses(hh1)
        if face2 is not None:
            if face2 is not face1:
                del self._faces[face2.id]
            # This should only happen if deletion results in seperate subgraphs
            # This check avoids creating a new face for an isolated vertex
            elif not (del_hh.right_turn() is del_hh.twin() or del_hh.twin().right_turn() is del_hh):
                face2 = Face(ID.get_new_id("face"), hh2)
                self._faces[face2.id] = face2
        # case: this is the last hourglass of the face
        if face1 is None and face2 is None:
            del self._faces[del_hh.right_face().id]

    def thicken_hourglass_by_id(self, v1_id, v2_id):
        r"""
        Thickens the hourglass between vertices identified by `v1_id` and `v2_id`.

        INPUT:

        - `v1_id` -- object; the ID of the first Vertex.
        
        - `v2_id` -- object; the ID of the second Vertex.

        EXAMPLES:

            TODO
        """
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)
        self.thicken_hourglass(v1, v2)
    add_strand_by_id = thicken_hourglass_by_id # alias

    def thicken_hourglass(self, v1, v2):
        r"""
        Thickens the hourglass between the vertices `v1` and `v2`.

        INPUT:

        - `v1` -- Vertex; the first Vertex.
        
        - `v2` -- Vertex; the second Vertex.

        EXAMPLES:

            TODO
        """
        self._get_hourglass(v1, v2).thicken()
    add_strand = thicken_hourglass # alias

    def thin_hourglass_by_id(self, v1_id, v2_id):
        r"""
        Thins the hourglass between vertices identified by `v1_id` and `v2_id`.

        INPUT:

        - `v1_id` -- object; the ID of the first Vertex.
        
        - `v2_id` -- object; the ID of the second Vertex.

        EXAMPLES:

            TODO
        """
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)
        self.thin_hourglass(v1, v2)
    remove_strand_by_id = thin_hourglass_by_id # alias

    def thin_hourglass(self, v1, v2):
        r"""
        Thins the hourglass between the vertices `v1` and `v2`.

        INPUT:

        - `v1` -- Vertex; the first Vertex.
        
        - `v2` -- Vertex; the second Vertex.

        EXAMPLES:

            TODO
        """
        self._get_hourglass(v1, v2).thin()
    remove_strand = thin_hourglass # alias

    # Moves

    def is_square_move_valid(self, face_id, r=4):
        r"""
        Verifies that the provided face can perform a square move.

        - `face_id` -- object; the ID of the provided face.

        - ``r`` -- positive integer (default: `4`); the valence of the graph. Assumed to be an integer `\geq 1`.

        OUTPUT: Boolean; Whether a square move is valid on the face.

        EXAMPLES:

            TODO
        """
        return self._get_face(face_id).is_square_move_valid(r)

    def square_move(self, face_id, r=4):
        r"""
        Verifies that the provided face can perform a square move.

        - `face_id` -- object; the ID of the provided face.

        - ``r`` -- positive integer (default: `4`); the valence of the graph. Assumed to be an integer `\geq 1`.

        EXAMPLES:

            TODO
        """
        face = self._get_face(face_id)

        new_vertices, removed_vertices = face.square_move(r)
        # NOTE: By assumption, all vertices involved in a square move are inner vertices
        for v in new_vertices:
            self._inner_vertices[v.id] = v
        for v in removed_vertices:
            del self._inner_vertices[v.id]
        # A square move does not add or remove any faces, but adjacent faces
        # should have their hourglass heads set to hourglasses that are guaranteed
        # to persist -- i.e. those of this face.
        # Note that hh will have face as its right face.
        for hh in face:
            hh.left_face().initialize_half_hourglasses(hh.twin())

    def is_cycle_valid(self, face_id, v1_id, v2_id):
        r"""
        Verifies that the provided face can perform a cycle move, starting from the .

        - `face_id` -- object; the ID of the provided face.

        - `v1_id` -- object; the ID of the first Vertex.
        
        - `v2_id` -- object; the ID of the second Vertex.

        OUTPUT: Boolean; Whether a square move is valid on the face.

        EXAMPLES:

            TODO
        """
        return self._get_face(face_id).is_cycle_valid(self._get_hourglass_by_id(v1_id, v2_id))

    def cycle(self, face_id, v1_id, v2_id):
        r"""
        """
        self._get_face(face_id).cycle(self._get_hourglass_by_id(v1_id, v2_id))

    def is_benzene_move_valid(self, face_id):
        r"""
        """
        return self._get_face(face_id).is_benzene_move_valid()
    move_square = square_move # alias

    def benzene_move(self, face_id):
        r"""
        """
        self._get_face(face_id).benzene_move()
    move_benzene = benzene_move # alias

    # Checks

    def is_r_valent(self, r=4, verbose=False):
        r"""
        """
        for v in self._inner_vertices.values():
            if v.total_degree() != r:
                if verbose: print(f"Graph is not r-valent. Vertex {v.id} does not have degree {r}. Instead, degree is {v.total_degree()}.")
                return False
        return True

    def is_fully_reduced(self, r=4, verbose=False):
        r"""
        The conditions for being fully reduced:
        - r-valent
        - All trips should have no self-intersections, including nontrivial isolated trips
        - For boundary trips, no trip_i should have an essential double crossing with another trip_i or a trip_i+1
        An isolated trip is a trip starting from an interior strand that never reaches the boundary.
        It is trivial if it loops within the same hourglass.
        An essential double crossing occurs when two paths intersect (cross rather than reflect) twice
        while traveling in the same direction, ignoring consecutive intersections.
        """
        # Verify r-valence
        if (not self.is_r_valent(r, verbose)): return False

        # Verify no nontrivial isolated trips
        for hh in self._get_interior_hourglasses():
            for strand in hh.iterate_strands():
                for i in range(1, r):
                    trip = strand.get_trip(i)
                    if not trip[0].v_from().boundary and len(trip) > 2:
                        if verbose: print(f"Isolated trip {i} detected passing through {trip[0]}.")
                        return False

        # Get all trips starting on the boundary in half-strand format
        trips = [[self.get_trip(v, i) for v in self._boundary_vertices.values()] for i in range(1, r)]

        # Returns true if trip does not intersect with itself.
        def validate_no_self_intersections(trip):
            vertices = { trip[0].v_from() }
            for strand in trip:
                if strand.v_to() in vertices:
                    return False
                vertices.add(strand.v_to())
            return True

        # Verify no self-intersections
        for i, trip_is in enumerate(trips):
            for trip in trip_is:
                if not validate_no_self_intersections(trip):
                    if verbose: print(f"trip{i+1} from vertex {trip[0].v_from().id} self-intersects.")
                    return False

        # Internal helper functions for double crossing checks

        # Returns an integer.
        # If the resulting crossing is valid - that is, the
        # orientations of the hourglasses going in and out
        # of the crossing genuinely intersect - returns the
        # number of shared vertices along the trips. Otherwise,
        # returns -1.
        def validate_crossing(trip1, ind1, trip2, ind2):
            # Keep track of ingoing hourglasses
            in_ind1 = ind1
            in_ind2 = ind2
            out_ind1 = ind1
            out_ind2 = ind2
            count = 0

            # Trace the shared trip intil it diverges
            while (out_ind1 < len(trip1) and out_ind2 < len(trip2)
                   and trip1[out_ind1].v_to() is trip2[out_ind2].v_to()):
                out_ind1 += 1
                out_ind2 += 1
                count += 1

            # If the crossing begins or ends at the boundary, we can assume it is valid.
            if in_ind1 == 0 or out_ind1 == len(trip1): return count

            inhh1 = trip1[in_ind1].twin()
            inhh2 = trip2[in_ind2].twin()
            outhh1 = trip1[out_ind1]
            outhh2 = trip2[out_ind2]

            # Validate crossing orientation
            # Case 1: Crossing is immediate
            # Verify that the order of hourglasses around the vertex
            # alternates between trip1 and trip2.
            if (count == 1):
                for hh in inhh1.iterate_clockwise():
                    if hh is outhh1: return -1
                    elif hh is inhh2 or outhh2: break
                for hh in inhh1.iterate_counterclockwise():
                    if hh is outhh1: return -1
                    elif hh is inhh2 or outhh2: return count
                # this should never be reached in a well-formed graph
                raise Exception("Issue with crossing validation. Hourglasses do not belong to same vertex.")

            # Case 2: Some shared edges along crossing
            # verify that that either the trip2 hourglasses
            # or the shared hourglasses are first in clockwise
            # order from the trip1 hourglasses
            else:
                inhh_shared = trip1[in_ind1+1]
                outhh_shared = trip1[out_ind1-1].twin()

                encounter_first = None
                encounter_second = None
                for hh in inhh1.iterate_clockwise():
                    if hh is inhh_shared:
                        encounter_first = outhh_shared
                        encounter_second = outhh2
                        break
                    elif hh is inhh2:
                        encounter_first = outhh2
                        encounter_second = outhh_shared
                        break
                for hh in outhh1.iterate_clockwise():
                    if hh is encounter_first: return count
                    elif hh is encounter_second: return -1
                # this should never be reached in a well-formed graph
                raise Exception("Issue with crossing validation. Hourglasses do not belong to same vertex.")

        # Finds the first crossing between trip1 and trip2
        # starting at the hourglasses indicated by ind1 and ind2.
        # If a crossing is found, returns the indices of the
        # outgoing hourglasses for each trip in a tuple.
        # If no crossing is found, returns None.
        def find_crossing_from(trip1, ind1, trip2, ind2):
            for i1 in range(ind1, len(trip1) - 1):
                for i2 in range(ind2, len(trip2) - 1):
                    # We only care if we see an intersection
                    if trip1[i1].v_to() is not trip2[i2].v_to(): continue

                    count = validate_crossing(trip1, i1, trip2, i2)
                    # Because there are no self intersections, if we encounter
                    # a potential self intersection on trip1's hourglass but it
                    # fails, we won't encounter another one for that hourglass.
                    if count == -1: break
                    return i1 + count, i2 + count
            return None

        def do_trips_double_cross(trip1, trip2):
            next_inds = find_crossing_from(trip1, 0, trip2, 0)
            if next_inds is None: return False
            final_inds = find_crossing_from(trip1, next_inds[0], trip2, next_inds[1])
            return (final_inds is not None)

        # Validate no double crossings
        for i, trip_is in enumerate(trips):
            all_compare_trips = trips[i] + (trips[i+1] if i < len(trips)-1 else [])
            for a in range(0, len(trip_is)):
                trip1 = trip_is[a]
                for b in range(a+1, len(all_compare_trips)):
                    trip2 = all_compare_trips[b]
                    if (do_trips_double_cross(trip1, trip2)):
                        if verbose: print(f"trip{i+1} from vertex {trip1[0].v_from().id} and trip{i+1 if b < len(trip_is) else i+2} from vertex {trip2[0].v_from().id} double cross.")
                        return False
        return True

    # Layout functions

    def make_circular(self, r=10):
        r"""
        """
        n = len(self._boundary_vertices.values())
        for i,v in self._boundary_vertices:
            v.x = r*math.sin((i+0.5)*2*math.pi/n)
            v.y = r*math.cos((i+0.5)*2*math.pi/n)

        self.tutte_layout()
        self.layout = "circular"

    def tutte_layout(self, error=0.01, max_iter = 1000):
        r"""
        from https://cs.brown.edu/people/rtamassi/gdhandbook/chapters/force-directed.pdf.
        """
        for i in range(max_iter):
            err = 0
            for v in self._inner_vertices:
                neighbours = v.get_neighbors()
                x_new = sum(w.x for w in neighbours)/len(neighbours)
                y_new = sum(w.y for w in neighbours)/len(neighbours)
                err += (v.x-x_new)**2 + (v.y-y_new)**2
                v.x, v.y = x_new, y_new
            if err < error:
                break

    # Trip functions

    def get_trip(self, vertex, i, output='half_strands'):
        r"""
        vertex: the initial boundary Vertex; assumes multiplicity 1
        i: computes trip_i by taking the ith left at unfilled/ith right at filled
        output: if output = 'half_strands', returns an array of HalfStrands. Otherwise, returns HalfHourglasses.

        Returns the list of HalfHourglasses/HalfStrands the trip visits in order.
        """

        return vertex.get_trip(i, output)

    def get_trip_perm(self, i, output='half_strands'):
        r"""
        Computes the ith trip permutation.
        The trip i permutation is generated by finding where trip i sends each boundary vertex to.
        Boundary vertices are assumed to be numbered 1, 2, ..., n CW starting slightly east of due north.
        """
        perm = []
        for vertex in self._boundary_vertices.values():
            trip = vertex.get_trip(i, output)
            final_vertex = trip[-1].v_to()
            perm.append(final_vertex.id)
        return perm

    def get_trip_perms(self, output='half_strands'):
        r"""
        Returns a list [t_1, ..., t_{r-1}] where t_i is the ith trip permutation
        and r is the maximum degree of an internal vertex.
        """
        r = max(v.total_degree() for v in self._inner_vertices.values()) # This is quite inefficient, could be a cached value provided by user?
        return [self.get_trip_perm(i, output) for i in range(1, r)]

    def separation_labeling(self, base_face, r=4, verbose=False):
        r"""
        Applies separation labelings to all HalfHourglasses in this graph departing from unfilled vertices.

         INPUT:

        - `base_face` -- Face; the base face of the separation labeling.
    
        - ``r`` -- positive integer (default: `4`); the valence of the graph. Assumed to be an integer `\geq 1`.

        - `verbose` -- Boolean (default: `False`); whether to print informative output.
    
        EXAMPLES:

            TODO
        """
        # Requisite data structures:
        # - Grid of faces and trips (dict of tuple trip, face to boolean)
        # - Dict from (oriented) strands to tuple of trips through strand
        # However, trips (arrays) are not hashable, so instead we simply
        # store the starting vertex id and use that plus the i to uniquely
        # identify trips. This means we also must use the same scheme to
        # identify trips for the separating_trips dict.
        separating_trips = dict()
        strand_to_trips = dict()

        tripid = lambda trip, i : (trip[0].v_from().id, i)

        if verbose: print(f"Performing separation_labeling with base_face {base_face.id} ({', '.join(str(hh.v_from().id) for hh in base_face)}).")

        # Get all trips by strand
        # trips[i] are all trip is
        trips = [[self.get_trip(v, i) for v in self._boundary_vertices.values()] for i in range(1, r)]

        # Populate strand_to_trips and separating_trips dicts
        for i, trip_is in enumerate(trips):
            for trip in trip_is:
                #if verbose: print(f"Found trip {i+1} from vertex {trip[0].v_from().id}.")
                for strand in trip:
                    # Only consider strands based at white (unfilled)
                    if strand.v_from().filled: continue

                    # Initialize if necessary
                    if strand not in strand_to_trips:
                        strand_to_trips[strand] = [None] * (r-1)

                    # Use uniquely identifying tuple instead of array itself
                    strand_to_trips[strand][i] = tripid(trip, i)

                # Figure out separations for trip
                # Perform a DFS on faces between the trip's path and the boundary to the right
                explore_stack = list()
                visited_faces = set()
                # Define boundary for DFS
                trip_hourglasses = set()
                for strand in trip:
                    trip_hourglasses.add(strand.hourglass())
                    r_face = strand.right_face()
                    # Begin pushing faces on the rightward interior to the stack
                    # This could be avoided -- only one face is necessary to start with
                    if r_face not in visited_faces:
                        #if verbose: print(f" Found face {r_face.id} to the right of trip.")
                        visited_faces.add(r_face)
                        explore_stack.append(r_face)

                # Perform DFS
                while explore_stack:
                    face = explore_stack.pop()
                    for hh in face:
                        # Avoid traversing past the boundary
                        if hh.is_boundary() or hh in trip_hourglasses or hh.twin() in trip_hourglasses: continue
                        l_face = hh.left_face()
                        if l_face not in visited_faces:
                            #if verbose: print(f" Found face {l_face.id} to the right of trip.")
                            visited_faces.add(l_face)
                            explore_stack.append(l_face)

                # Value stored for this tuple is equal to whether the base face and this face are on
                # different sides of the trip, ie the trip is separating
                
                visited_base_face = base_face in visited_faces
                #if verbose: print(f"base_face{' ' if visited_base_face else ' not '}found to the right of trip.")
                for face in self._faces.values():
                    separating_trips[(tripid(trip, i), face)] = (visited_base_face != (face in visited_faces))

        hourglasses = self._get_interior_hourglasses()
        for hh in hourglasses:
            # Ensure we are rooted at white (unfilled)
            # Note that _get_interior_hourglasses filters out redundant (twin) hourglasses, so we can do this safely
            if hh.v_from().filled: hh = hh.twin()
            if verbose: print(f"Creating label for hourglass from {hh.v_from().id} to {hh.v_to().id}.")
            hh.label = []
            l_face = hh.left_face() # Left face has "white on right" for hourglass rooted at white
            # for each strand: label is # separating trips
            for strand in hh.iterate_strands():
                hh.label.append(sum(((t is not None) and separating_trips[(t, l_face)]) for t in strand_to_trips[strand]))
            if verbose: print(f"Pre-sorted counts: {hh.label}")
            # Sort strand labels, then zip with (1, 2, ..., m) tuple
            hh.label = [x + y for (x, y) in zip(sorted(hh.label), range(1, hh.multiplicity()+1))]
            if verbose: print(f"Created label {hh.label} for hourglass from {hh.v_from().id} to {hh.v_to().id}.")

    # Internal accessors

    def _get_face(self, f_id):
        r"""
        """
        face = self._faces.get(f_id)
        if face is None: raise ValueError(f"id {f_id} does not correspond to any face.")
        return face

    def _get_vertex(self, v_id):
        r"""
        Internal helper function that gets the vertex with the given id from either _inner_vertices or _boundary_vertices, and throws if the id is not found.
        """
        v = self._inner_vertices.get(v_id)
        if v is None:
            v = self._boundary_vertices.get(v_id)
            if v is None: raise ValueError(f"id {v_id} does not correspond to any vertex.")
        return v

    def _get_hourglass_by_id(self, v1_id, v2_id):
        r"""
        """
        return self._get_hourglass(self._get_vertex(v1_id), self._get_vertex(v2_id))
    def _get_hourglass(self, v1, v2):
        return v1.get_hourglass_to(v2)

    def _get_interior_hourglasses(self):
        r"""
        """
        hourglasses = set()
        for vertex in self._inner_vertices.values():
            for hh in vertex:
                if hh.twin() not in hourglasses:
                    hourglasses.add(hh)
        return hourglasses

    def order(self):
        r"""
        The number of vertices in this graph.
        """
        return len(self._inner_vertices) + len(self._boundary_vertices)

    # Serialization/Data Conversion

    def to_graph(self, hourglass_labels=False): # TODO: VERIFY/TEST
        r"""
        Creates an equivalent sagemath Graph. Represents strands in an hourglass in the label.
        """
        vertex_refs = list(self._inner_vertices.values()) + list(self._boundary_vertices.values())
        edge_refs = set()
        for v in vertex_refs:
            for hh in v:
                if not hh.twin() in edge_refs:
                    edge_refs.add(hh)

        vertices = [v.id for v in vertex_refs]
        edges = [(h.v_from().id, h.v_to().id, h.label if hourglass_labels else h.strand_count()) for h in edge_refs]
        pos = {v.id:(v.x,v.y) for v in vertex_refs}
        g = Graph([vertices, edges], format='vertices_and_edges', pos=pos)
        return g

    # Update with **kwds argument?
    def plot(self):
        r"""
        """
        vertex_refs = list(self._inner_vertices.values()) + list(self._boundary_vertices.values())
        vertex_colors = {"gray":[v.id for v in vertex_refs if v.filled],  "white":[v.id for v in vertex_refs if not v.filled]}
        return self.to_graph().plot(vertex_colors=vertex_colors, edge_labels=True)

    @classmethod
    def from_dict(cls, data):
        r"""
        Constructs a new hourglass plabic graph from a dictionary representing
        a JSON encoding of the graph.
        """
        HPG = cls()

        if 'layout' in data: HPG.layout = data['layout']

        # prepare internal data for graph
        for v_data in data['vertices']:
            HPG.create_vertex(v_data['id'], v_data['x'], v_data['y'], v_data['filled'], v_data['boundary'])

        for e in data['edges']:
            label = e['label'] if 'label' in e else None
            hh = HPG.create_hourglass_by_id(e['sourceId'], e['targetId'], e['multiplicity'])
            hh.label = label

         # add boundary edges
        sorted_boundary_vertices = list(HPG._boundary_vertices.values())
        if HPG.layout == 'circular':
            sorted_boundary_vertices.sort(key = lambda v: math.atan2(-v.x, -v.y)) # cw orientation
        elif HPG.layout == 'linear':
            sorted_boundary_vertices.sort(key = lambda v: v.x) # left to right
        else:
            raise NotImplementedError("Layout must be circular or linear.")
        for i in range(0, len(sorted_boundary_vertices)):
            v_from = sorted_boundary_vertices[i]
            v_to   = sorted_boundary_vertices[(i+1)%len(sorted_boundary_vertices)]
            HPG.create_hourglass(v_from, v_to, 0)

        return HPG

    def to_dict(self):
        r"""
        Encode this HourglassPlabicGraph as a dictionary representing
        a JSON encoding of the graph.
        """
        vertices = list(self._inner_vertices.values()) + list(self._boundary_vertices.values())
        edges = set()
        for v in vertices:
            for hh in v:
                # do not record boundary edges
                if not (hh.is_boundary() or hh.twin() in edges):
                    edges.add(hh)

        d = {
            'edges': [{
                "multiplicity": e.multiplicity(),
                "sourceId": e.v_from().id,
                "targetId": e.v_to().id,
                "label": e.label,
                } for e in edges],
            'vertices': [{
                "id": v.id,
                "x": float(v.x),
                "y": float(v.y),
                "filled": v.filled,
                "boundary": v.boundary,
                } for v in vertices],
            'layout': self.layout,
        }
        return d

    # TESTING
    def print_faces(self):
        for f in self._faces.values():
            print(f.id + ":")
            f.print_vertices()
