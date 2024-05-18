from .halfhourglass import HalfHourglass
from .vertex import Vertex
from .hourglassplabicgraph import HourglassPlabicGraph
import math

class _TestVertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def halfhourglass_tests():
    print("Testing HalfHourglass class.")

    v1 = _TestVertex(0, 0)
    v2 = _TestVertex(1, 1)
    hh = HalfHourglass(1, v1, v2, 1)
    assert hh.twin != None, "hh should have created a twin"
    assert hh.twin.twin == hh, "hh twin's twin should be hh"
    assert hh.v_to == hh.twin.v_from and hh.v_from == hh.twin.v_to, "hh and twin should have swapped vertices"
    assert hh.get_angle() == math.pi/4, "hh angle should be pi/4 (45 degrees). instead, it is " + str(hh.get_angle())

    hh.thicken()
    hh.thin()
    hh.thin()
    assert hh.strand_count == 1, "hh should not go below 1 strand. strand_count: " + str(hh.strand_count)
    
    hhp = HalfHourglass(2, None, None, 0)
    assert hhp.is_phantom(), "hhp should be a phantom (boundary) edge"
    
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

    assert v1.simple_degree() == 3, "v1 should have 3 hourglasses around it"
    assert v1.total_degree() == 8, "v1 should have 8 strands around it"
    assert v4.simple_degree() == 2, "v4 should have 2 hourglasses implicitly created around it"
    assert v4.total_degree() == 5, "v4 should have 5 strands around it"

    print("Vertex tests complete.")

def trip_tests():
    print("Testing trips.")
    HPG = create_test_HPG()
    print(HPG.get_trip_perms())

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
    

    