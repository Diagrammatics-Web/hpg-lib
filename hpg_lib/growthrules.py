r"""
Routines for dealing with growth rules.

AUTHORS:

- Joshua P. Swanson (2025-12-11): initial version

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

from itertools import chain
from random import random
from .hourglassplabicgraph import HourglassPlabicGraph
from .prom import to_lattice_word

def occurrences(big, small):
    '''Consecutive occurrences.'''
    for i in range(len(big)-len(small)+1):
        for j in range(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            yield i

def create_local_move(X, Y, s):
    '''Returns a function which takes a list L and replaces every occurrence
       of X as a consecutive sublist with Y, returning an iterator of all such results as lists.
       Returns (Xp, i, s) where Xp is the replacement, the index i of the beginning of the
       occurence of Y in X, and s is the given type.'''
    def local_move(L):
        for i in occurrences(L, X):
            yield list(chain(L[:i], Y, L[i+len(X):])), i, s
    return local_move

_nonelliptic_rule_specs = (([1, 2], [-3], "Y"),
                           ([1, 3], [-2], "Y"),
                           ([2, 3], [-1], "Y"),
                           ([-2, -1], [3], "Y"),
                           ([-3, -1], [2], "Y"),
                           ([-3, -2], [1], "Y"),
                           ([2, -2], [-1, 1], "H"),
                           ([2, -1], [-1, 2], "H"),
                           ([1, -2], [-2, 1], "H"),
                           ([-2, 2], [3, -3], "H"),
                           ([-3, 2], [-2, 3], "H"),
                           ([1, -1], [], "cup"),
                           ([-3, 3], [], "cup"))

_nonelliptic_local_moves = [create_local_move(X, Y, s) for X, Y, s in _nonelliptic_rule_specs]

def get_nonelliptic_web(T):
    '''Takes in a 3-row rectangular standard Young tableau T.
       Outputs Kuperberg's corresponding non-elliptic basis web as
       an HourglassPlabicGraph. Implemented using the Khovanov--Kuperberg growth rules.'''
    L = to_lattice_word(T)
    n = len(L)

    G = HourglassPlabicGraph(n)
    danglers = G.sorted_boundary_vertices()
    base_hhs = []
    for i in range(n):
        v = danglers[i]
        hhs = list(v)
        base = hhs[0] if hhs[0].v_to() == danglers[(i-1)%n] else hhs[1]
        base_hhs.append(base)

    while True:
        for Lp, i, s in chain(*(move(L) for move in _nonelliptic_local_moves)):
            v1 = danglers[i]
            v2 = danglers[i+1]

            if s=="Y":
                v_new = G.create_vertex(random(), random(), False if Lp[i]<0 else True)
                hh1 = G.create_hourglass(v1, v_new, 1, base_hhs[i], None)
                hh2 = G.create_hourglass(v2, v_new, 1, hh1, None)
                danglers[i] = v_new
                base_hhs[i] = hh1
                del danglers[i+1]
                del base_hhs[i+1]
                
            elif s=="H":
                v1_new = G.create_vertex(random(), random(), False if Lp[i]<0 else True)
                v2_new = G.create_vertex(random(), random(), False if Lp[i+1]<0 else True)
                hh1 = G.create_hourglass(v1, v1_new, 1, base_hhs[i], None)
                hh2 = G.create_hourglass(v2, v2_new, 1, base_hhs[i+1], None)
                hhx = G.create_hourglass(v1_new, v2_new, 1, None, None)
                danglers[i] = v1_new
                danglers[i+1] = v2_new
                base_hhs[i] = hh1
                base_hhs[i+1] = hhx
            
            elif s=="cup":
                G.create_hourglass(v1, v2, 1, base_hhs[i], base_hhs[i+1])
                del danglers[i:i+2]
                del base_hhs[i:i+2]
                
            print(Lp, i, s)
            
            L = Lp
            break
        else:
            break
    G.make_circular()
    return G
