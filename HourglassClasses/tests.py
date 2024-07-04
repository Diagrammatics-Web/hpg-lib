from .dihedralelement import DihedralElement
from .halfstrand import HalfStrand
from .halfhourglass import HalfHourglass
from .vertex import Vertex
from .face import Face
from .hourglassplabicgraph import HourglassPlabicGraph
import math

# Mock classes for testing lower level classes

class _TestHalfHourglass:
    def twin(self):
        return self

class _TestVertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Begin tests

def all_tests():
    # dihedral_element_tests()
    half_strand_tests()
    half_hourglass_tests()
    vertex_tests()
    face_tests()
    hourglass_plabic_graph_tests()

def dihedral_element_tests():
    print("Testing DihedralElement class.")

    d1 = DihedralElement(1)
    d2 = DihedralElement(2)
    d3 = DihedralElement(3)

    assert d1.get_num_elements() == 1, "d1 should form a 1 element list."

    d1.insert_cw_next(d2)
    d2.insert_ccw_next(d3)
    # list order should now be d1, d3, d2
    assert d1.get_num_elements() == 3, "All 3 elements should be in list."
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
        [element.id for element in d2.iterate_counterlockwise()] == [2, 3, 1]
    ), "Iterator does not work."

    assert d1.get_cw_ith_element(4) == d3, "get_cw_ith_element is broken."
    assert d1.get_ccw_ith_element(7) == d2, "get_ccw_ith_element is broken."

    d3.remove()
    assert d1.get_num_elements() == 2, "d3 should have been removed correctly."
    d2.remove()
    assert d1.get_num_elements() == 1, "d2 should have been removed correctly."
    
    print("DihedralElement tests complete.")

def half_strand_tests():
    print("Testing HalfStrand class.")

    hh1 = _TestHalfHourglass()
    hh2 = _TestHalfHourglass()
    
    s1 = HalfStrand(1, hh1)
    assert s1.twin() != None, "s1 should have created a twin."
    assert s1.twin().twin() == s1, "s1's twin's twin should be s1."
    
    assert s1.get_last_strand_same_hourglass() == s1, "s1 is not linked to itself properly when alone."
    assert s1.get_num_strands_same_hourglass() == 1, "s1 not counting number of strands properly when alone."

    s2 = HalfStrand(2, hh1)
    s3 = HalfStrand(3, hh1)
    s1.insert_cw_next(s2)
    s2.insert_cw_next(s3)
    assert s1.get_last_strand_same_hourglass() == s3, "s1 is not linked to other strands properly when strands are all from same hourglass."
    assert s1.get_num_strands_same_hourglass() == 3, "s1 not counting number of strands properly when strands are all from same hourglass."

    s4 = HalfStrand(4, hh2)
    s1.insert_ccw_next(s4)
    assert s4.get_last_strand_same_hourglass() == s4, "s4 is not linked to other strands properly when alone with another hourglass."
    assert s4.get_num_strands_same_hourglass() == 1, "s4 not counting number of strands properly when alone with another hourglass."

    s5 = HalfStrand(5, hh2)
    s4.insert_cw_next(s5)
    assert s4.get_last_strand_same_hourglass() == s5, "s4 is not linked to other strands properly when multiple hourglasses."
    assert s4.get_num_strands_same_hourglass() == 2, "s4 not counting number of strands properly when multiple hourglasses."    

    print("HalfStrand tests complete.")

def half_hourglass_tests():
    print("Testing HalfHourglass class.")

    v1 = _TestVertex(0, 0)
    v2 = _TestVertex(1, 1)
    hh = HalfHourglass(1, v1, v2, 1)
    assert hh.twin() != None, "hh should have created a twin."
    assert hh.twin().twin() == hh, "hh's twin's twin should be hh."
    assert hh.v_to() == hh.twin().v_from() and hh.v_from() == hh.twin().v_to(), "hh and twin should have swapped vertices."
    assert hh.get_angle() == math.pi/4, "hh angle should be pi/4 (45 degrees). instead, it is " + str(hh.get_angle())

    hh.thicken()
    hh.thicken()
    hh.thicken()
    assert hh.strand_count() == 4, "hh should have 4 strands. strand_count: " + str(hh.strand_count())
    hh.thin()
    hh.thin()
    assert hh.strand_count() == 2, "hh should have 2 strands. strand_count: " + str(hh.strand_count())
    
    hhp = HalfHourglass(2, v1, v2, 0)
    assert hhp.is_phantom() and hhp.strand_count() == 0, "hhp should be a phantom (boundary) edge."

    hh3 = HalfHourglass(3, v1, v2, 5)
    hh4 = HalfHourglass(4, v1, v2, 2)

    hh.insert_cw_next(hhp)
    hhp.insert_cw_next(hh3)
    hh.insert_ccw_next(hh4)

    # list order should now be hh, hhp, hh3, hh4
    assert (
        hh.strand_count() == 2 and 
        hhp.strand_count() == 0 and 
        hh3.strand_count() == 5 and 
        hh4.strand_count() == 2
    ), "Strands were not linked properly between hourglasses during insertions."
    assert hh._half_strands_head.get_num_elements() == 2 + 5 + 2, "Strands were not linked properly all the way around during insertions."

    hhp.remove()
    hh3.remove()
    # list order should now be hh, hh4
    assert hh.strand_count() == 2 and hh4.strand_count() == 2, "Strands were not linked properly between hourglasses during removals."
    assert hh._half_strands_head.get_num_elements() == 2 + 2, "Strands were not linked properly all the way around during removals."

    #TODO: test is_left_face_valid
    
    print("HalfHourglass tests complete.")

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

    assert v1.simple_degree() == 3, "v1 should have 3 hourglasses around it. Instead has " + str(v1.simple_degree())
    assert v1.total_degree() == 8, "v1 should have 8 strands around it. Instead has " + str(v1.total_degree())
    assert v4.simple_degree() == 2, "v4 should have 2 hourglasses implicitly created around it. Instead has " + str(v4.simple_degree())
    assert v4.total_degree() == 5, "v4 should have 5 strands around it. Instead has " + str(v4.total_degree())

    assert v4.get_hourglass_to(v2).v_to() == v2, "v4 should be able to find an hourglass to v2."
    assert v1.get_hourglass_to(v3).v_to() == v3, "v1 should be able to find an hourglass to v3."
    
    v1.clear_hourglasses()
    assert v1.simple_degree() == 0, "v1 should have no hourglasses around it."
    
    Vertex.create_hourglass_between(v1, v2, 1)
    Vertex.create_hourglass_between(v1, v3, 2)
    Vertex.create_hourglass_between(v1, v4, 5)
    
    Vertex.remove_hourglass_between(v1, v2)
    Vertex.remove_hourglass_between(v2, v4)

    assert v1.simple_degree() == 2, "v1 should have 2 hourglasses around it. Instead has " + str(v1.simple_degree())
    assert v1.total_degree() == 7, "v1 should have 7 strands around it. Instead has " + str(v1.total_degree())
    assert v4.simple_degree() == 1, "v4 should have 1 hourglass around it. Instead has " + str(v4.simple_degree())
    assert v4.total_degree() == 5, "v4 should have 5 strands around it. Instead has " + str(v4.total_degree())
    assert v2.simple_degree() == 0, "v2 should have 0 hourglasses around it. Instead has " + str(v2.simple_degree())
    assert v2.total_degree() == 0, "v2 should have 0 strands around it. Instead has " + str(v2.total_degree())

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
    
    print("Vertex tests complete.")

def face_tests():
    print("Testing Face class.")
    # Square move tests
    
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
    assert [v.id for v in rem_add_tuple[0]] == ['v_4', 'v_3'], "Incorrect vertices marked for addition."
    assert rem_add_tuple[1] == [v2, v1], "Incorrect vertices marked for removal."
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

    # Benzene move tests

    v1 = Vertex(1, 0, 0, True)
    v2 = Vertex(2, 1, 0, False)
    v3 = Vertex(3, 3, 1, True)
    v4 = Vertex(4, 2, 2, False)
    v5 = Vertex(5, 1, 2, True)
    v6 = Vertex(6, -1, 1, False)

    hh1 = Vertex.create_hourglass_between(v1, v2, 1)
    hh2 = Vertex.create_hourglass_between(v2, v3, 2)
    hh3 = Vertex.create_hourglass_between(v3, v4, 1)
    hh4 = Vertex.create_hourglass_between(v4, v5, 2)
    hh5 = Vertex.create_hourglass_between(v5, v6, 1)
    hh6 = Vertex.create_hourglass_between(v6, v1, 2)
    face = Face("face", hh1.twin())

    assert face.is_benzene_move_valid(), "Benzene move should be valid."
    face.benzene_move()
    assert (
        hh1.multiplicity() == 2 and
        hh2.multiplicity() == 1 and
        hh3.multiplicity() == 2 and
        hh4.multiplicity() == 1 and
        hh5.multiplicity() == 2 and
        hh6.multiplicity() == 1
    ), "Hourglass multiplicities are incorrect."
    assert face.is_benzene_move_valid(), "Benzene move should be valid even after performing a benzene move."
    face.benzene_move()
    assert (
        hh1.multiplicity() == 1 and
        hh2.multiplicity() == 2 and
        hh3.multiplicity() == 1 and
        hh4.multiplicity() == 2 and
        hh5.multiplicity() == 1 and
        hh6.multiplicity() == 2
    ), "Hourglass multiplicities are incorrect."

    hh1.thicken()
    assert not face.is_benzene_move_valid(), "Cannot perform benzene move on hourglass with incorrect multiplicity."
    hh1.thin()
    Vertex.create_hourglass_between(v5, v1, 1)
    assert not face.is_benzene_move_valid(), "Cannot perform benzene move on face with odd number of hourglasses."
    
    print("Face tests complete.")

def hourglass_plabic_graph_tests():
    print("Testing HourglassPlabicGraph class.")

    # initialization/create_boundary
    
    HPG = HourglassPlabicGraph(10)

    assert len(HPG._boundary_vertices) == 10, "HPG should have been initialized with 10 boundary vertices."
    for v in HPG._boundary_vertices.values():
        assert v.boundary, "Vertex " + str(v.id) + " is not marked as a boundary vertex."
    assert len(HPG._faces) == 2, "HPG should have two faces."

    # adding vertices and hourglasses

    HPG = HourglassPlabicGraph(8)
    HPG.create_vertex("v1",  5,  5, True )
    HPG.create_vertex("v2",  5, -5, False)
    HPG.create_vertex("v3", -5, -5, True )
    HPG.create_vertex("v4", -5,  5, False)
    HPG.create_hourglass("v1", "v2", 2)
    HPG.create_hourglass("v2", "v3", 2)
    HPG.create_hourglass("v3", "v4", 2)
    HPG.create_hourglass("v4", "v1", 2)
    HPG.create_hourglass("v1", "0", 1)
    HPG.create_hourglass("v1", "1", 1)
    HPG.create_hourglass("v2", "2", 1)
    HPG.create_hourglass("v2", "3", 1)
    HPG.create_hourglass("v3", "4", 1)
    HPG.create_hourglass("v3", "5", 1)
    HPG.create_hourglass("v4", "6", 1)
    HPG.create_hourglass("v4", "7", 1)

    '''
    for v in list(HPG._boundary_vertices.values()) + list(HPG._inner_vertices.values()):
        print(v.id + ":")
        v.print_neighbors()
    '''

    for f in HPG._faces.values():
        print(f.id + ":")
        f.print_vertices()
    
    # removing vertices and hourglasses

    print("HourglassPlabicGraph test not yet complete.")

def trip_tests():
    print("Testing trips.")
    HPG = create_test_HPG()
    print(HPG.get_trip_perms())
    print("TODO")

def create_test_HPG():
    '''Creates the graph seen at https://youtu.be/wsltX4aTjbc?t=2565'''
    # TODO