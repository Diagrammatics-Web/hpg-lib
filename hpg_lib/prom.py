r"""
Promotion permutations and other tableaux-related routines.

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

def to_lattice_word(T):
    '''Takes a standard tableau T and turns it into a lattice word, namely a list of the rows of
       1, 2, 3, ...'''
    L = list(T)
    r = len(L)
    starts = [0]*r
    ret = []
    for i in range(1, sum(len(_) for _ in T)+1):
        for j in range(r):
            if starts[j] < len(L[j]):
                if L[j][starts[j]] == i:
                    # Found i
                    ret.append(j+1)
                    starts[j] += 1
                    break
    return ret

def from_lattice_word(L):
    '''Takes a lattice word L and turns it into a standard tableau.'''
    T = [[] for _ in range(max(L))]
    for i,v in enumerate(L):
        T[v-1].append(i+1)
    return StandardTableau(T)

def sum_horizontal(T1, T2):
    '''Takes two rectangular standard tableau with the same number of rows and returns the
       'horizontal sum' obtained by placing T1 left of T2 and incrementing the entries of T2.'''
    L1 = to_lattice_word(T1)
    L2 = to_lattice_word(T2)
    return from_lattice_word(L1 + L2)

def sum_vertical(T1, T2):
    '''Takes two rectangular standard tableau with the same number of columns and returns the
       'vertical sum' obtained by placing T1 on top of T2 and incrementing the entries of T2.'''
    L1 = to_lattice_word(T1)
    L2 = to_lattice_word(T2)
    r = len(T1)
    L2 = [_ + r for _ in L2]
    return from_lattice_word(L1 + L2)

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
    return [i if i != 0 else n for i in ret]
