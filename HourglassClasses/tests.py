from .idgenerator import ID
from .dihedralelement import DihedralElement
from .halfstrand import HalfStrand
from .halfhourglass import HalfHourglass
from .vertex import Vertex
from .face import Face
from .hourglassplabicgraph import HourglassPlabicGraph
from hourglass2 import HourglassPlabicGraph as HourglassPlabicGraphOld

from .examples import Examples

import math
import json
from sage.graphs.graph import Graph

# Proxy classes for testing lower level classes

class _TestHalfHourglass:
    def twin(self):
        return self

class _TestVertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def all_tests():
    dihedral_element_tests()
    half_strand_tests()
    half_hourglass_tests()
    vertex_tests()
    face_tests()
    hourglass_plabic_graph_tests()
    move_tests()
    serialization_tests()
    reduced_tests()
    separation_labeling_tests()

# TESTS FOR BASE CLASS FUNCTIONALITY

def dihedral_element_tests():
    print("Testing DihedralElement class.")

    d1 = DihedralElement(1)
    d2 = DihedralElement(2)
    d3 = DihedralElement(3)

    assert d1.get_num_elements() == 1, f"d1 should form a 1 element list. Instead has {d1.get_num_elements()}."

    d1.insert_cw_next(d2)
    d2.insert_ccw_next(d3)
    # list order should now be d1, d3, d2
    assert d1.get_num_elements() == 3, f"All 3 elements should be in list. Instead contains only {d1.get_num_elements()}."
    assert d1.get_elements_as_list() == [d1, d3, d2], "Iteration does not form proper list."
    assert (
        d1.cw_next() == d3  and
        d1.ccw_next() == d2 and
        d2.cw_next() == d1  and
        d2.ccw_next() == d3 and
        d3.cw_next() == d2  and
        d3.ccw_next() == d1
    ), "List order is incorrect or list is broken."
    assert (
        [element.id for element in d1.iterate_clockwise()] == [1, 3, 2] and
        [element.id for element in d2.iterate_counterclockwise()] == [2, 3, 1]
    ), "Iterator does not work."

    assert d1.get_cw_ith_element(4) == d3, "get_cw_ith_element is broken."
    assert d1.get_ccw_ith_element(7) == d2, "get_ccw_ith_element is broken."

    d3.remove()
    assert d1.get_num_elements() == 2, "d3 should have been removed correctly."
    d2.remove()
    assert d1.get_num_elements() == 1, "d2 should have been removed correctly."

    print("DihedralElement tests complete.\n")

def half_strand_tests():
    print("Testing HalfStrand class.")

    hh1 = _TestHalfHourglass()
    hh2 = _TestHalfHourglass()

    s1 = HalfStrand(1, hh1)
    assert s1.twin() != None, "s1 should have created a twin."
    assert s1.twin().twin() == s1, "s1's twin's twin should be s1."

    assert s1.get_last_strand_same_hourglass() == s1, "s1 is not linked to itself properly when alone."

    s2 = HalfStrand(2, hh1)
    s3 = HalfStrand(3, hh1)
    s1.insert_cw_next(s2)
    s2.insert_cw_next(s3)
    assert s1.get_last_strand_same_hourglass() == s3, "s1 is not linked to other strands properly when strands are all from same hourglass."

    s4 = HalfStrand(4, hh2)
    s1.insert_ccw_next(s4)
    assert s4.get_last_strand_same_hourglass() == s4, "s4 is not linked to other strands properly when alone with another hourglass."

    s5 = HalfStrand(5, hh2)
    s4.insert_cw_next(s5)
    assert s4.get_last_strand_same_hourglass() == s5, "s4 is not linked to other strands properly when multiple hourglasses."

    print("HalfStrand tests complete.\n")

def half_hourglass_tests():
    print("Testing HalfHourglass class.")

    v1 = _TestVertex(0, 0)
    v2 = _TestVertex(1, 1)
    hh = HalfHourglass(1, v1, v2, 1)
    assert hh.twin() != None, "hh should have created a twin."
    assert hh.twin().twin() == hh, "hh's twin's twin should be hh."
    assert hh.v_to() == hh.twin().v_from() and hh.v_from() == hh.twin().v_to(), "hh and twin should have swapped vertices."
    assert hh.get_angle() == math.pi/4, f"hh angle should be pi/4 (45 degrees). instead, it is {hh.get_angle()}."

    hh.thicken()
    hh.thicken()
    hh.thicken()
    assert hh.strand_count() == 4, f"hh should have 4 strands. Instead, it has {hh.strand_count()}."
    assert len([s for s in hh.iterate_strands()]) == 4, f"Strand iteration on hh should count 4 strands, but instead counts {len([s for s in hh.iterate_strands()])} strands."
    hh.thin()
    hh.thin()
    assert hh.strand_count() == 2, f"hh should have 2 strands. Instead, it has {hh.strand_count()}."

    hhp = HalfHourglass(2, v1, v2, 0)
    assert hhp.is_phantom() and hhp.strand_count() == 0, "hhp should be a phantom (boundary) edge."

    hh3 = HalfHourglass(3, v1, v2, 5)
    hh4 = HalfHourglass(4, v1, v2, 2)

    hh.insert_cw_next(hhp)
    hhp.insert_cw_next(hh3)
    hh.insert_ccw_next(hh4)

    # list order should now be hh, hhp, hh3, hh4
    assert hh.strand_count()  == 2, f"Strands were not linked properly between hourglasses during insertions. hh should have 2 strands. Instead has {hh.strand_count()}."
    assert hhp.strand_count() == 0, f"Strands were not linked properly between hourglasses during insertions. hhp should have 2 strands. Instead has {hhp.strand_count()}."
    assert hh3.strand_count() == 5, f"Strands were not linked properly between hourglasses during insertions. hh3 should have 2 strands. Instead has {hh3.strand_count()}."
    assert hh4.strand_count() == 2, f"Strands were not linked properly between hourglasses during insertions. hh4 should have 2 strands. Instead has {hh4.strand_count()}."
    assert hh._half_strands_head.get_num_elements() == 2 + 5 + 2, "Strands were not linked properly all the way around during insertions."

    assert len([s for s in hh.iterate_strands()]) == 2, f"Strand iteration on hh should count 2 strands, but instead counts {len([s for s in hh.iterate_strands()])} strands."
    assert len([s for s in hhp.iterate_strands()]) == 0, f"Strand iteration on hhp should count 0 strands, but instead counts {len([s for s in hhp.iterate_strands()])} strands."
    assert len([s for s in hh3.iterate_strands()]) == 5, f"Strand iteration on hh3 should count 5 strands, but instead counts  {len([s for s in hh3.iterate_strands()])} strands."
    assert len([s for s in hh4.iterate_strands()]) == 2, f"Strand iteration on hh4 should count 2 strands, but instead counts  {len([s for s in hh4.iterate_strands()])} strands."

    hhp.remove()
    hh3.remove()
    # list order should now be hh, hh4
    assert hh.strand_count() == 2 and hh4.strand_count() == 2, "Strands were not linked properly between hourglasses during removals."
    assert hh._half_strands_head.get_num_elements() == 2 + 2, "Strands were not linked properly all the way around during removals."

    #TODO: test is_left_face_valid

    print("HalfHourglass tests complete.\n")

def vertex_tests():
    print("Testing Vertex class.")

    v1 = Vertex(1, 0, 0, True)
    v2 = Vertex(2, 1, 0, False)
    v3 = Vertex(3, 1, 1, True)
    v4 = Vertex(4, 0, 1, False)

    Vertex.create_hourglass_between(v1, v2, 1)
    Vertex.create_hourglass_between(v1, v3, 2)
    Vertex.create_hourglass_between(v1, v4, 5)
    Vertex.create_hourglass_between(v2, v4, 0)

    assert v1.simple_degree() == 3, f"v1 should have 3 hourglasses around it. Instead has{v1.simple_degree()}."
    assert v1.total_degree() == 8, f"v1 should have 8 strands around it. Instead has {v1.total_degree()}."
    assert v4.simple_degree() == 2, f"v4 should have 2 hourglasses implicitly created around it. Instead has {v4.simple_degree()}."
    assert v4.total_degree() == 5, f"v4 should have 5 strands around it. Instead has {v4.total_degree()}."

    assert v4.get_hourglass_to(v2).v_to() == v2, "v4 should be able to find an hourglass to v2."
    assert v1.get_hourglass_to(v3).v_to() == v3, "v1 should be able to find an hourglass to v3."

    v1.clear_hourglasses()
    assert v1.simple_degree() == 0, "v1 should have no hourglasses around it."

    Vertex.create_hourglass_between(v1, v2, 1)
    Vertex.create_hourglass_between(v1, v3, 2)
    Vertex.create_hourglass_between(v1, v4, 5)

    Vertex.remove_hourglass_between(v1, v2)
    Vertex.remove_hourglass_between(v2, v4)

    assert v1.simple_degree() == 2, f"v1 should have 2 hourglasses around it. Instead has {v1.simple_degree()}."
    assert v1.total_degree() == 7, f"v1 should have 7 strands around it. Instead has {v1.total_degree()}."
    assert v2.simple_degree() == 0, f"v2 should have 0 hourglasses around it. Instead has {v2.simple_degree()}."
    assert v2.total_degree() == 0, f"v2 should have 0 strands around it. Instead has {v2.total_degree()}."
    assert v4.simple_degree() == 1, f"v4 should have 1 hourglass around it. Instead has {v4.simple_degree()}."
    assert v4.total_degree() == 5, f"v4 should have 5 strands around it. Instead has {v4.total_degree()}."

    # SQUARE MOVE TESTING

    v5 = Vertex(5, 0, 0, False)
    v6 = Vertex(6, 1, 0, True)
    extras = [Vertex(7, -1, 1, True), Vertex(8, -1, -1, True), Vertex(9, 2, 1, True), Vertex(10, 2, -1, True)]
    mid_hh = Vertex.create_hourglass_between(v5, v6, 2)
    hh1 = Vertex.create_hourglass_between(v5, extras[0], 1)
    hh2 = Vertex.create_hourglass_between(v5, extras[1], 1)
    hh3 = Vertex.create_hourglass_between(v6, extras[2], 1)
    hh4 = Vertex.create_hourglass_between(v6, extras[3], 1)

    v5.square_move_contract(mid_hh)
    assert v6.get_neighbors() == [extras[2], extras[0], extras[1], extras[3]], "v6 should be connected to 7, 8, 9, and 10."
    v5 = v6.square_move_expand(hh1, hh2)
    assert (
        v5.get_neighbors() == [v6, extras[0], extras[1]] and
        v6.get_neighbors() == [extras[2], v5, extras[3]]
    ), "Graph should have returned to previous state."

    v6.square_move_contract(v5._half_hourglasses_head.twin())
    assert v5.get_neighbors() == [extras[2], extras[0], extras[1], extras[3]], "v5 should be connected to 7, 8, 9, and 10."
    v6 = v5.square_move_expand(hh3, hh4)
    assert (
        v5.get_neighbors() == [v6, extras[0], extras[1]] and
        v6.get_neighbors() == [extras[2], v5, extras[3]]
    ), "Graph should have returned to previous state."

    print("Vertex tests complete.\n")

def face_tests():
    print("Testing Face class.")
    # Square move tests
    ID.reset_id()

    v1 = Vertex(1, 0, 0, True)
    v2 = Vertex(2, 1, 0, False)
    v3 = Vertex(3, 1, 1, True)
    v4 = Vertex(4, 0, 1, False)
    extras = [Vertex(5, -1, -1, False), Vertex(6, 2, -1, True), Vertex(7, 2, 1, False), Vertex(8, 1, 2, False), Vertex(9, 0, 2, True), Vertex(10, -1, 1, True), Vertex(11, -2, -1, True), Vertex(12, -1, -2, True), Vertex(13, 2, -2, False), Vertex(14, 3, -1, False)]
    hh1 = Vertex.create_hourglass_between(v1, v2, 1)
    Vertex.create_hourglass_between(v2, v3, 1)
    Vertex.create_hourglass_between(v3, v4, 1)
    Vertex.create_hourglass_between(v4, v1, 1)
    face = Face("face", hh1.twin())
    Vertex.create_hourglass_between(v1, extras[0], 2)
    Vertex.create_hourglass_between(v2, extras[1], 2)
    Vertex.create_hourglass_between(v3, extras[2], 1)
    Vertex.create_hourglass_between(v3, extras[3], 1)
    Vertex.create_hourglass_between(v4, extras[4], 1)
    Vertex.create_hourglass_between(v4, extras[5], 1)
    Vertex.create_hourglass_between(extras[0], extras[6], 1)
    Vertex.create_hourglass_between(extras[0], extras[7], 1)
    Vertex.create_hourglass_between(extras[1], extras[8], 1)
    Vertex.create_hourglass_between(extras[1], extras[9], 1)

    assert [hh.v_from() for hh in face] == [v2, v1, v4, v3], "Face iteration does not work properly."

    assert face.is_square_move_valid(), "Square move should be valid on face."
    rem_add_tuple = face.square_move()
    assert face.is_square_move_valid(), "Square move should be valid on face even after performing square move."
    assert [v.id for v in rem_add_tuple[0]] == ['v16', 'v19'], f"Incorrect vertices marked for addition. Marked vertices are {[v.id for v in rem_add_tuple[0]]}, but should hould be ['v16', 'v19']."
    assert rem_add_tuple[1] == [v2, v1], f"Incorrect vertices marked for removal. Marked vertices are {[v.id for v in rem_add_tuple[0]]} but should be [v2, v1]."
    rem_add_tuple = face.square_move()
    assert face.is_square_move_valid(), "Square move should be valid on face even after performing square move twice."

    v2 = rem_add_tuple[0][0]
    v1 = rem_add_tuple[0][1]

    Vertex.create_hourglass_between(v4, v2, 1)
    assert not face.is_square_move_valid(), "Square move should not be valid on face with 3 edges."
    Vertex.remove_hourglass_between(v4, v2)
    v4.filled = True
    assert not face.is_square_move_valid(), "Square move should not be valid on face with improper vertex fillings."
    v4.filled = False
    v1.get_hourglass_to(v2).thicken()
    assert not face.is_square_move_valid(), "Square move should not be valid on face with improper hourglass multiplicities."

    # Benzene move and cycle tests

    v1 = Vertex(1, 0, 0, True)
    v2 = Vertex(2, 1, 0, False)
    v3 = Vertex(3, 2, 1, True)
    v4 = Vertex(4, 1, 2, False)
    v5 = Vertex(5, 0, 2, True)
    v6 = Vertex(6, -1, 1, False)

    hh1 = Vertex.create_hourglass_between(v2, v1, 1)
    hh2 = Vertex.create_hourglass_between(v3, v2, 2)
    hh3 = Vertex.create_hourglass_between(v4, v3, 1)
    hh4 = Vertex.create_hourglass_between(v5, v4, 2)
    hh5 = Vertex.create_hourglass_between(v6, v5, 1)
    hh6 = Vertex.create_hourglass_between(v1, v6, 2)
    face = Face("face", hh1)

    assert face.is_benzene_move_valid(), "Benzene move should be valid."
    assert face.is_cycle_valid(hh2), "Cycle move should be valid."

    face.benzene_move()
    assert (
        hh1.multiplicity() == 2 and
        hh2.multiplicity() == 1 and
        hh3.multiplicity() == 2 and
        hh4.multiplicity() == 1 and
        hh5.multiplicity() == 2 and
        hh6.multiplicity() == 1
    ), "Hourglass multiplicities are incorrect after first benzene move."
    assert face.is_benzene_move_valid(), "Benzene move should be valid even after performing a benzene move."
    face.benzene_move()
    assert (
        hh1.multiplicity() == 1 and
        hh2.multiplicity() == 2 and
        hh3.multiplicity() == 1 and
        hh4.multiplicity() == 2 and
        hh5.multiplicity() == 1 and
        hh6.multiplicity() == 2
    ), "Hourglass multiplicities are incorrect after second benzene move."

    face.cycle(hh2)
    assert (
        hh1.multiplicity() == 2 and
        hh2.multiplicity() == 1 and
        hh3.multiplicity() == 2 and
        hh4.multiplicity() == 1 and
        hh5.multiplicity() == 2 and
        hh6.multiplicity() == 1
    ), "Hourglass multiplicities are incorrect after first cycle."
    assert face.is_cycle_valid(hh1.twin()), "Cycle move should be valid on hh1 after performing a cycle."
    face.cycle(hh1.twin())
    assert (
        hh1.multiplicity() == 1 and
        hh2.multiplicity() == 2 and
        hh3.multiplicity() == 1 and
        hh4.multiplicity() == 2 and
        hh5.multiplicity() == 1 and
        hh6.multiplicity() == 2
    ), "Hourglass multiplicities are incorrect after second cycle."

    hh2.thin()
    assert not face.is_benzene_move_valid(), "Cannot perform benzene move on hourglass with incorrect multiplicity."
    assert not face.is_cycle_valid(hh2), "Cannot perform cycle move on hourglass with incorrect multiplicity."
    hh2.thicken()
    Vertex.create_hourglass_between(v5, v1, 1)
    assert not face.is_benzene_move_valid(), "Cannot perform benzene move on face with odd number of hourglasses."
    assert not face.is_cycle_valid(hh2), "Cannot perform cycle move on face with odd number of hourglasses."

    print("Face tests complete.\n")

def hourglass_plabic_graph_tests():
    print("Testing HourglassPlabicGraph class.")

    # initialization/construct_boundary

    HPG = HourglassPlabicGraph(10)

    assert len(HPG._boundary_vertices) == 10, f"HPG should have been initialized with 10 boundary vertices. Instead, has {len(HPG._boundary_vertices)}."
    for v in HPG._boundary_vertices.values():
        assert v.boundary, f"Vertex {v.id} is not marked as a boundary vertex."
    assert len(HPG._faces) == 2, f"HPG should have two faces. Instead, has {len(HPG._faces)}."

    ID.reset_id()
    HPG = HourglassPlabicGraph()
    HPG.construct_face(6, [1+(i%2) for i in range(0, 6)])
    assert len(HPG._boundary_vertices) == 6, f"HPG should have been initialized with 6 boundary vertices. Instead, has {len(HPG._boundary_vertices)}."
    assert len(HPG._inner_vertices) == 6, f"HPG should have been initialized with 6 inner vertices. Instead, has {len(HPG._inner_vertices)}."
    assert len(HPG._faces) == 8, f"HPG should have eight faces. Instead, has {len(HPG._faces)}."
    assert str(HPG.get_trip_perms()) == "[[4, 3, 0, 5, 2, 1], [3, 4, 5, 0, 1, 2], [2, 5, 4, 1, 0, 3]]", f"Issue with trip permutations. Should be [[4, 3, 0, 5, 2, 1], [3, 4, 5, 0, 1, 2], [2, 5, 4, 1, 0, 3]], but instead are {HPG.get_trip_perms()}."

    # adding vertices and hourglasses

    HPG = create_test_HPG()

    '''
    print("Checking for proper face initialization.")
    for v in list(HPG._boundary_vertices.values()) + list(HPG._inner_vertices.values()):
        print(str(v.id) + ": " + str([hh.left_face().id for hh in v]))
        #v.print_neighbors()
    HPG.print_faces()
    '''

    # removing vertices and hourglasses

    HPG.remove_vertex_by_id(8)
    HPG.remove_vertex_by_id(5)
    HPG.remove_vertex_by_id(12)

    '''
    print("Testing vertex removal.")
    HPG.print_faces()
    '''

    HPG = create_test_HPG()

    HPG.remove_hourglass_by_id(13, 10)
    HPG.remove_hourglass_by_id(12, 9)
    HPG.remove_hourglass_by_id(8, 1)

    '''
    print("Testing hourglass removal.")
    HPG.print_faces()
    '''

    # Trip tests

    ID.reset_id()
    HPG = create_test_HPG()

    trip_perms1 = HPG.get_trip_perms()
    assert trip_perms1 == [[1, 4, 3, 6, 5, 0, 7, 2], [3, 6, 5, 0, 7, 2, 1, 4], [5, 0, 7, 2, 1, 4, 3, 6]], f"Trip permutations should be [[1, 4, 3, 6, 5, 0, 7, 2], [3, 6, 5, 0, 7, 2, 1, 4], [5, 0, 7, 2, 1, 4, 3, 6]], but instead are {trip_perms1}."
    # Should be the same
    HPG.square_move("face12")
    trip_perms2 = HPG.get_trip_perms()
    assert trip_perms1 == trip_perms2, "Trip permutations should be unchanged after performing a square move."

    # Isomorphism tests

    HPG1 = Examples.GetExample("example_ASM")
    HPG2 = Examples.GetExample("example_ASM")
    HPG3 = Examples.GetExample("example_5_by_2")
    HPG4 = Examples.GetExample("example_5_by_2")
    assert HPG1.is_isomorphic(HPG2), "HPG1 should be isomorphic to HPG2."
    assert HPG3.is_isomorphic(HPG4), "HPG3 should be isomorphic to HPG4."
    assert not HPG1.is_isomorphic(HPG3), "HPG1 should not be isomorphic to HPG3."
    HPG.square_move("face12")
    assert HPG1.is_isomorphic(HPG), "HPG1 should be isomorphic to HPG, even after two square moves."  

    print("HourglassPlabicGraph test complete.\n")

# TESTS FOR EXTENDED HOURGLASS PLABIC GRAPH FUNCTIONALITY

def move_tests():
    print("Testing moves.")
    ID.reset_id()
    plots = []

    HPG = Examples.GetExample("example_ASM")
    face_id = "face2"
    plots.append(("HPG before square move:", HPG.plot()))
    assert HPG.is_square_move_valid(face_id), f"Square move should be valid on {face_id}."

    '''
    print("Checking for proper face initialization.")
    for v in list(HPG._boundary_vertices.values()) + list(HPG._inner_vertices.values()):
        print(f"{v.id}: {[hh.left_face().id for hh in v]}")
    HPG.print_faces()
    '''

    # Square move test
    HPG.square_move(face_id)
    plots.append(("HPG after first square move:", HPG.plot()))
    assert HPG.is_square_move_valid(face_id), f"Square move should be valid on {face_id} after performing square move."

    HPG.square_move(face_id)
    plots.append(("HPG after second square move:", HPG.plot()))
    assert HPG.is_square_move_valid(face_id), f"Square move should be valid on {face_id} after performing second square move."

    # Benzene move test
    assert not HPG.is_benzene_move_valid(face_id), f"Benzene move should not be valid on {face_id}."
    HPG.thicken_hourglass_by_id(9, "v36")
    HPG.thicken_hourglass_by_id(11, "v33")
    plots.append(("HPG after thickening:", HPG.plot()))
    assert HPG.is_benzene_move_valid(face_id), f"Benzene move should be valid on {face_id} after thickening some edges."
    HPG.benzene_move(face_id)
    plots.append(("HPG after benzene move:", HPG.plot()))
    assert HPG._get_hourglass_by_id(9, "v33").multiplicity() == 2, f"Hourglass between 9 and v33 should have multiplicity 2. Instead has multiplicity {HPG._get_hourglass_by_id('9', 'v33').multiplicity()}."
    assert HPG._get_hourglass_by_id("v33", 11).multiplicity() == 1, f"Hourglass between v33 and 11 should have multiplicity 1. Instead has multiplicity {HPG._get_hourglass_by_id('v33', '11').multiplicity()}."
    assert HPG._get_hourglass_by_id(11, "v36").multiplicity() == 2, f"Hourglass between 11 and v36 should have multiplicity 2. Instead has multiplicity {HPG._get_hourglass_by_id('11', 'v36').multiplicity()}."
    assert HPG._get_hourglass_by_id("v36", 9).multiplicity() == 1, f"Hourglass between v36 and 9 should have multiplicity 1. Instead has multiplicity {HPG._get_hourglass_by_id('v36', '9').multiplicity()}."

    # Square move test in SL7
    ID.reset_id()
    HPG = Examples.GetExample("example_2_column_running")
    face_id = "face9"
    plots.append(("HPG before square move in SL7:", HPG.plot()))
    assert HPG.is_square_move_valid(face_id, 7), f"Square move should be valid on {face_id}."

    HPG.square_move(face_id, 7)
    plots.append(("HPG after first square move in SL7:", HPG.plot()))
    assert HPG.is_square_move_valid(face_id, 7), f"Square move should be valid on {face_id} after performing square move."

    HPG.square_move(face_id, 7)
    plots.append(("HPG after second square move in SL7:", HPG.plot()))
    assert HPG.is_square_move_valid(face_id, 7), f"Square move should be valid on {face_id} after performing second square move."

    print("Move tests complete.\n")
    return plots

def serialization_tests():
    print("Testing serialization.")
    HPG = create_test_HPG()
    HPGdict = HPG.to_dict()
    HPGstr = json.dumps(HPGdict, indent=4)
    #print(HPGstr)
    HPG2 = HourglassPlabicGraph.from_dict(HPGdict)
    #HPG2.print_faces()
    print("Serialization tests complete.\n")

def reduced_tests():
    print("Testing is_fully_reduced.")

    verbose = False
    def test_reducedness(name, r, expected):
        if verbose: print(f"Testing {name} for reducedness.")
        if (expected is not None):
            assert Examples.GetExample(name).is_fully_reduced(r, verbose) == expected, f"{name} should{' ' if expected else ' not '}be fully reduced."
            if verbose: print(f"{name} is{' ' if expected else ' not '}fully reduced.")
        else: print(f"{name} is{' ' if Examples.GetExample(name).is_fully_reduced(r, verbose) else ' not '}fully reduced (unkown expectation).")

    # Reduced HPGs
    test_reducedness("example_ASM", 4, True)
    test_reducedness("example_5_by_2", 5, True)
    test_reducedness("example_5_by_3_ASM", 5, True)
    test_reducedness("example_9_by_2", 9, True)
    test_reducedness("example_2_column_running", 7, True)
    test_reducedness("example_2_column_running_after_squaremove", 7, True)
    test_reducedness("example_2_column_running_ear_cut", 7, True)
    test_reducedness("example_benzene", 4, True)
    test_reducedness("example_double_crossing", 4, True)
    test_reducedness("example_6_by_3", 6, True)

    # Non-reduced HPGs
    test_reducedness("example_benzene_full_nonreduced", 4, False)
    test_reducedness("example_5x4_badsep", 5, False)
    test_reducedness("example_6_by_3_bad", 6, False)
    test_reducedness("example_christian_is_working_with", 4, False)
    test_reducedness("examples_christian_plabic", 3, False)

    if verbose:
        # Test unknown examples
        test_reducedness("example_6_by_6", 6, None)
        test_reducedness("examples_ICERM", 5, None)
        # Throws NotImplementedError
        try:
            test_reducedness("example_contractable", 5, None)
            assert False, "example_contractable should have thrown an error."
        except NotImplementedError as nie:
            print(f"Successfully caught NotImplementedError: '{nie}'.")
        except Exception as e:
            assert False, f"Some other error was thrown: '{e}'."

    print("is_fully_reduced tests complete.\n")

def separation_labeling_tests():
    print("Testing separation_labeling.")
    
    def test_labeling(graphdict, name, r, verbose=False):
        if verbose: print(f"Testing separation labeling on {name}.")
        ID.reset_id()
        HPG = HourglassPlabicGraph.from_dict(graphdict)
        HPGOld = HourglassPlabicGraphOld.from_dict(graphdict)
        # Test separation labeling for every face
        for face in HPG._faces.values():
            # Skip the boundary face
            is_complete_boundary = True
            for hh in face:
                if not hh.is_boundary(): 
                    is_complete_boundary = False
                    break
            if is_complete_boundary: continue
            # We find corresponding face in the old graph
            # IDs for vertices are shared as they are defined in the dictionary, thus they can be used as identifiers
            oface = None
            vertex_ids = set([hh.v_from().id for hh in face])
            for f in HPGOld.faces.values(): 
                if vertex_ids == set([v.id for v in f.vertices()]):
                    oface = f
                    break
            assert oface is not None, f"Unable to find corresponding face for {face.id}."
            if verbose: print("-Performing New Separation Labeling-")
            HPG.separation_labeling(face, r, verbose)
            if verbose: print("-Performing Legacy Separation Labeling-")
            HPGOld.separation_labeling(oface, r)

            # Compare all labels
            # Remember, labels are applied to halfhourglasses rooted at white (unfilled)
            for oh in HPGOld.hourglasses.values():
                hh = None
                if oh.v_from.filled: hh = HPG._get_hourglass_by_id(oh.v_to.id, oh.v_from.id)
                else: hh = HPG._get_hourglass_by_id(oh.v_from.id, oh.v_to.id)
                assert hh is not None, f"Unable to find hourglass between vertices {oh.v_from.id} and {oh.v_to.id}."
                # Note that we assume label is in ascending order, which is not necessarily true of legacy code
                assert sorted(oh.label) == hh.label, f"Labels do not agree on hourglass between vertices {hh.v_from().id} to {hh.v_to().id}. New label: {hh.label} Old label: {sorted(oh.label)}."
            if verbose: print(f"Separation labeling passed on {name}.")

    test_labeling(Examples.example_ASM, "example_ASM", 4)
    test_labeling(Examples.example_5_by_2, "example_5_by_2", 5)
    test_labeling(Examples.example_5_by_3_ASM, "example_5_by_3_ASM", 5)
    test_labeling(Examples.example_9_by_2, "example_9_by_2", 9)
    test_labeling(Examples.example_2_column_running, "example_2_column_running", 7)
    test_labeling(Examples.example_2_column_running_after_squaremove, "example_2_column_running_after_squaremove", 7)
    test_labeling(Examples.example_2_column_running_ear_cut, "example_2_column_running_ear_cut", 7)
    test_labeling(Examples.example_benzene, "example_benzene", 4)
    test_labeling(Examples.example_double_crossing, "example_double_crossing", 4)
    test_labeling(Examples.example_6_by_3, "example_6_by_3", 6)

    print("separation_labeling tests complete.\n")

def create_test_HPG():
    '''
    Creates the following graph with the labeled IDs:
    '''
#           7----0
#         / |    | \
#        /  |    |  \
#       6---11   8---1
#       |   | \  ()  |
#       |   |  \ ()  |
#       |   |    12  |
#       |   13   |   |
#       |   ()\  |   |
#       |   () \ |   |
#       5---10   9---2
#        \  |    |  /
#         \ |    | /
#           4----3
    '''
    Note that the boundary, 12, and 13 are filled,
    while 8, 9, 10, and 11 are unfilled.
    '''
    HPG = HourglassPlabicGraph(8)
    HPG.create_vertex(8,  5,  5, False )
    HPG.create_vertex(9,  5, -5, False)
    HPG.create_vertex(10, -5, -5, False )
    HPG.create_vertex(11, -5,  5, False)
    HPG.create_vertex(12, 2,  2, True)
    HPG.create_vertex(13, -2,  -2, True)
    HPG.create_hourglass_by_id(8, 12, 2)
    HPG.create_hourglass_by_id(10, 13, 2)
    HPG.create_hourglass_by_id(9, 12)
    HPG.create_hourglass_by_id(9, 13)
    HPG.create_hourglass_by_id(11, 12)
    HPG.create_hourglass_by_id(11, 13)
    HPG.create_hourglass_by_id(8, 0)
    HPG.create_hourglass_by_id(8, 1)
    HPG.create_hourglass_by_id(9, 2)
    HPG.create_hourglass_by_id(9, 3)
    HPG.create_hourglass_by_id(10, 4)
    HPG.create_hourglass_by_id(10, 5)
    HPG.create_hourglass_by_id(11, 6)
    HPG.create_hourglass_by_id(11, 7)
    return HPG
