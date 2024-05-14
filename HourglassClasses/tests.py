from halfhourglass import HalfHourglass
from vertex import Vertex

class TestVertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def halfhourglass_tests():
    print("Testing HalfHourglass class.")

    v1 = TestVertex(0, 0)
    v2 = TestVertex(1, 1)

    hh = HalfHourglass(1, v1, v2, 1)
    
    assert hh.twin != None, "hh should have created a twin"
    assert hh.twin.twin == hh, "hh twin's twin should be hh"
    assert hh.v_to == hh.twin.v_from and hh.v_from == hh.twin.v_to, "hh and twin should have swapped vertices"
    assert hh.get_angle() == math.pi/2, "hh angle should be pi/2 (45 degrees)"
    
    
    hhp = HH.HalfHourglass(2, None, None, 0)

def vertex_tests():
    print("Testing Vertex class.")

    v1 = V.Vertex(1, 0, 0, True)
    v2 = V.Vertex(2, 0, 0, False)
    v3 = V.Vertex(3, 0, 0, True)
    v4 = V.Vertex(4, 0, 0, False)

    