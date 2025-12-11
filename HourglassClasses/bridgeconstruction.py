r"""
Contains routines for finding hourglass plabic graphs with prescribed trips.

AUTHORS:

- Joshua P. Swanson (2025-12-04): initial version

"""

# ****************************************************************************
#       Copyright (C) 2025 Joshua P. Swanson <jpswanson3.14@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from .hourglassplabicgraph import HourglassPlabicGraph
from sage.combinat.permutation import Permutation

def _bridge_decomp(p, verbose=False):
    '''Takes a fixed-point free permutation as a list consisting of the numbers 1, ..., n.
       Returns a list of transpositions which encode the BCFW-bridge decomposition of p as
       described in [Williams GrassPerm.pdf, Def. 2.18].
       '''
    p = list(p)
    n = len(p)

    # Highlight co-excedances
    highlight = [0 if p[i]-1 > i else 1 for i in range(n)]

    # Initialized frozen data
    frozen = [0]*n # no fixed points
    n_frozen = 0

    # The unhighlighted entries of p will always be left of their sorted position.
    # The highlighted entries will always be right of their sorted position.
    # If we repeatedly transpose the largest unfrozen highlighted entry to get
    #   it to drift left to its sorted position, we'll arrive at the identity.
    ts = []
    while n_frozen < n:
        if verbose:
            print("p =", p)
            print("frozens: ", frozen)
            print("highlighted: ", highlight)

        # Get index of largest unfrozen highlighted entry
        unfrozen_i = [i for i in range(n) if frozen[i] == 0]
        h_max = max(p[i] for i in unfrozen_i if highlight[i] == 1)
        h_max_i = [i for i in range(n) if p[i] == h_max][0]

        # Drift left
        drift_int = [i for i in unfrozen_i if h_max-1 <= i <= h_max_i]
        for j in reversed(range(len(drift_int)-1)):
            a = drift_int[j]
            b = drift_int[j+1]
            ts.append((a+1,b+1))
            if verbose:
                print("...applying", ts[-1])
            frozen[a],frozen[b] = frozen[b],frozen[a]
            highlight[a],highlight[b] = highlight[b],highlight[a]
            p[a],p[b] = p[b],p[a]
            if p[a]-1 == a:
                frozen[a] = 1
                n_frozen += 1
            if p[b]-1 == b:
                frozen[b] = 1
                n_frozen += 1

    if verbose:
        print("p =", p)
        print("frozens: ", frozen)
        print("highlighted: ", highlight)
    return ts

class BridgeVertex:
    max_id = -1

    def __init__(self, x, y, is_filled, is_boundary = False):
        BridgeVertex.max_id += 1
        self.id = BridgeVertex.max_id
        self.x = x
        self.y = y
        self.is_filled = is_filled
        self.is_boundary = is_boundary

    def __repr__(self):
        return str(self.id)

def bridge_construction(w, boundary_type=None):
    '''Takes a permutation w as a list consisting of the numbers 1, ..., n
       and without fixed points. Returns an HourglassPlabicGraph consisting
       of the result of the BCFW bridge construction as described in
       [Williams GrassPerm.pdf, Def. 2.18].
       
       If boundary_type is None, makes all boundary vertices black.
       Otherwise, boundary_type is a list [c1, ..., cn] where
       ci=1 means black, ci=-1 means white for the ith boundary vertex.'''
    BridgeVertex.max_id = -1
    ts = _bridge_decomp(w)

    if boundary_type is None:
        boundary_type = [1]*len(list(w))
    points = [[BridgeVertex(i, 0, boundary_type[i]>0, True)] for i in range(len(w))]
    edges = []
    def add_vertex(bv):
        last_in_column = points[bv.x][-1]
        if last_in_column.is_filled == bv.is_filled:
            add_vertex(BridgeVertex(bv.x, (bv.y+last_in_column.y)/2, not bv.is_filled))
            add_vertex(bv)
        else:
            points[bv.x].append(bv)
            edges.append((last_in_column, bv))


    for i,t in enumerate(ts, 1):
        y = -i
        x1, x2 = [x-1 for x in t]
        left = BridgeVertex(x1, y, False)
        right = BridgeVertex(x2, y, True)
        add_vertex(left)
        add_vertex(right)
        edges.append((left, right))

    all_points = sum(points, [])

    dct = dict()
    dct['edges'] = [{'multiplicity': 1, 'sourceId': left.id, 'targetId': right.id} for left, right in edges]
    dct['vertices'] = [{'id': bv.id,
                          'x': bv.x,
                          'y': bv.y,
                     'filled': bv.is_filled,
                   'boundary': bv.is_boundary} for bv in all_points]
    dct['layout'] = 'linear'

    G = HourglassPlabicGraph.from_dict(dct)
    G.contract_all()
    return G

def prom_perm(T, k):
    '''Computes the promotion permutation of a rectangular standard Young tableau T with shape b^a as
       defined by [HR] and [GPPSS].

       To compute it, do inverse promotion, without decrementing, ab times
       (i.e. remove 1 which is in the upper left corner, rectify, make lower right entry one
       more than the previous maximum). At each step, record which entry slides into the kth row,
       with the top row being the 1st row. Those entries form a permutation of ab when they're taken
       modulo ab.

       sage: T = StandardTableau([[1, 4, 6, 9, 10, 13, 19, 20, 28, 29], [2, 7, 8, 12, 17, 18, 23, 25, 31,

 33], [3, 11, 14, 15, 21, 22, 27, 32, 34, 36], [5, 16, 24, 26, 30, 35, 37, 38, 39, 40]])

       sage: prom_perm(T, 1).cycle_string()
       (1,2,3,8,17,25,26,9,12,15,16,10,11,40,4,5)(6,7,18,23,24,13,14,39)(19,22,27,33,34,35,29,30,20,21,36,37,28,31,32,38)

       sage: prom_perm(T, 2).cycle_string()
       (1,3)(2,5)(4,15)(6,11)(7,40)(8,39)(9,22)(10,14)(12,21)(13,16)(17,36)(18,27)(19,26)(20,24)(23,38)(25,30)(28,34)(29,32)(31,37)(33,35)

       sage: prom_perm(T, 3).cycle_string()
       (1,5,4,40,11,10,16,15,12,9,26,25,17,8,3,2)(6,39,14,13,24,23,18,7)(19,38,32,31,28,37,36,21,20,30,29,35,34,33,27,22)

       sage: prom_perm(T, 4).cycle_string()
       ()'''
    n = sum(T.shape())

    ret = []
    for i in range(n):
        T_next = T.promotion_inverse()
        p = T[k-1]
        q = tuple(_+1 for _ in T_next[k-1])
        for j in reversed(range(len(p))):
            if p[j] != q[j]:
                ret.append((q[j]+i) % n)
                break
        T = T_next
    return Permutation([i if i != 0 else n for i in ret])

def get_nonelliptic_web(T):
    '''Constructs Kuperberg's non-elliptic sl(3) web associated with the input
       3-row rectangular standard Young tableau T, as an HourglassPlabicGraph.'''
    G = bridge_construction(prom_perm(T, 1))
    G.make_circular()
    return G
