from .dihedralelement import DihedralElement
from .halfstrand import HalfStrand
from .halfhourglass import HalfHourglass
from .vertex import Vertex
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

    print("Awaiting further tests.")

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
    ),   "List order is incorrect or list is broken."

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

    v1.create_hourglass_between(v2, 1)
    v1.create_hourglass_between(v3, 2)
    v1.create_hourglass_between(v4, 5)
    v2.create_hourglass_between(v4, 0)

    assert v1.simple_degree() == 3, "v1 should have 3 hourglasses around it."
    assert v1.total_degree() == 8, "v1 should have 8 strands around it."
    assert v4.simple_degree() == 2, "v4 should have 2 hourglasses implicitly created around it."
    assert v4.total_degree() == 5, "v4 should have 5 strands around it."

    assert v4.get_hourglass_to(v2).v_to() == v2, "v4 should be able to find an hourglass to v2."
    assert v1.get_hourglass_to(v3).v_to() == v3, "v1 should be able to find an hourglass to v3."
    v1.clear_hourglasses()
    assert v1.simple_degree() == 0, "v1 should have no hourglasses around it."

    print("Vertex tests complete.")

def trip_tests():
    print("Testing trips.")
    HPG = create_test_HPG()
    print(HPG.get_trip_perms())
    print("TODO")

def create_test_HPG():
    '''Creates the graph seen at https://youtu.be/wsltX4aTjbc?t=2565'''
    inner_vertices = []
    boundary_vertices = []

    boundary_vertices.append(Vertex(id=1, x=1, y=1, filled=True, boundary=True))
    boundary_vertices.append(Vertex(id=2, x=1, y=0, filled=False, boundary=True))
    boundary_vertices.append(Vertex(id=3, x=1, y=-1, filled=True, boundary=True))
    boundary_vertices.append(Vertex(id=4, x=0, y=-1, filled=True, boundary=True))
    boundary_vertices.append(Vertex(id=5, x=-1, y=-1, filled=False, boundary=True))
    boundary_vertices.append(Vertex(id=6, x=-1, y=0, filled=True, boundary=True))
    boundary_vertices.append(Vertex(id=7, x=-1, y=1, filled=False, boundary=True))

    inner_vertices.append(Vertex(id=11, x=.5, y=.5, filled=False))
    inner_vertices.append(Vertex(id=12, x=.5, y=0, filled=True))
    inner_vertices.append(Vertex(id=13, x=.5, y=-.5, filled=False))
    inner_vertices.append(Vertex(id=14, x=0, y=-.5, filled=False))
    inner_vertices.append(Vertex(id=15, x=-.5, y=-.5, filled=True))
    inner_vertices.append(Vertex(id=16, x=-.5, y=0, filled=False))
    inner_vertices.append(Vertex(id=17, x=-.5, y=.5, filled=True))

    boundary_vertices[0].create_hourglass_between(boundary_vertices[1], 0)
    boundary_vertices[1].create_hourglass_between(boundary_vertices[2], 0)
    boundary_vertices[2].create_hourglass_between(boundary_vertices[3], 0)
    boundary_vertices[3].create_hourglass_between(boundary_vertices[4], 0)
    boundary_vertices[4].create_hourglass_between(boundary_vertices[5], 0)
    boundary_vertices[5].create_hourglass_between(boundary_vertices[6], 0)
    boundary_vertices[6].create_hourglass_between(boundary_vertices[0], 0)
    
    boundary_vertices[0].create_hourglass_between(inner_vertices[0], 2)
    boundary_vertices[1].create_hourglass_between(inner_vertices[1], 1)
    boundary_vertices[2].create_hourglass_between(inner_vertices[2], 2)
    boundary_vertices[3].create_hourglass_between(inner_vertices[3], 1)
    boundary_vertices[4].create_hourglass_between(inner_vertices[4], 2)
    boundary_vertices[5].create_hourglass_between(inner_vertices[5], 2)
    boundary_vertices[6].create_hourglass_between(inner_vertices[6], 1)

    inner_vertices[0].create_hourglass_between(inner_vertices[1], 1)
    inner_vertices[1].create_hourglass_between(inner_vertices[2], 1)
    inner_vertices[3].create_hourglass_between(inner_vertices[4], 1)
    inner_vertices[4].create_hourglass_between(inner_vertices[5], 1)
    inner_vertices[5].create_hourglass_between(inner_vertices[6], 1)
    inner_vertices[6].create_hourglass_between(inner_vertices[0], 1)

    inner_vertices[1].create_hourglass_between(inner_vertices[3], 1)
    inner_vertices[3].create_hourglass_between(inner_vertices[6], 1)

    HPG = HourglassPlabicGraph()
    HPG.boundary_vertices = boundary_vertices
    HPG.inner_vertices = inner_vertices

    return HPG
    

    