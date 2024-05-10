import math
from copy import deepcopy
from collections import defaultdict
import itertools
from sage.all import Graph
from sage.all import RecursivelyEnumeratedSet
from sage.all import VoronoiDiagram
from sage.all import multinomial

class HalfHourglass:
    '''Represents part of an edge from one vertex to another in an hourglass plabic graph.'''
    def __init__(self, id, v_from, v_to, strand_count, label='', twin=None):
        '''id: an object, assumed unique, should be hashable
           strand_count: number of strands between from and to. if 0, this is an edge boundary
           label: an object
        '''
        self.id = id
        self.v_from = v_from
        self.v_to = v_to
        self.strand_count = strand_count
        self.label = label

        # set up twin with swapped to/from vertices
        if (twin == None):
            twin = HalfHourglass("id", v_to, v_from, strand_count, '', self)
        else: self.twin = twin
            
        self.cw_next = self
        self.ccw_next = self

    def add_strand(self):
        strand_count++
        twin.strand_count++

    def remove_strand(self):
        # hourglass must have 
        if (strand_count > 1): 
            strand_count--
            twin.strand_count--

    def is_phantom(self):
        return strand_count == 0

    def get_angle(self):
        ''' returns the angle between the vector from v_from to v_to and the x-axis.
        returns value between 0 and 2pi.'''
        angle = math.atan2(self.v_to.y-self.v_from.y, self.v_to.x-self.v_from.x)
        if angle < 0:
            angle += 2 * math.pi
        return angle