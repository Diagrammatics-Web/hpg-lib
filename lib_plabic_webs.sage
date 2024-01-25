def is_prom_minimal(L, r):
    '''Determines if L is lex-minimal among all of its promotions.'''
    L0 = list(L)
    while True:
       L = promotion_L(L, r)
       if L < L0:
           return False
       if L == L0:
           break
    return True

def get_G_from_L(L, r, ignore_trips_above=-1):
    '''Iterates over all solutions of get_G_from_trips for the prom permutations
       of the oscillating word L.'''
    ps = prom_perms_L(L, r)
    boundary_type=[1 if el > 0 else -1 for el in L]
    yield from get_G_from_trips(ps, r, boundary_type=boundary_type, ignore_trips_above=ignore_trips_above)

def plot_hpg(H, edge_labels=True, **kwds):
    vertex_colors = {"gray":[k for k,v in H.vertices.items() if v.is_filled()],  "white":[k for k,v in H.vertices.items() if v.is_unfilled()]}
    return H.to_graph().plot(edge_labels=edge_labels, vertex_colors=vertex_colors, **kwds)

def get_fluctuating_Ls(content, r, flatten=True):
    '''Iterates over all rectangular fluctuating tableau of the given content with r rows.'''
    content_SSYT = [c if c > 0 else r+c for c in content]
    for T in SemistandardTableaux([r]*(sum(content_SSYT)//r), eval=content_SSYT):
        L = []
        for i in range(len(content_SSYT)):
            L.append([y+1 for x,y in T.cells_containing(i+1)])
        for i in range(len(content)):
            if content[i] < 0:
                L[i] = [j for j in range(-r, 0) if -j not in L[i]]
        if flatten:
            L = _flatten(L)
        yield L

def _flatten(xss):
    return [x for xs in xss for x in xs]

def Aexc(pi):
    '''Returns the list of anti-excedances of the permutation pi in sorted order.'''
    return sorted(pi[i] for i in range(len(pi)) if i+1 > pi[i])

def blow_up(G,power=1):
    pos = G.get_pos()
    for v in G:
        if type(v)!=int:
            pos[v] = pos[v]*numpy.linalg.norm(pos[v])**power
    G.set_pos(pos)
    return G

def refine_positions(G, niter, step=0.5):
    def neighbour_mean(v,pos):
        return sum([pos[w] for w in G[v]])/len(G[v])
    pos = G.get_pos()
    V = [v for v in G if type(v)!=int]
    for _ in range(niter):
        v = max(V, key=lambda v: numpy.linalg.norm(pos[v]-neighbour_mean(v,pos)))
        pos[v] = pos[v]*(1-step) + neighbour_mean(v,pos)*step
        #print("selecting",v)
    G.set_pos(pos)
    return G

def calculate_positions(G, pow=2):
    G = blow_up(G, power=100)
    G = refine_positions(G, int(len(G)**pow), step=0.5)

def plot_from_raw(G, edge_labels=False):
    n = sum(1 for v in G if type(v)==int)
    show(sum([text(i+1,vector(pt)*1.1) for i,pt in enumerate(create_boundary_coordinates(n))],G.plot(vertex_labels=False,edge_labels=edge_labels,vertex_size=0,figsize=(6,6))),axes=False,aspect_ratio=1)

def contains(big, small):
    for i in range(len(big)-len(small)+1):
        for j in range(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return True
    return False

def occurrences(big, small):
    '''Consecutive occurrences.'''
    for i in range(len(big)-len(small)+1):
        for j in range(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            yield i

def first_occurrence(big, small):
    '''Yields the first occurrence, or an empty iterator.'''
    for i in range(len(big)-len(small)+1):
        for j in range(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            yield i
            return

def has_subsequence(subseq, seq):
    '''Determines whether the list seq contains the list subseq as a possibly non-consecutive subsequence.'''
    it = iter(seq)
    return all(x in it for x in subseq)

def first_subsequence(subseq, seq):
    '''Yields the index of the last element of the first appearance of the subsequence. If none, empty iterator.'''
    i=0
    j=0
    for i in range(len(seq)):
        if seq[i] == subseq[j]:
            j += 1
            if j == len(subseq):
                yield i
                return
        i += 1

def avoids_subsequence(subseq, seq):
    return not has_subsequence(subseq, seq)

def right_long_good_degens(L, asc, des, star_witnesses, avoiders):
    '''Yields triples (i, i+1, j) where i, i+1 are the indexes of the ascent and j is the index of the first star witness
       to the right. Here des is the result of applying the degeneration to asc if it applies.'''
    for i in occurrences(L, asc):
        Lp = L[i+2:]
        for sw in star_witnesses:
            for j in first_subsequence(sw, Lp):
                Lpp = Lp[:j+1]
                if all(avoids_subsequence(avoider, Lpp) for avoider in avoiders):
                    yield(i, i+1, des, i+j+2)

def right_long_good_degen_applies(L, asc, star_witnesses, avoiders):
    return any(True for _ in right_long_good_degens(L, asc, star_witnesses, avoiders))

def right_long_good_degens_all(L, skip_witnessless=False):
    '''Yields triples (i, i+1, j) where i, i+1 is are the indexes of the ascent in a good degeneration and j is the index of
       the first star witness to the right. Use j=None if no witnesses are used.'''
    yield from chain(right_long_good_degens(L,   [1, 2], [2, 1], [[2], [-1]], [[1], [4], [3], [-2]]),
                     right_long_good_degens(L, [-4, -3], [2, 1], [[2], [-1]], [[1], [4], [3], [-2]]),
                     right_long_good_degens(L,   [1, 3], [3, 1], [[3], [2], [-1]], [[1], [4], [-3, 3], [-3, -2, 2], [-3, -2, -1]]),
                     right_long_good_degens(L, [-4, -2], [3, 1], [[3], [2], [-1]], [[1], [4], [-3, 3], [-3, -2, 2], [-3, -2, -1]]),
                     right_long_good_degens(L,   [1, 4], [4, 1], [[4], [3], [2], [-1]], [[1], [-4, 4], [-4, -3, 3], [-4, -3, -2, 2], [-4, -3, -2, -1]]),
                     right_long_good_degens(L, [-3, -2], [4, 1], [[4], [3], [2], [-1]], [[1], [-4, 4], [-4, -3, 3], [-4, -3, -2, 2], [-4, -3, -2, -1]]),
                     right_long_good_degens(L, [1, -3], [-3, 1], [[-1], [2]], [[1], [-2], [3, -1], [3, 2]]),
                     right_long_good_degens(L, [1, -3], [-3, 1], [[-1]], [[1], [-2], [-3, -1], [3, 4, -1]]),
                     right_long_good_degens(L, [1, -4], [-4, 1], [[-1], [2, 3]], [[1], [4], [-3], [-2]]))

    if skip_witnessless:
        yield from chain(((i, i+1, [], None) for i in occurrences(L, [1, -1])),
                         ((i, i+1, [-2, 1], None) for i in occurrences(L, [1, -2])),
                         ((i, i+1, [-1, 2], None) for i in occurrences(L, [2, -1])),
                         ((i, i+1, [-1, 1], None) for i in occurrences(L, [2, -2])))

def right_long_good_degens_apply(L):
    any(True for _ in right_long_good_degens_all(L))

def degens(L):
    n1 = len(L)-1
    yield from right_long_good_degens_all(L)
    for i, i1, des, j in right_long_good_degens_all(tau(eps(L))):
        yield (i, i1, tau(eps(des)), j)
    for i, i1, des, j in right_long_good_degens_all(tau(L), skip_witnessless=True):
        if j is None:
            yield (n1-i1, n1-i, tau(des), j)
        else:
            yield (n1-i1, n1-i, tau(des), n1-j)
    for i, i1, des, j in right_long_good_degens_all(eps(L), skip_witnessless=True):
        if j is None:
            yield (n1-i1, n1-i, eps(des), j)
        else:
            yield (n1-i1, n1-i, eps(des), n1-j)

def degen_applies(L):
    return any(True for _ in degens(L))

def some_degen(L):
    cur_L = list(L)
    ret_Ls = [cur_L]
    ret_edges = []
    while True:
        for i, i1, des, j in degens(cur_L):
            ret_edges.append((i, i1, j))
            cur_L = list(cur_L)
            if des==[]:
                del cur_L[i:i+2]
            else:
                cur_L[i] = des[0]
                cur_L[i1] = des[1]
            ret_Ls.append(cur_L)
            break
        else:
            return ret_Ls, ret_edges

degen_latex = {1:r'\mathrm{\texttt{1}}', -4:r'\dot{\mathrm{\texttt{1}}}', 2:r'\mathrm{\texttt{2}}', -3:r'\dot{\mathrm{\texttt{2}}}', 3:r'\mathrm{\texttt{3}}', -2:r'\dot{\mathrm{\texttt{3}}}', 4:r'\mathrm{\texttt{4}}', -1:r'\dot{\mathrm{\texttt{4}}}'}
def show_degen(degen, path=False):
    Ls, edges = degen
    if not path:
        Ls_latex = [[degen_latex[x] for x in L] for L in Ls]
    else:
        Ls, edges = degen_path(degen)
        Ls_latex = [[r'\texttt{'+x+r'}' for x in L] for L in Ls]
    ret = []
    for k in range(len(edges)):
        i, i1, j = edges[k]
        if j is not None:
            Ls_latex[k][j] = r'\underline{' + Ls_latex[k][j] + r'}'
        ret.append(''.join(Ls_latex[k]))
        if len(Ls_latex[k+1]) == len(Ls_latex[k]):
            ret.append(r'\mathrm{\texttt{|}}'*i + r'\hspace{0.1cm}\mathrm{\texttt{X}}\hspace{0.1cm}' + r'\mathrm{\texttt{|}}'*(len(Ls_latex[k])-i-2))
        else:
            ret.append(r'\mathrm{\texttt{|}}'*i + r'\hspace{0.1cm}\mathrm{\texttt{V}}\hspace{0.1cm}' + r'\mathrm{\texttt{|}}'*(len(Ls_latex[k])-i-2)) # \widecheck{\texttt{\ \ }}
            ret.append(r'\mathrm{\texttt{|}}'*i + r'\texttt{\ }' + r'\mathrm{\texttt{/}}'*(len(Ls_latex[k])-i-2))
            ret.append(r'\mathrm{\texttt{|}}'*i + r'\mathrm{\texttt{|}}'*(len(Ls_latex[k])-i-2))
    ret.append(''.join(Ls_latex[-1]))
    if ret[-1] == '': ret[-1] = r'\varnothing'
    show(LatexExpr(r'\\'.join(ret)))

def degen_path(degen):
    '''Replaces the labels +/- 1, ..., 4 with strings A, B, ..., Z, a, b, ....
       The strings are constant on Trip_2 paths up to endcaps. The strings start in linear ASCII order.'''
    Ls, edges = degen
    new_Ls = []
    cur_L = [chr(65+i) for i in range(len(Ls[0]))]
    new_Ls.append(list(cur_L))
    for k in range(len(edges)):
        i, i1, j = edges[k]
        if len(Ls[k]) == len(Ls[k+1]):
            cur_L[i], cur_L[i1] = cur_L[i1], cur_L[i]
        else:
            del cur_L[i:i+2]
        new_Ls.append(list(cur_L))
    return (new_Ls, edges)

def show_degen_paths(degen):
    Ls, edges = degen
    cur_L = Ls[0]
    Ls_latex = [[degen_latex[x] for x in L] for L in Ls]
    ret = []
    for k in range(len(edges)):
        i, i1, j = edges[k]
        if j is not None:
            Ls_latex[k][j] = r'\underline{' + Ls_latex[k][j] + r'}'
        ret.append(''.join(Ls_latex[k]))
        if len(Ls_latex[k+1]) == len(Ls_latex[k]):
            ret.append(r'\mathrm{\texttt{|}}'*i + r'\hspace{0.1cm}\mathrm{\texttt{X}}\hspace{0.1cm}' + r'\mathrm{\texttt{|}}'*(len(Ls_latex[k])-i-2))
        else:
            ret.append(r'\mathrm{\texttt{|}}'*i + r'\hspace{0.1cm}\mathrm{\texttt{V}}\hspace{0.1cm}' + r'\mathrm{\texttt{|}}'*(len(Ls_latex[k])-i-2)) # \widecheck{\texttt{\ \ }}
            ret.append(r'\mathrm{\texttt{|}}'*i + r'\texttt{\ }' + r'\mathrm{\texttt{/}}'*(len(Ls_latex[k])-i-2))
            ret.append(r'\mathrm{\texttt{|}}'*i + r'\mathrm{\texttt{|}}'*(len(Ls_latex[k])-i-2))
    ret.append(''.join(Ls_latex[-1]))
    if ret[-1] == '': ret[-1] = r'\varnothing'
    show(LatexExpr(r'\\'.join(ret)))

import numpy
from itertools import chain
import itertools

# %load promotion_permutation_utils.sage

def prom_perm(T, k):
    '''Computes the promotion permutation of a rectangular standard Young tableau T with shape b^a as
       defined by Sam Hopkins.

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

def middle_matching(T):
    '''If T is a rectangular standard tableau with 2k rows, prom(T, k) is a fixed-point free involution. Returns that matching.

       sage: T = StandardTableau([[1, 4, 6, 9, 10, 13, 19, 20, 28, 29], [2, 7, 8, 12, 17, 18, 23, 25, 31, 33], [3, 11, 14, 15, 21, 22, 27, 32, 34, 36], [5, 16, 24, 26, 30, 35, 37, 38, 39, 40]])

       sage: middle_matching(T)
       [(1, 3), (2, 5), (4, 15), (6, 11), (7, 40), (8, 39), (9, 22), (10, 14), (12, 21), (13, 16), (17, 36), (18, 27), (19, 26), (20, 24), (23, 38), (25, 30), (28, 34), (29, 32), (31, 37), (33, 35)]
    '''
    assert is_even(len(T))
    k = len(T)//2
    pi = prom_perm(T, k)
    return PerfectMatching(pi.cycle_tuples())

def growth_matrix(T):
    '''Takes an r x m rectangular standard tableau T and computes the 'growth matrix' of T, which can be defined as
       the 'disjoint union of permutation matrices' defined by sum_{i=0}^{r-1} (i+1) Prom_i(T).'''
    n = T.size()
    r = len(T)

    # Return matrix and "state matrix".
    # M[i][j][k] is the number of k+2's minus the number of k+1's weakly southwest of entry (i, j)
    G = [[0 for j in range(n)] for i in range(n)]
    M = [[[0]*r for j in range(n)] for i in range(n)]

    # Set main diagonal 1's
    for i in range(n):
        G[i][i] = 1
        M[i][i][0] = 1

    # Compute M iteratively in columns from left to right
    for j, v in enumerate(to_lattice_word(T)):
        for i in range(j):
            # Insert v into entry (i, j) if possible; if not, decrement v and insert that
            if v > 1 and M[i][j-1][v-2] == 0:
                v -= 1
            G[i][j] = v
            M[i][j] = list(M[i][j-1])
            M[i][j][v-1] += 1
            if v > 1:
                M[i][j][v-2] -= 1

    # In each column, for all v, remove all but the bottom-most copy of v.
    #    Also fill in the lower-left triangle.
    for j in range(n):
        for i in range(j):
            if G[i+1][j] == G[i][j]:
                G[i][j] = 0
            else:
               G[j][i] = r + 2 - G[i][j]
    return Matrix(G)

def e_i(D, i):
    '''Applies i to a generalized Young diagram D viewed as a list of possibly negative weakly decreasing row lengths.
       Returns a new copy.'''
    Dp = list(D)
    if i > 0:
        Dp[i-1] += 1
        return Dp
    else:
        Dp[-i-1] -= 1
        return Dp

def valid_D(D):
    '''Determines if the list D consists weakly decreasing entries.'''
    for i in range(len(D)-1):
        if D[i+1] > D[i]:
            return False
    return True

def e_diff(D1, D2):
    '''Takes two generalized Young diagrams and returns i such that e_i(D1, i) = D2.
       Assumes such i exists.'''
    for i in range(len(D1)):
        if D1[i] != D2[i]:
            if D2[i] > D1[i]:
                return i+1
            else:
                return -(i+1)

def local_rule(ll, ul, ur):
    '''Applies the generalized oscillating tableau local rule to compute the lower right
       corner given the lower left, upper left, and upper right. Follows Patrias' Def. 4.6.'''
#    print(ll, ul, ur)
    i = e_diff(ll, ul)
    j = e_diff(ul, ur)
    if i > 0:
        # OP1
        if j > 0:
            # OP1(a) or (b)
            ret = e_i(ll, j)
            if valid_D(ret):
                # OP1(a)
                return ret
            else:
                # OP1(b)
                return e_i(ll, i)
        else:
            # OP1(c) or (d)
            ret = e_i(ll, j)
            if valid_D(ret):
                # OP1(c)
                return ret
            else:
                # OP1(d)
                for t in range(1, len(ll)):
                    ret = e_i(ll, j-t)
                    if valid_D(ret):
                        return ret
    else:
        # OP2
        if j < 0:
            # OP2(a) or (b)
            ret = e_i(ll, j)
            if valid_D(ret):
                # OP2(a)
                return ret
            else:
                # OP2(b)
                return e_i(ll, i)
        else:
            # OP2(c) or (d)
            ret = e_i(ll, j)
            if valid_D(ret):
                # OP2(c)
                return ret
            else:
                # OP2(d)
                for t in range(1, len(ll)):
                    ret = e_i(ll, j-t)
                    if valid_D(ret):
                        return ret

def growth_diagram(L, m):
    '''Takes a signed Yamanouchi word L as a list of numbers from +/- 1, 2, ..., m.
       Computes the growth diagram of L obtained by performing promotion len(L) times.
       '''
    # Compute sequence of generalized Young diagrams associated to L
    M_cur = [0]*m
    M_init = [M_cur]
    for el in L:
        M_cur = e_i(M_cur, el)
        assert valid_D(M_cur)
        M_init.append(M_cur)
    M = [M_init]

    # Compute promotions
    n = len(L)
    n1 = n+1
    M_prev = M_init
    for i in range(1,n+1):
        M_next = [[]]*(n+1)
        M_next[i] = [0]*m
        for j in range(1,n):
            M_next[(i+j) % n1] = local_rule(M_next[(i+j-1) % n1], M_prev[(i+j-1) % n1], M_prev[(i+j) % n1])
        M_next[(i+n) % n1] = list(M_init[-1])
        M.append(M_next)
        M_prev = M_next
    return M

def evacuation(L, m):
    '''Takes a signed Yamanouchi word L with maximum m.
       Computes the evacuation of L.'''
    M = growth_diagram(L, m)
    L = []
    for j in range(len(M)-1, 0, -1):
        L.append(e_diff(M[j][-1], M[j-1][-1]))
    return L

def promotion_L(L, m):
    '''Takes a signed Yamanouchi word L with maximum m.
       Computes the promotion of L.'''
    # Compute sequence of generalized Young diagrams associated to L
    M_cur = [0]*m
    M = [M_cur]
    for el in L:
        M_cur = e_i(M_cur, el)
        assert valid_D(M_cur)
        M.append(M_cur)

    P = [[0]*m]
    for i in range(1, len(M)-1):
        P.append(local_rule(P[-1], M[i], M[i+1]))
    P.append(list(M[-1]))

    Lp = []
    for j in range(len(P)-1):
        Lp.append(e_diff(P[j], P[j+1]))
    return Lp

def promotion_power_L(L, k, m):
    '''Takes a signed Yamanouchi word L with maximum m.
       Computes the mth power of promotion of L.'''
    Lp = L
    for i in range(k):
        Lp = promotion_L(Lp, m)
    return Lp

def promotion_orbit_L(L, m):
    '''Takes a signed Yamanouchi word L with maximum m.
       Computes the promotion orbit of L as a set.'''
    cur = L
    ret = set()
    ret.add(tuple(L))
    o = len(ret)
    while True:
        cur = promotion_L(cur, m)
        ret.add(tuple(cur))
        if len(ret) == o:
            break
        o += 1
    return ret

def is_prom_minimal_L(L, m):
    '''Takes a signed Yamanouchi word L with maximum m.
       Determines if L is lexicographically minimal in its
       promotion orbit.'''
    return tuple(L) == min(promotion_orbit_L(L, m))

def growth_matrix_L(L, m, diffs_only=False, signed=True):
    '''Takes a signed Yamanouchi word L with maximum m.
       Computes the growth matrix of L.'''
    # First make a matrix recording the row of the bullet during
    #   all the JDT's
    M = growth_diagram(L, m)
    n = len(L)
    GM = []
    for i in range(1,n+1):
        GM.append([])
        GM_row = GM[-1]
        for j in range(n+1):
            if i-1 != j:
                GM_row.append(e_diff(M[i][j], M[i-1][j]))
    if diffs_only: return GM

    # Now pick off the first new entries in each row to form the growth matrix
    ret = [[[] for _ in range(len(GM))] for __ in range(len(GM))]
    for i in range(len(GM)):
        if GM[i][i] > 0:
            k_prev = 0
            for j in chain(range(i, len(GM)), range(i)):
                if GM[i][j] > k_prev:
                    ret[i][j] = list(range(k_prev+1, GM[i][j]+1))
                    k_prev = GM[i][j]
        else:
            k_prev = -m-1
            for j in chain(range(i, len(GM)), range(i)):
                if GM[i][j] > k_prev:
                    ret[i][j] = list(range(k_prev, GM[i][j]))
                    if k_prev == -m-1:
                        ret[i][j] = [-1]
                    k_prev = GM[i][j]

    for j in range(len(ret)):
        if L[j] < 0:
            for i in range(len(ret)):
                ret[i][j] = list(reversed(sorted([-abs(_) for _ in ret[i][j]])))

    if not signed:
        for j in range(len(ret)):
            for i in range(len(ret)):
                ret[i][j] = [abs(_) for _ in ret[i][j]]

    return ret

def m_pp(M):
    s = [[str(e) for e in row] for row in M]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))

def prom_perm_L(L, m, k):
    '''Computes the kth promotion permutation of a signed, balanced Yamanouchi word L
       with maximum possible letter m. Returns literal permutations, not signed
       permutations.'''
    M = growth_matrix_L(L, m)
    ret = []
    for row in M:
        for i in range(len(row)):
            if k+1 in [abs(_) for _ in row[i]]:
                ret.append(i+1)
                break
    return Permutation(ret)

def prom_perms_L(L, m):
    '''Returns a list of all promotion permutations.'''
    M = growth_matrix_L(L, m)
    ret = [[] for _ in range(m)]
    for row in M:
        for i in range(len(row)):
            for k1 in [abs(_) for _ in row[i]]:
                ret[k1-1].append(i+1)
    return [Permutation(_) for _ in ret]

def middle_matching_L(L, m):
    assert is_even(m)
    k = m//2
    pi = prom_perm_L(L, m, k)
    return PerfectMatching(pi.cycle_tuples())

def yams_sb(m, n):
    '''Iterates over all signed, balanced Yamanouchi words on letters from +/- 1, ..., +/- m
       of length n.

       Currently quite inefficient in that it imposes the balanced condition at the
       very end as a filter.'''
    cur_Y = []
    cur_la = [0]*(m+2)  # cur_la[i] = number of i's (minus number of -(i)'s)
    cur_la[0] = n
    cur_la[-1] = -n
    def _yams_sb(n):
        if n==0:
            Y1 = cur_la[1]
            if all(Y1 == cur_la[i] for i in range(1, m+1)):
                yield cur_Y
            return
        for i in range(1,m+1):
            if cur_la[i-1] > cur_la[i]:
                cur_Y.append(i)
                cur_la[i] += 1
                yield from _yams_sb(n-1)
                cur_la[i] -= 1
                cur_Y.pop()
            if cur_la[i] > cur_la[i+1]:
                cur_Y.append(-i)
                cur_la[i] -= 1
                yield from _yams_sb(n-1)
                cur_la[i] += 1
                cur_Y.pop()

    for Y in _yams_sb(n):
        yield list(Y)

def yams_s(m, n):
    '''Iterates over all signed Yamanouchi words on letters from +/- 1, ..., +/- m
       of length n.'''
    cur_Y = []
    cur_la = [0]*(m+2)  # cur_la[i] = number of i's (minus number of -(i)'s)
    cur_la[0] = n
    cur_la[-1] = -n
    def _yams_s(n):
        if n==0:
            yield cur_Y
            return
        for i in range(1,m+1):
            if cur_la[i-1] > cur_la[i]:
                cur_Y.append(i)
                cur_la[i] += 1
                yield from _yams_s(n-1)
                cur_la[i] -= 1
                cur_Y.pop()
            i = m+1-i # Iterate in \tilde-lex order
            if cur_la[i] > cur_la[i+1]:
                cur_Y.append(-i)
                cur_la[i] -= 1
                yield from _yams_s(n-1)
                cur_la[i] += 1
                cur_Y.pop()

    for Y in _yams_s(n):
        yield list(Y)

def des_L(L):
    '''Computes the descent sets (D_+, D_-) of the signed lattice word L.
       Here D_+ consists of the list of all indexes i (starting from 1) for which
       0 < L_i < L_{i+1}. D_- consists of all indexes i (starting from 1)
       for which 0 > L_i > L_{i+1}.'''
    D_plus  = [i+1 for i in range(len(L)-1) if 0 < L[i] < L[i+1]] + [i+1 for i in range(len(L)-1) if L[i] < 0 < L[i+1]]
    D_minus = [] #[i+1 for i in range(len(L)-1) if 0 > L[i+1] > L[i]] + [i+1 for i in range(len(L)-1) if L[i] < 0 < L[i+1]]
    return (D_plus, D_minus)

def full_maj_L(L):
    D_plus, D_minus = des_L(L)
    return sum(i for i in D_plus) + sum(i for i in D_minus)

def D_to_C(D, n):
    '''Takes a subset D of {1, ..., n-1} and returns the
       corresponding strong composition. Assumes D is a
       list [i1, i2, ..., ik] where 1 <= i1 < i2 < ... < ik < n.'''
    L = [0] + D + [n]
    return [L[i] - L[i-1] for i in range(1, len(L))]

def strand_intersection(strand1_from, strand1_to, strand2_from, strand2_to):
    #s,t = var('s t')
    #return solve([a*s+b*(1-s)==c*t+d*(1-t) for a,b,c,d in zip(strand1_from, strand1_to, strand2_from, strand2_to)],s,t)
    b = [u-v for u,v in zip(strand1_from, strand2_from)]
    M = [[strand1_from[i]-strand1_to[i],strand2_to[i]-strand2_from[i]] for i in range(2)]
    if numpy.linalg.det(M) == 0:
        return False
    s,t = numpy.linalg.solve(M,b)
    if not (0<s<1 and 0<t<1):
        return False
    return (s,t)

def create_random_boundary_coordinates(n):
    angles = [i+(random()-0.5)/4 for i in range(n)]
    return [(sin(i*2*pi/n).n(),cos(i*2*pi/n).n()) for i in angles]

def create_boundary_coordinates(n):
    angles = [i for i in range(n)]
    return [(sin(i*2*pi/n).n(),cos(i*2*pi/n).n()) for i in angles]

def random_crossing_graph(M):
    C = M.crossings()
    G = DiGraph([C + list(range(1,2*len(M)+1)), []], format='vertices_and_edges')
    boundary_coordinates_random = create_random_boundary_coordinates(M.size())
    boundary_coordinates_real = create_boundary_coordinates(M.size())
    LL = {}
    pos = {}

    for i in range(1, M.size()+1):
        pos[i] = vector(boundary_coordinates_real[i-1])

    for c in C:
        for arc in c:
            if arc not in LL:
                LL[arc] = {}
        # check if clockwise or acw is correct here!!!
        s,t = strand_intersection(boundary_coordinates_random[c[0][0]-1],boundary_coordinates_random[c[0][1]-1],boundary_coordinates_random[c[1][0]-1],boundary_coordinates_random[c[1][1]-1])
        LL[c[0]][c] = s
        LL[c[1]][c] = t
        pos[c] = (1-s)*vector(boundary_coordinates_random[c[0][0]-1])+s*vector(boundary_coordinates_random[c[0][1]-1])



    # First traverse each arc (a, b) with a < b, finding the order in which
    #    k-fold intersections appear and adding directed labeled edges between them.
    #    Directions are left to right, labels are the arc (a, b).
    for arc, L in LL.items():
        #print(arc, L)
        (a, b) = arc

        Lsorted = [a] + sorted(L,key=L.get) + [b]
        #print(arc, Lsorted)
        for i in range(len(Lsorted) - 1):
            G.add_edge(Lsorted[i], Lsorted[i+1], label=arc)


    #print("in and out")
    # Deduce the planar orientation (clockwise order) of the edges around each k-fold vertex
    embedding = {}
    for v in G:
        #print(v, G.incoming_edges(v), G.outgoing_edges(v))
        L  = [(l, a) for (l, _, (a, b)) in G.incoming_edges(v)]
        L += [(r, b) for (_, r, (a, b)) in G.outgoing_edges(v)]
        L = sorted(L, key=lambda x: x[1])
        L = [_[0] for _ in L]
        embedding[v] = L

    G = Graph(G)
    #G._circle_embedding((list(range(1,2*len(M)+1))))
    G.set_embedding(embedding)
    G.set_pos(pos)
    return G

def graph_orientations(G, LW=None, verbose=False):
    '''Takes a graph with 'outer' vertices of degree 1 and 'interior' vertices of degree 4.
       Iterates over all assignments of edge orientations subject to the following constraints:

           1. When L is None, Outer vertices have outgoing edges. When LW is set,
              the ith outer vertex is outgoing if the ith element of LW is positive,
              otherwise it is incoming.
           2. Interior vertices are either sources, sinks, or they have two planar-adjacent
              incoming and two planar-adjacent outgoing edges.
    '''
    V = list(G)
    E = G.edges(labels=False, sort=False)
    emb = G._embedding
    pos = G.get_pos()

    # Track the orientations of edges in the embedding's order:
    #    +1 means incoming, -1 means outgoing, 0 means unassigned
    ori = {v : [0]*len(emb[v]) for v in V}

    # Set outer vertex edges
    for v,L in ori.items():
        if len(L) == 1:
            s = 1 if (LW is None) or (LW[v-1] > 0) else -1
            w = emb[v][0]
            ori[v][emb[v].index(w)] = -s #-1
            ori[w][emb[w].index(v)] = s  # 1

    # Track how many orientations around each vertex have been filled in
    #   zs[i] = list of interior vertexes with i unchosen orientations
    def _count_zeros(L):
        return sum(1 for _ in L if _ == 0)

    zs = [[] for i in range(5)]
    for v in V:
        L = ori[v]
        if len(L) == 4:
            zs[_count_zeros(L)].append(v)

    def _to_digraph():
        # Converts ori and emb to a digraph
        DG = DiGraph({v: [emb[v][i] for i in range(len(L)) if L[i] == -1] for v,L in ori.items()})
        DG._embedding = deepcopy(emb)
        DG._ori = deepcopy(ori)
        DG.set_pos(deepcopy(pos))
        return DG

    # Use recursive backtracking to compute all ways to complete orientation assignments
    def _graph_orientations():
        # Assume the current orientation assignments either satisfy the constraints or
        #   can be locally completed in a way that satisfies the constraints.

        # If everything has been assigned, just yield and return
        if all(zs[i] == [] for i in range(1, 5)):
            yield _to_digraph()
            return

        updated_edges = []

        def _validate(L):
            # Check if the local configuration L, a list of 0's, 1's, -1's of length 4, is
            #    locally valid (i.e. can be completed to a valid configuration)
            z = _count_zeros(L)
            s = sum(L)

            if z == 0:
                if s == 2 or s == -2:
                    return False
                if s == 0:
                    if L[0] == -L[1] == L[2] == -L[3]:
                        return False
                return True

            if z == 1:
                if s == 3 or s == -3:
                    return True
                if L[0] == L[2] or L[1] == L[3]:
                    return False
                return True

            return True

        def _update_validate(u, v, c):
            # Assumes the u<->v edge is unoriented and that u will pass validation after the update
            if verbose: print("Updating: ", u, v, c)

            Lu = emb[u]
            Lv = emb[v]
            Ou = ori[u]
            Ov = ori[v]

            zu = _count_zeros(Ou)
            zv = _count_zeros(Ov)

            i = Lu.index(v)
            j = Lv.index(u)

            # Update zs's lists
            zs[zu].remove(u)
            zs[zu-1].append(u)
            zs[zv].remove(v)
            zs[zv-1].append(v)

            # Update orientations
            Ou[i] = c
            Ov[j] = -c

            # Log changes
            updated_edges.append((u, i))
            updated_edges.append((v, j))

            # Validate v's local configuration
            return _validate(Ov)

        def _rollback():
            (u, i) = updated_edges.pop()
            if verbose: print("Rolling back: ", u, emb[u][i])
            zu = _count_zeros(ori[u])
            ori[u][i] = 0
            zs[zu].remove(u)
            zs[zu+1].append(u)
            return

        # Iteratively find edges whose orientations are forced.
        # Recursively bifurcate only when we run out of forced edges.
        # Terminate if we find a forced inconsistency.
        valid = True
        while valid:
            if len(zs[1]) > 0:
                # Work through vertexes with one 0 first
                u = zs[1][0]
                i = ori[u].index(0)
                v = emb[u][i]

                s = sum(ori[u])
                if abs(s) == 3:
                    c = sgn(s)
                else: # abs(s) = 1
                    c = -sgn(s)

                valid = _update_validate(u, v, c)

                continue

            if len(zs[2]) > 0:
                # Work through vertexes with two 0's. Usually this is where bifurcation happens
                u = zs[2][0]
                s = sum(ori[u])
                i1 = ori[u].index(0)
                v1 = emb[u][i1]
                i2 = ori[u].index(0, i1+1)
                v2 = emb[u][i2]

                if i2 == i1 + 2 and s != 0:
                    c = sgn(s) 

                    valid = _update_validate(u, v1, c) and _update_validate(u, v2, c)

                    continue

                # Try one branch
                if verbose: print("Guessing branch +1")
                valid = _update_validate(u, v1, 1)
                if valid and _validate(ori[u]):
                    yield from _graph_orientations()
                _rollback()
                _rollback()
                if verbose: print("Finished branch +1")

                # Try the other branch
                if verbose: print("Guessing branch -1")
                valid = _update_validate(u, v1, -1)
                if valid and _validate(ori[u]):
                    yield from _graph_orientations()
                _rollback()
                _rollback()
                if verbose: print("Finished branch -1")

                # We've exhausted all possibilities in this branch
                break

            if all(zs[i] == [] for i in range(1, 5)):
                # All edges have been assigned!
                yield _to_digraph()
                break

            raise Exception("There are no vertexes with one or two 0's, yet assignments are incomplete. This should not happen.")

        # Rollback edge updates
        while updated_edges != []:
            _rollback()

    yield from _graph_orientations()

def oriented_graph_labelings(OG, T, verbose=False):
    '''Takes an oriented graph OG from the output of graph_labelings
       and a lattice word T representing a 4 x m standard tableau, where OG has 4m outer vertices.
       Iterates over all assignments of edge labels subject to the following constraints:
           1. Sources and sinks have edges 1, 2, 3, 4 each used once.
           2. Vertices with two planar-adjacent incoming and two planar-adjacent outgoing edges
              use the same two labels for both the incoming and the outgoing edges.
           3. Edges incident to boundary vertices are labeled according to T.
    '''
    V = list(OG)
    emb = OG._embedding
    ori = OG._ori
    pos = OG.get_pos()

    # Track the labels of edges in the embedding's order:
    #    0 means not set, otherwise it's 1, 2, 3, or 4
    lab = {v : [0]*len(emb[v]) for v in V}

    # Set outer vertex edge labels according to (absolute values of) T
    for v,L in lab.items():
        if len(L) == 1:
            w = emb[v][0]
            c = abs(T[v-1])
            lab[v][emb[v].index(w)] = c
            lab[w][emb[w].index(v)] = c

    # Track how many labels around each vertex have been filled in
    #   zs[i] = list of interior vertexes with i unchosen labels
    def _count_zeros(L):
        return sum(1 for _ in L if _ == 0)

    zs = [[] for i in range(5)]
    for v in V:
        L = lab[v]
        if len(L) == 4:
            zs[_count_zeros(L)].append(v)

    def _to_digraph():
        # Stamp off a new copy of this graph with correct edge labels and return it
        DG = DiGraph({v: {emb[v][i]: lab[v][i] for i in range(len(L)) if L[i] == -1} for v,L in ori.items()})
        DG._embedding = deepcopy(emb)
        DG._ori = deepcopy(ori)
        DG._lab = deepcopy(lab)
        DG.set_pos(deepcopy(pos))
        return DG

    # Use recursive backtracking to compute all ways to complete label assignments
    rl = -1
    def _graph_labels():
        # Assume the current label assignments either satisfy the constraints or
        #   can be locally completed in a way that satisfies the constraints.
        nonlocal rl
        rl += 1
        if all(zs[i] == [] for i in range(1, 5)):
            # If everything has been assigned, just yield and return
            yield _to_digraph()
            rl -= 1
            return

        updated_edges = []

        def _validate(L_label, L_ori):
            # Check if the local configuration L_label, a list of 0-4's of length 4,
            #    and L_ori, a valid list of +/-1's, is
            #    locally valid (i.e. can be completed to a valid configuration)
            s = sum(L_ori)

            if s == 4 or s == -4:
                # Source or sink; non-empty labels just need to be injective
                c = [0]*5
                for i in range(4):
                    c[L_label[i]] += 1
                valid = all(c[j] <= 1 for j in range(1, 5))
                if not valid and verbose: print(":"*rl+"Invalid: not injective", L_label, L_ori, c)
                return valid

            # Expandable vertex
            a = L_ori.index(1)
            if a==0 and L_ori[-1]==1:
                a=-1
            in1  = L_label[a % 4]
            in2  = L_label[(a+1) % 4]
            out1 = L_label[(a+2) % 4]
            out2 = L_label[(a+3) % 4]

            if (in1 == in2 and in1 != 0) or (out1 == out2 and out1 != 0):
                return False

            # Both ins are 0 or distinct; both outs are 0 or distinct
            return len(set([l for l in L_label if l != 0])) <= 2

        def _update_validate(u, v, c):
            # Updates the edge between u and v to have label c.
            # Assumes that u will pass validation after the update.
            if verbose: print(":"*rl+"Updating: ", u, v, c)

            Lu = emb[u]
            Lv = emb[v]
            Ou = ori[u]
            Ov = ori[v]
            lu = lab[u]
            lv = lab[v]

            zu = _count_zeros(lu)
            zv = _count_zeros(lv)

            i = Lu.index(v)
            j = Lv.index(u)

            # Update zs's lists
            zs[zu].remove(u)
            zs[zu-1].append(u)
            zs[zv].remove(v)
            zs[zv-1].append(v)

            # Update labels
            lu[i] = c
            lv[j] = c

            # Log changes
            updated_edges.append((u, i))
            updated_edges.append((v, j))

            # Validate v's local configuration
            return _validate(lv, Ov)

        def _rollback():
            (u, i) = updated_edges.pop()
            if verbose: print(":"*rl+"Rolling back: ", u, emb[u][i])
            zu = _count_zeros(lab[u])
            lab[u][i] = 0
            zs[zu].remove(u)
            zs[zu+1].append(u)
            return

        # Iteratively find edges whose labels are forced.
        # Recursively bifurcate only when we run out of forced labels.
        # Terminate if we find a forced inconsistency.
        valid = True
        while valid:
            if len(zs[1]) > 0:
                # Work through vertexes with one 0 first
                u = zs[1][0]
                ou = ori[u]
                lu = lab[u]
                eu = emb[u]

                s = sum(ou)
                i = lu.index(0)
                v = eu[i]

                if s==4 or s==-4:
                    # Source or sink
                    c = min({1, 2, 3, 4}.difference(lu))

                    valid = _update_validate(u, v, c)

                    continue

                else:
                    # Expandable vertex
                    ins  = {lu[i] for i in range(4) if ou[i] ==  1 and lu[i] != 0}
                    outs = {lu[i] for i in range(4) if ou[i] == -1 and lu[i] != 0}

                    c = min(ins.symmetric_difference(outs))

                    valid = _update_validate(u, v, c)

                    continue

            if len(zs[2]) > 0:
                # Work through vertexes with two 0's. Bifurcates.
                u = zs[2][0]
                ou = ori[u]
                lu = lab[u]
                eu = emb[u]

                s = sum(ou)
                i1 = lu.index(0)
                v1 = eu[i1]
                i2 = lu.index(0, i1+1)
                v2 = eu[i2]

                if s==4 or s==-4:
                    # Source or sink
                    (c1, c2) = {1, 2, 3, 4}.difference(lu)

                    # Try both branches
                    if verbose: print(":"*rl+"Guessing branch %i, %i"%(c1, c2))
                    valid = _update_validate(u, v1, c1) & _update_validate(u, v2, c2)
                    if valid:
                        yield from _graph_labels()
                    _rollback()
                    _rollback()
                    _rollback()
                    _rollback()
                    if verbose: print(":"*rl+"Finished branch %i, %i"%(c1, c2))

                    if verbose: print(":"*rl+"Guessing branch %i, %i"%(c2, c1))
                    valid = _update_validate(u, v1, c2) & _update_validate(u, v2, c1)
                    if valid:
                        yield from _graph_labels()
                    _rollback()
                    _rollback()
                    _rollback()
                    _rollback()
                    if verbose: print(":"*rl+"Finished branch %i, %i"%(c2, c1))

                    break

                else:
                    # Expandable vertex
                    ins  = {lu[i] for i in range(4) if ou[i] ==  1 and lu[i] != 0}
                    outs = {lu[i] for i in range(4) if ou[i] == -1 and lu[i] != 0}

                    if len(ins) == 2 or len(outs) == 2:
                        # e.g. 12 ins and 00 outs or vice-versa
                        (c1, c2) = [_ for _ in lu if _ != 0]

                        if verbose: print(":"*rl+"Guessing branch %i, %i"%(c1, c2))
                        valid = _update_validate(u, v1, c1) & _update_validate(u, v2, c2)
                        if valid:
                            yield from _graph_labels()
                        _rollback()
                        _rollback()
                        _rollback()
                        _rollback()
                        if verbose: print(":"*rl+"Finished branch %i, %i"%(c1, c2))

                        if verbose: print(":"*rl+"Guessing branch %i, %i"%(c2, c1))
                        valid = _update_validate(u, v1, c2) & _update_validate(u, v2, c1)
                        if valid:
                            yield from _graph_labels()
                        _rollback()
                        _rollback()
                        _rollback()
                        _rollback()
                        if verbose: print(":"*rl+"Finished branch %i, %i"%(c2, c1))

                        break

                    else:
                        if ins != outs:
                            # e.g. 10 ins and 03 outs; complete to 13 and 13
                            (c_in, ) = ins
                            (c_out, ) = outs
                            c1 = c_in if ou[i1] == -1 else c_out
                            c2 = c_in if ou[i2] == -1 else c_out

                            if verbose: print(":"*rl+"Guessing branch %i, %i"%(c_in, c_out))
                            valid = _update_validate(u, v1, c1) & _update_validate(u, v2, c2)
                            if valid:
                                yield from _graph_labels()
                            _rollback()
                            _rollback()
                            _rollback()
                            _rollback()
                            if verbose: print(":"*rl+"Finished branch %i, %i"%(c_in, c_out))

                            break

                        else:
                            # e.g. 10 ins and 01 outs; complete to 1j ins and j1 outs for all j
                            cs = {1, 2, 3, 4}.difference(lu)
                            for c in cs:
                                if verbose: print(":"*rl+"Guessing branch %i"%(c))
                                valid = _update_validate(u, v1, c) & _update_validate(u, v2, c)
                                if valid:
                                    yield from _graph_labels()
                                _rollback()
                                _rollback()
                                _rollback()
                                _rollback()
                                if verbose: print(":"*rl+"Finished branch %i"%(c))

                            break

            if len(zs[3]) > 0:
                # Work through vertexes with three 0's. Bifurcates.
                u = zs[3][0]
                ou = ori[u]
                lu = lab[u]
                eu = emb[u]

                s = sum(ou)
                i1 = lu.index(0)
                v1 = eu[i1]
                i2 = lu.index(0, i1+1)
                v2 = eu[i2]
                i3 = lu.index(0, i2+1)
                v3 = eu[i3]

                if s==4 or s==-4:
                    # Source or sink
                    cs = {1, 2, 3, 4}.difference(lu)

                    # Try all branches
                    for c in cs:
                        if verbose: print(":"*rl+"Guessing branch %i"%(c))
                        valid = _update_validate(u, v1, c1)
                        if valid:
                            yield from _graph_labels()
                        _rollback()
                        _rollback()
                        if verbose: print(":"*rl+"Finished branch %i"%(c))

                    break

                else:
                    # Expandable vertex, e.g. 10 ins and 00 outs. Complete to 10 ins and either 10 outs or 01 outs
                    (j, ) = [_ for _ in range(4) if lu[_] != 0]
                    c = lu[j]

                    for i in range(4):
                        if i != j and ou[i] != ou[j]:
                            if verbose: print(":"*rl+"Guessing branch %i"%(c))
                            valid = _update_validate(u, oe[i], c)
                            if valid:
                                yield from _graph_labels()
                            _rollback()
                            _rollback()
                            if verbose: print(":"*rl+"Finished branch %i"%(c))

                    break

            if all(zs[i] == [] for i in range(1, 5)):
                # All labels have been assigned!
                yield _to_digraph()
                break

            raise Exception("There are no vertexes with one, two, or three 0's, yet assignments are incomplete. This should not happen.")

        # Rollback edge updates
        while updated_edges != []:
            _rollback()

        rl -= 1

    yield from _graph_labels()

def trip_perm(OG, k=1):
    assert(k==1 or k==2)

    # Compute the local permutations around each vertex
    m=0
    emb = OG._embedding
    ori = {v:[-1 if OG.has_edge(v, w) else 1 for w in L] for v,L in emb.items()}
    loc = {v:None for v,L in emb.items()}
    for v in OG:
        L = ori[v]
        # Always leave a leaf
        if len(L) == 1:
            m += 1
            continue

        # Handle four-way crossings
        s = sum(L)
        if k==2:
            # Always go straight across
            loc[v] = [2, 3, 0, 1]
            continue

        # Now k==1
        if s == 4:
            # Sink / "unfilled"
            loc[v] = [1, 2, 3, 0]
        elif s == -4:
            # Source / "filled"
            loc[v] = [3, 0, 1, 2]
        elif s == 0:
            # Two in/two out / "expandable"
            if L == [1, -1, -1, 1]:
                loc[v] = [2, 3, 1, 0]
            elif L == [1, 1, -1, -1]:
                loc[v] = [1, 3, 0, 2]
            elif L == [-1, 1, 1, -1]:
                loc[v] = [3, 2, 0, 1]
            elif L == [-1, -1, 1, 1]:
                loc[v] = [2, 0, 3, 1]
            else:
                raise Exception("Vertex is not actually expandable. This should not happen")
        else:
            raise Exception("Vertex is not a sink, source, or expandable. This should not happen")

    # Run through the graph and compute the trip permutation!
    ret = []
    for i in range(1, m+1):
        v = i
        w = emb[v][0]
        while type(w) is tuple:
            j = emb[w].index(v)
            v = w
            w = emb[w][loc[w][j]]
        ret.append(w)

    return Permutation(ret)

def center_of_gravity(vectors):
    return sum(vectors)/len(vectors)

def expand_to_plabic(G,edge_labels=True):
    ori = G._ori
    pos = G.get_pos()
    emb = G.get_embedding()

    if not edge_labels:
        for u,v in G.edges(sort=False, labels=False):
            G.set_edge_label(u,v, None)

    G.allow_multiple_edges(True)
    def is_expandable(v):
        return type(v) != int and sum(ori[v]) == 0

    expandables = [v for v in G if is_expandable(v)]

    for v in expandables:
        ov = ori[v]
        ev = emb[v]
        a = ov.index(1)
        if a==0 and ov[-1]==1:
            a=-1
        in1 = ev[a % 4]
        in2 = ev[(a+1) % 4]
        out1 = ev[(a+2) % 4]
        out2 = ev[(a+3) % 4]
        v_sink = (v, 1)
        v_source = (v, -1)
        G.add_vertices([v_sink, v_source])
        pos[v_sink] = center_of_gravity([pos[v],pos[in1],pos[in2]])
        pos[v_source] = center_of_gravity([pos[v],pos[out1],pos[out2]])
        label_in1  = G.edge_label(in1, v)[0]
        label_in2  = G.edge_label(in2, v)[0]
        label_out1 = G.edge_label(v, out1)[0]
        label_out2 = G.edge_label(v, out2)[0]
        G.delete_vertex(v)

        emb[in1][emb[in1].index(v)] = v_sink
        emb[in2][emb[in2].index(v)] = v_sink
        emb[out1][emb[out1].index(v)] = v_source
        emb[out2][emb[out2].index(v)] = v_source

        del ori[v]

        if edge_labels:
            G.add_edges([(in1, v_sink, label_in1), (in2, v_sink, label_in2), (v_source, out1, label_out1), (v_source, out2, label_out2)])
        else:
            G.add_edges([(in1, v_sink), (in2, v_sink), (v_source, out1), (v_source, out2)])

        # Hourglass edge!
        G.add_edge(v_source, v_sink) #, tuple(sorted({1, 2, 3, 4}.difference((label_in1, label_in2)))))
        G.add_edge(v_source, v_sink) #, tuple(sorted({1, 2, 3, 4}.difference((label_in1, label_in2)))))

        emb[v_sink] = [in1, in2, v_source, v_source]
        ori[v_sink] = [1, 1, 1, 1]
        emb[v_source] = [v_sink, v_sink, out1, out2]
        ori[v_source] = [-1, -1, -1, -1]

    return G

from collections import Counter

def hourglass(pos1,pos2,degree,edge_label=None):
    pos1 = vector(pos1)
    pos2 = vector(pos2)
    mid = (pos1+pos2)/2
    H = Graphics()


    if degree % 2 == 1:
        H += line([pos1,pos2], color="black")

    if degree == 1:
        if edge_label is not None:
            H += text(edge_label,mid,background_color='white')
        return H
    V = pos2-pos1
    Vortho = matrix([[0,1],[-1,0]])*V
    quater1 = 0.75*pos1+0.25*pos2
    quater2 = 0.25*pos1+0.75*pos2
    for i in range(degree//2):
        factor = (i+1.0)/(degree//2)
        path1 = [[tuple(pos1),tuple(quater1+Vortho/8*factor),tuple(mid)],[tuple(quater2-Vortho/8*factor),tuple(pos2)]]
        path2 = [[tuple(pos1),tuple(quater1-Vortho/8*factor),tuple(mid)],[tuple(quater2+Vortho/8*factor),tuple(pos2)]]
        H += bezier_path(path1, color="black")+bezier_path(path2, color="black")
    if edge_label is not None:
        H += text(edge_label,mid,background_color='white')

    return H

def plot_plabic(PG):
    pos = PG.get_pos()

    sources = []
    sinks = []

    for v in PG:

        if set(PG._ori[v]) == set([1]):
            sinks.append(v)
            continue
        if set(PG._ori[v]) == set([-1]):
            sources.append(v)
            continue
        assert False, f"Vertex {v} is neither a source or a sink"

    edges_with_multiplicities = Counter(PG.edges(sort=False))

    P = points([pos[v] for v in sinks], color="red", markeredgecolor="red", size=15)+points([pos[v] for v in sources], color="black", markeredgecolor="black", size=15)
    for e,m in edges_with_multiplicities.items():
        a, b, label = e
        P += hourglass(pos[a],pos[b], m, label)

    for v in PG:
        if type(v)==int:
            P += text(v,pos[v]*1.1)

    return P

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


def count_LOGs(T, m=None, filter_perm=True, first_only=False, verbose=False, output=True, plabic=False, edge_labels=True):
    '''Takes a standard tableau T and plots the labeled oriented graphs obtained from a random crossing graph.
       More generally allows T to be a signed balanced lattice word L with maximum possible letter m.
       Currently only works with m=4. If filter_perm is True, only prints graph orientations whose
       Trip_1 and Trip_2 match Prom_1 and Prom_2. If plabic=True, prints the (unlabled)
       plabic graph associated to each oriented graph instead.'''
    if m is not None:
        # Assume T is actually a lattice word
        L = T
    else:
        L = to_lattice_word(T)
        m = len(T)
    assert m==4
    M = middle_matching_L(L, m)
    G = random_crossing_graph(M)
    calculate_positions(G, 1.5)
    c=0
    for OG in graph_orientations(G, L, verbose=verbose):

#        plot_from_raw(OG)

        if filter_perm:
            if trip_perm(OG, 1) != prom_perm_L(L, m, 1):
                continue
        if not plabic:
            for LOG in oriented_graph_labelings(OG, L, verbose=verbose):
#                c += 2**(sum(1 for v in OG if  sum(OG._ori[v]) == 4) )
                c += 2**(sum(1 for v in OG if  abs(sum(OG._ori[v])) == 4) )
                if first_only: return
        else:
            for LOG in oriented_graph_labelings(OG, L, verbose=verbose):
                if output:
                    expanded = expand_to_plabic(LOG,edge_labels=edge_labels)
                    calculate_positions(expanded, 1.5)
                    plot_plabic(expanded).show(axes=False, aspect_ratio=1,figsize=(6,6))
                if first_only: return
    return c

def plot_LOGs(T, m=None, filter_perm=True, first_only=False, verbose=False, output=True, plabic=False, edge_labels=True):
    '''Takes a standard tableau T and plots the labeled oriented graphs obtained from a random crossing graph.
       More generally allows T to be a signed balanced lattice word L with maximum possible letter m.
       Currently only works with m=4. If filter_perm is True, only prints graph orientations whose
       Trip_1 and Trip_2 match Prom_1 and Prom_2. If plabic=True, prints the (unlabled)
       plabic graph associated to each oriented graph instead.'''
    if m is not None:
        # Assume T is actually a lattice word
        L = T
    else:
        L = to_lattice_word(T)
        m = len(T)
    assert m==4
    M = middle_matching_L(L, m)
    G = random_crossing_graph(M)
    calculate_positions(G, 1.5)
    for OG in graph_orientations(G, L, verbose=verbose):

#        plot_from_raw(OG)

        if filter_perm:
            if trip_perm(OG, 1) != prom_perm_L(L, m, 1):
                continue
        if not plabic:
            for LOG in oriented_graph_labelings(OG, L, verbose=verbose):
                if output: plot_from_raw(LOG, edge_labels=edge_labels)
                if first_only: return
        else:
            for LOG in oriented_graph_labelings(OG, L, verbose=verbose):
                if output:
                    expanded = expand_to_plabic(LOG,edge_labels=edge_labels)
                    calculate_positions(expanded, 1.5)
                    plot_plabic(expanded).show(axes=False, aspect_ratio=1,figsize=(6,6))
                if first_only: return

def orbit_graph(x, fs, fs_labels=None, multi_valued=False):
    '''Takes an object x and a list of functions fs which take x as a single argument.
       Creates a directed graph whose vertices are compositions of functions applied to x
       and whose edges are of the form (y, f, f(y)).'''
    if fs_labels==None:
        fs_labels = list(range(len(fs)))

    G = DiGraph()
    xs = [x]

    if not multi_valued:
        while len(xs) > 0:
            y = xs.pop()
            for i in range(len(fs)):
                z = fs[i](y)
                if z not in G.vertices():
                    xs.append(z)
                G.add_edge(y, z, fs_labels[i])
    else:
        while len(xs) > 0:
            y = xs.pop()
            for i in range(len(fs)):
                zs = fs[i](y)
                for z in zs:
                    if z not in G.vertices():
                        xs.append(z)
                    G.add_edge(y, z, fs_labels[i])
    return G

def create_local_move(X, Y):
    '''Returns a function which takes a signed list L and replaces every occurrence
       of X as a consecutive sublist with Y, returning an iterator of all such results (converted to tuples).'''
    def local_move(L):
        for i in occurrences(L, X):
            yield tuple(chain(L[:i], Y, L[i+len(X):]))
    return local_move

local_moves_orbits = (

# End caps

    ((( 1,-1),      ()),
     ((-4, 4),      ())),

# 12' -> 2'1 family

    ((( 1,-2),      (-2, 1)),
     (( 2,-1),      (-1, 2)),
     ((-3, 4),      ( 4,-3)),
     ((-4, 3),      ( 3,-4))),

# 22' -> 1'1 family

    ((( 2,-2),      (-1, 1)),
     ((-3, 3),      ( 4,-4))),

# 13' -> 3'1 witnessed family

    ((( 1,-3,-1),   (-3, 1,-1)),
     (( 1, 3,-1),   ( 1,-1, 3)),
     ((-4,-2, 4),   (-4, 4,-2)),
     ((-4, 2, 4),   ( 2,-4, 4))),
    ((( 1,-3, 2),   (-3, 1, 2)),
     ((-2, 3,-1),   (-2,-1, 3)),
     (( 3,-2, 4),   ( 3, 4,-2)),
     ((-4, 2,-3),   ( 2,-4,-3))),

# 23 -> 1'4' witnessed family

    ((( 2, 3,-1),   (-1,-4,-1)),
     (( 1,-3,-2),   ( 1, 4, 1)),
     ((-4, 2, 3),   (-4,-1,-4)),
     ((-3,-2, 4),   ( 4, 1, 4))),
    ((( 2, 3,-2),   (-1,-4,-2)),
     (( 2,-3,-2),   ( 2, 4, 1)),
     ((-3, 2, 3),   (-3,-1,-4)),
     ((-3,-2, 3),   ( 4, 1, 3))),
    ((( 2, 3,-3),   (-1,-4,-3)),
     (( 3,-3,-2),   ( 3, 4, 1)),
     ((-2, 2, 3),   (-2,-1,-4)),
     ((-3,-2, 2),   ( 4, 1, 2))),
    ((( 2, 3, 4),   (-1,-4, 4)),
     ((-4,-3,-2),   (-4, 4, 1)),
     (( 1, 2, 3),   ( 1,-1,-4)),
     ((-3,-2,-1),   ( 4, 1,-1))),

# 14 -> 41 witnessed family

#((1, 4),       (4, 1)),
#((-4, -1),     (-1, -4)),
    ((( 1, 4,-1),   ( 4, 1,-1)),
     (( 1,-4,-1),   ( 1,-1,-4)),
     ((-4, 1, 4),   (-4, 4, 1)),
     ((-4,-1, 4),   (-1,-4, 4))),
    ((( 1, 4, 2),   ( 4, 1, 2)),
     ((-2,-4,-1),   (-2,-1,-4)),
     (( 3, 1, 4),   ( 3, 4, 1)),
     ((-4,-1,-3),   (-1,-4,-3))),
    ((( 1, 4, 3),   ( 4, 1, 3)),
     ((-3,-4,-1),   (-3,-1,-4)),
     (( 2, 1, 4),   ( 2, 4, 1)),
     ((-4,-1,-2),   (-1,-4,-2))),
    ((( 1, 4, 4),   ( 4, 1, 4)),
     ((-4,-4,-1),   (-4,-1,-4)),
     (( 1, 1, 4),   ( 1, 4, 1)),
     ((-4,-1,-1),   (-1,-4,-1))),

# 12 -> 21 witnessed family

    ((( 1, 2,-1),   ( 2, 1,-1)),
     (( 1,-2,-1),   ( 1,-1,-2)),
     ((-4, 3, 4),   (-4, 4, 3)),
     ((-4,-3, 4),   (-3,-4, 4))),
    ((( 1, 2, 2),   ( 2, 1, 2)),
     ((-2,-2,-1),   (-2,-1,-2)),
     (( 3, 3, 4),   ( 3, 4, 3)),
     ((-4,-3,-3),   (-3,-4,-3))),

# 12 -> 3'4' witnessed family

    ((( 1, 2,-3),   (-3,-4,-3)),
     (( 3,-2,-1),   ( 3, 4, 3)),
     ((-2, 3, 4),   (-2,-1,-2)),
     ((-4,-3, 2),   ( 2, 1, 2))),
    ((( 1, 2, 4),   (-3,-4, 4)),
     ((-4,-2,-1),   (-4, 4, 3)),
     (( 1, 3, 4),   ( 1,-1,-2)),
     ((-4,-3,-1),   ( 2, 1,-1))),

# 13 -> 31 witnessed family

    ((( 1, 3,-1),   ( 3, 1,-1)),
     (( 1,-3,-1),   ( 1,-1,-3)),
     ((-4, 2, 4),   (-4, 4, 2)),
     ((-4,-2, 4),   (-2,-4, 4))),
    ((( 1, 3, 2),   ( 3, 1, 2)),
     ((-2,-3,-1),   (-2,-1,-3)),
     (( 3, 2, 4),   ( 3, 4, 2)),
     ((-4,-2,-3),   (-2,-4,-3))),
    ((( 1, 3, 3),   ( 3, 1, 3)),
     ((-3,-3,-1),   (-3,-1,-3)),
     (( 2, 2, 4),   ( 2, 4, 2)),
     ((-4,-2,-2),   (-2,-4,-2))),

# 13 -> 2'4' witnessed family

    ((( 1, 3,-2),   (-2,-4,-2)),
     (( 2,-3,-1),   ( 2, 4, 2)),
     ((-3, 2, 4),   (-3,-1,-3)),
     ((-4,-2, 3),   ( 3, 1, 3))),
    ((( 1, 3,-3),   (-2,-4,-3)),
     (( 3,-3,-1),   ( 3, 4, 2)),
     ((-2, 2, 4),   (-2,-1,-3)),
     ((-4,-2, 2),   ( 3, 1, 2))),
    ((( 1, 3, 4),   (-2,-4, 4)),
     ((-4,-3,-1),   (-4, 4, 2)),
     (( 1, 2, 4),   ( 1,-1,-3)),
     ((-4,-2,-1),   ( 3, 1,-1))),

# 14 -> 2'3' bi-witnessed family

    (((-3, 1, 4,-2),   (-3,-2,-3,-2)),
     (( 2,-4,-1, 3),   ( 2, 3, 2, 3))),

# 23 -> 32 bi-witnessed family

    ((( 2, 2, 3, 3),   ( 2, 3, 2, 3)),
     ((-3,-3,-2,-2),   (-3,-2,-3,-2))),

# 14 xy -> 41 yx adjacent descent family

    ((( 1, 4,-2,-1),   ( 4, 1,-1,-2)),
     (( 1, 2,-4,-1),   ( 2, 1,-1,-4)),
     ((-4,-3, 1, 4),   (-3,-4, 4, 1)),
     ((-4,-1, 3, 4),   (-1,-4, 4, 3))),
    ((( 1, 4,-3,-1),   ( 4, 1,-1,-3)),
     (( 1, 3,-4,-1),   ( 3, 1,-1,-4)),
     ((-4,-2, 1, 4),   (-2,-4, 4, 1)),
     ((-4,-1, 2, 4),   (-1,-4, 4, 2))),
    ((( 1, 4,-4,-1),   ( 4, 1,-1,-4)),
     ((-4,-1, 1, 4),   (-1,-4, 4, 1))),

)

local_moves_pairs = []
local_moves_names = []
local_moves = []
local_moves_orbits_names = []
def initialize_local_moves():
    global local_moves_pairs, local_moves_names, local_moves, local_moves_orbits_names
    local_moves_pairs = [p for _ in local_moves_orbits for p in _]

    local_moves = []
    local_moves_names = []
    for X, Y in local_moves_pairs:
        local_moves.append(create_local_move(X, Y))
        local_moves_names.append((X, Y))

    local_moves_orbits_names = []
    for local_moves_orbit in local_moves_orbits:
        local_moves_orbits_names.append(tuple(local_moves_orbit[0]))

initialize_local_moves()

def local_move_graph(L):
    G = orbit_graph(tuple(L), local_moves, fs_labels=local_moves_names, multi_valued=True)
    return G

def leaves(G):
    return [v for v in G.vertices() if G.out_degree(v) == 0]

def local_move_applies(L):
    '''Returns True if some local move applies to L, False otherwise.'''
    for f in local_moves:
        if any(True for _ in f(L)):
            return True
    return False

tilde_subs = {1:1, 2:2, 3:3, 4:4, -4:1, -3:2, -2:3, -1:4}
def tildify(L):
    return [tilde_subs[i] for i in L]

def ainv(L):
    T = tildify(L)
    return sum(1 for i in range(len(L)) for j in range(i+1, len(L)) if T[i] < T[j])

dim = 4

V = crystals.Tableaux(["A",dim-1],shapes=[[1]])
V_dual = crystals.Tableaux(["A",dim-1],shapes=[[1]*(dim-1)])

letters = {**dict(enumerate(V,1)), **dict(enumerate(V_dual,-dim))}

def tensor_crystal(signature):
    C = crystals.TensorProduct(*[V if s==1 else V_dual for s in signature[::-1]])
    return C

def topmost(word):
    signature = [sgn(l) for l in word]
    C = tensor_crystal(signature)
    crystal_word = C(*[letters[l] for l in word[::-1]])
    return crystal_word.to_highest_weight()

def bottommost(word):
    signature = [sgn(l) for l in word]
    C = tensor_crystal(signature)
    crystal_word = C(*[letters[l] for l in word[::-1]])
    return crystal_word.to_lowest_weight()

def upper_and_lower(word):
    signature = [sgn(l) for l in word]
    C = tensor_crystal(signature)
    crystal_word = C(*[letters[l] for l in word[::-1]])
    S_up = C.subcrystal(generators=[crystal_word], direction="upper")
    G_up = S_up.digraph()
    G_up.relabel(lambda s: new_label(s,word))

    S_down = C.subcrystal(generators=[crystal_word], direction="lower")
    G_down = S_down.digraph()
    G_down.relabel(lambda s: new_label(s,word))
    return G_up, G_down

def graph_containing(word):
    signature = [sgn(l) for l in word]
    C = tensor_crystal(signature)
    crystal_word = C(*[letters[l] for l in word[::-1]])
    S = C.subcrystal(generators=[crystal_word])
    G = S.digraph()
    G.relabel(lambda s: new_label(s,word))
    return G

def letter(weight):
    for i,s in enumerate(weight,1):
        if s!=0:
            return s*i

def letter_from_crystal_weight(weight):
    weight = list(weight.to_vector())
    if sum(weight)>1:
        weight = [e-1 for e in weight]
    return letter(weight)

def to_word(s):
    return [letter_from_crystal_weight(p.weight()) for p in s][::-1]

def lstr(l):
    """
    The latex string of a letter:
    """
    if l>0:
        return str(l)
    else:
        return "\\bar{}".format(-l)

def texword(w, math=False):
    if math:
        return "$"+"".join(map(lstr,w))+"$"
    return "".join(map(lstr,w))

def new_label(s,highlight=None):
    word = to_word(s.value)
    return tuple(word)
#    highlighter = "*" if word==highlight else ""
#    return LatexExpr(highlighter+texword(word))

def path_to_matrix_fragment(P):
    if type(P[0][0]) is tuple:
        hww = P[0][0]
    else:
        hww = P[0]
        P = []

    ret = []
    sigs = [1 if p > 0 else -1 for p in hww]
    vals = [abs(_) for _ in hww]
    for a, b, label in P:
        i = abs(e_diff(a, b))-1
        ret.append([[]]*len(a))
#        print(i, label+1, vals)
        if sigs[i] > 0:
            ret[-1][i] = list(range(vals[i]+1, label+1+1))
            vals[i] = label+1
        else:
            ret[-1][i] = list(range(label+1, vals[i]+1))
            vals[i] = label
    return ret

def paths_to_matrix_columns(PU, PL):
    # Empty paths are [v] rather than [(u, v, label), ...]
    if type(PU[0][0]) is tuple:
        hww = PU[0][0]
    else:
        hww = PU[0]
    if type(PL[0][0]) is tuple:
        lww = PL[-1][1]
    else:
        lww = PL[0]
    n = len(hww)

    top = list(reversed(path_to_matrix_fragment(PU)))

    upper_triangle = growth_matrix_L(hww, 4, signed=False)
    lower_triangle = growth_matrix_L(tau(lww), 4, signed=False)
    middle = [[upper_triangle[i][j] if i <= j else lower_triangle[n-1-i][n-1-j] for j in range(n)] for i in range(n)]

    bottom = list(reversed(path_to_matrix_fragment(PL)))

    return top + middle + bottom

def tau(L):
    '''Applies time reversal by reversing and negating a word.'''
    return [-_ for _ in reversed(L)]

def eps(L, k=4):
    '''Applies evacuation by reversing and complementing values of a word, preserving sign.'''
    return [sign(_)*(k+1 - abs(_)) for _ in reversed(L)]

def matrix_columns_to_proms(columns, offset):
    '''offset typically is the length of the upper path.'''
    proms = [dict() for i in range(4)]
    for i, row in enumerate(columns):
        for j, cell in enumerate(row):
            for k in cell:
                proms[(5-k)  % 4][j] = i-offset
    return proms

def danglers(L, i=None):
    '''Iterates over all possible tuples of promotion permutations as determined by the crystal magic.
       If i is from 0 to m-1, picks out only the ith promotion permutations.'''
    U, L = upper_and_lower(L)
    for UP in U.all_paths(U.sources()[0], U.sinks()[0], report_edges=True, labels=True):
        for LP in L.all_paths(L.sources()[0], L.sinks()[0], report_edges=True, labels=True):
            columns = paths_to_matrix_columns(UP, LP)
            if type(UP[0][0]) is tuple:
                offset = len(UP)
            else:
                offset = 0
            proms = matrix_columns_to_proms(columns, offset)
            if i is None:
                yield proms
            else:
                yield proms[i]

def is_a_crossing(a, b, c, d):
    '''Assumes a and b are an edge, and c and d are an edge.
       Determines if these edges form a crossing. Assumes a != b,
       c != d. If {a, b} = {c, d}, we declare it not to be a
       crossing by convention. If {a, b, c, d} are not distinct,
       errors.'''
    if a > b:
        a, b = b, a
    if c > d:
        c, d = d, c
    if a == c:
        if b != d:
            raise NotImplementedException()
        return False
    if a > c:
        a, b, c, d = c, d, a, b
    return c < b < d

def is_not_crossing(L, i, j):
    '''Determines if elements at index i and j in L where i<j always
       result in a dangling where the Prom_2 matching involving i and j
       does not have a crossing.'''
    for dangler in danglers(L):
        prom2 = dangler[2]
        if is_a_crossing(i, prom2[i], j, prom2[j]):
            return False
    return True

def cyclically_inc(L):
    '''Consider cyclically rotating the list L so that it begins with its minimum. Returns True if the result is
       weakly increasing, False otherwise.'''
    min_i = L.index(min(L))
    return all(L[i] <= L[i+1] for i in range(min_i - len(L), min_i - 1))

def cyclically_dec(L):
    max_i = L.index(max(L))
    return all(L[i] >= L[i+1] for i in range(max_i - len(L), max_i - 1))

def is_going_monotonic(L):
    '''Determines if all dangling permutations cyclically increase for positive elements of L
       and cyclically decrease for negative elements.'''
    for dangler in danglers(L):
        for i in range(len(L)):
            prom_ends = [prom[i] for prom in dangler]
            if L[i] > 0:
                if not cyclically_inc(prom_ends):
                    return False
            else:
                if not cyclically_dec(prom_ends):
                    return False
    return True

def isomorphic_path(P, f):
    if type(P[0][0]) is tuple:
        return [(f[a], f[b], label) for a, b, label in P]
    else:
        return [f[P[0]]]

def is_good_degeneration(L, Lp, plumbing, verbose=False):
    '''Determines whether the "crystal magic" proves a degeneration is always good.'''
    G = graph_containing(L)
    Gp = graph_containing(Lp)
    b,f = G.is_isomorphic(Gp, edge_labels=True, certificate=True)
    if not b: # Probably unnecessary...
        if verbose:
            print("Not isomorphic crystals")
        return False

    U, L = upper_and_lower(L)
    Up, Lp = upper_and_lower(Lp)
    bU, fU = U.is_isomorphic(Up, edge_labels=True, certificate=True)
    bL, fL = L.is_isomorphic(Lp, edge_labels=True, certificate=True)
    if not (bU and bL):
        if verbose:
            print("Not locally isomorphic crystals")
        return False

    for UP in U.all_paths(U.sources()[0], U.sinks()[0], report_edges=True, labels=True):
        for LP in L.all_paths(L.sources()[0], L.sinks()[0], report_edges=True, labels=True):
#            print(UP, LP)
            columns = paths_to_matrix_columns(UP, LP)
            columns_p = paths_to_matrix_columns(isomorphic_path(UP, fU), isomorphic_path(LP, fL))
#            m_pp(columns)
#            print("\n")
#            m_pp(columns_p)
            if type(UP[0][0]) is tuple:
                offset = len(UP)
            else:
                offset = 0
            proms = matrix_columns_to_proms(columns, offset)
            proms_p = matrix_columns_to_proms(columns_p, offset)

            for i in range(3):
                if not is_consistent(proms[i+1], proms_p[i+1], plumbing[i], verbose=verbose):
                    if verbose:
                        print("...fail path UP:", UP)
                        print("...fail path LP:", LP)
                        print("...fail path UP_p:", isomorphic_path(UP, fU))
                        print("...fail path LP_p:", isomorphic_path(LP, fL))
                        print("...fail proms:", proms)
                        print("...fail proms_p:", proms_p)
                    return False

    return True

def is_consistent(prom, prom_p, plumbing, verbose):
#    print("prom, prom_p, plumbing", prom, prom_p, plumbing)
    n = len(plumbing.keys())//2
    prom = {(k, 0, 0):(v if v < 0 or v >= n else (v, 1, 0)) for k,v in prom.items()}
    prom_p = {(k, 0, 1):(v if v < 0 or v >= n else (v, 1, 1)) for k,v in prom_p.items()}
    for k,v in plumbing.items():
        prom_p[k] = v

#    print("prom, prom_p", prom, prom_p)
    for i in range(n):
        # Go from (i, 0, 0) to a leaf
        cur = (i, 0, 0)
        while cur in prom_p:
            cur = prom_p[cur]
        if cur != prom[(i, 0, 0)]:
            if verbose:
                print("...failed at", i)
            return False

    return True

def plumbing_sum(*args):
    # Plumbings are listed left to right
    rets = [dict() for _ in range(3)]
    offset = 0
    for plumbing in args:
        for i in range(3):
            for (a, b, c), (x, y, z) in plumbing[i].items():
                rets[i][(a+offset, b, c)] = (x+offset, y, z)
        offset += len(plumbing[0].keys())/2
    return rets

def _plumbing_composite2(pi, sigma):
    n = len(sigma[0].keys())//2
    ret = [[]] * len(sigma)
    for i in range(len(sigma)):
        comp       = {(a, x, 2 if y==1 else y):(b, u, 2 if v==1 else v) for (a, x, y), (b, u, v) in sigma[i].items()}
        comp.update( {(a, x, 2 if y==0 else y):(b, u, 2 if v==0 else v) for (a, x, y), (b, u, v) in pi[i].items()} )
        ret_i = {}
        for a in range(n):
            cur = (a, 0, 0)
            while cur in comp:
                cur = comp[cur]
            ret_i[(a, 0, 0)] = cur
            cur = (a, 1, 1)
            while cur in comp:
                cur = comp[cur]
            ret_i[(a, 1, 1)] = cur
        ret[i] = ret_i
    return ret

import functools
def plumbing_composite(*args):
    # Plumbings are listed bottom to top. Must all have the same length.
    if len(args) == 0:
        raise NotImplementedError("Not implemented.")
    elif len(args) == 1:
        return args[0]
    return functools.reduce(_plumbing_composite2, args[1:], args[0])

# Length-preserving plumbing connectivities.
# Each encodes how trip permutations behave when some plumbing is added.
# Each is a list whose ith element represents Trip_i plumbing, for i=1, 2, 3.
# Specifically, the top and bottom vertices are each numbered 0, 1, ....
# Something like 2_i means an input at the 2nd vertex on top and is represented by
# (2, 1, 0). Something like 2_o' means an output (going down) at the second vertex on
# the bottom and is represented by (2, 0, 1). The i or o is a 1 or 0 in the 2nd coordinate
# and the prime or lack thereof is a 1 or 0 in the third coordinate.

bar = [
    {(0, 0, 0):(0, 0, 1),
     (0, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),
     (0, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),
     (0, 1, 1):(0, 1, 0)},
]

bowtie = [
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(1, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(1, 1, 0)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
]

# Two normal edges down to an internal vertex with a dangling hourglass edge
twist_pp_nn = [
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 0, 1),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(1, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(1, 1, 0)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 1, 0),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 0, 1)},
]

twist_nn_pp = [
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 1, 0),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 0, 1)},
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(1, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(1, 1, 0)},
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 0, 1),  (1, 1, 1):(0, 1, 0)},
]

X_pp_pp = [
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 0, 1),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 1, 0),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 0, 1)},
]

X_pp_nn = [
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(1, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(0, 0, 1)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(0, 1, 0),
     (0, 1, 1):(1, 0, 1),  (1, 1, 1):(1, 1, 0)},
]

X_nn_pp = [
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(0, 1, 0),
     (0, 1, 1):(1, 0, 1),  (1, 1, 1):(1, 1, 0)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(1, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(0, 0, 1)},
]

X_nn_nn = [
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 1, 0),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 0, 1)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 0, 1),  (1, 1, 1):(0, 1, 0)},
]

X_pn_np = [
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(1, 1, 0)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
]

X_np_pn = [
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(1, 1, 0)},
]

X_pp_pp_X_pp_pp = plumbing_sum(X_pp_pp, X_pp_pp) # done
X_pp_pp_X_nn_nn = plumbing_sum(X_pp_pp, X_nn_nn) # done
X_pp_pp_X_np_pn = plumbing_sum(X_pp_pp, X_np_pn) # done
X_pp_pp_X_pn_np = plumbing_sum(X_pp_pp, X_pn_np) # done
X_pp_pp_X_pp_nn = plumbing_sum(X_pp_pp, X_pp_nn) # done
X_pp_pp_X_nn_pp = plumbing_sum(X_pp_pp, X_nn_pp) # done

#X_nn_nn_X_pp_pp = plumbing_sum(X_nn_nn, X_pp_pp)
#X_nn_nn_X_nn_nn = plumbing_sum(X_nn_nn, X_nn_nn)
#X_nn_nn_X_np_pn = plumbing_sum(X_nn_nn, X_np_pn)
#X_nn_nn_X_pn_np = plumbing_sum(X_nn_nn, X_pn_np)
#X_nn_nn_X_pp_nn = plumbing_sum(X_nn_nn, X_pp_nn)
#X_nn_nn_X_nn_pp = plumbing_sum(X_nn_nn, X_nn_pp)

#X_np_pn_X_pp_pp = plumbing_sum(X_np_pn, X_pp_pp)
#X_np_pn_X_nn_nn = plumbing_sum(X_np_pn, X_nn_nn)
X_np_pn_X_np_pn = plumbing_sum(X_np_pn, X_np_pn) # done
X_np_pn_X_pn_np = plumbing_sum(X_np_pn, X_pn_np) # done
X_np_pn_X_pp_nn = plumbing_sum(X_np_pn, X_pp_nn) # done
X_np_pn_X_nn_pp = plumbing_sum(X_np_pn, X_nn_pp) # done

#X_pn_np_X_pp_pp = plumbing_sum(X_pn_np, X_pp_pp)
#X_pn_np_X_nn_nn = plumbing_sum(X_pn_np, X_nn_nn)
#X_pn_np_X_np_pn = plumbing_sum(X_pn_np, X_np_pn)
#X_pn_np_X_pn_np = plumbing_sum(X_pn_np, X_pn_np)
#X_pn_np_X_pp_nn = plumbing_sum(X_pn_np, X_pp_nn)
#X_pn_np_X_nn_pp = plumbing_sum(X_pn_np, X_nn_pp)

#X_pp_nn_X_pp_pp = plumbing_sum(X_pp_nn, X_pp_pp)
#X_pp_nn_X_nn_nn = plumbing_sum(X_pp_nn, X_nn_nn)
#X_pp_nn_X_np_pn = plumbing_sum(X_pp_nn, X_np_pn)
#X_pp_nn_X_pn_np = plumbing_sum(X_pp_nn, X_pn_np)
X_pp_nn_X_pp_nn = plumbing_sum(X_pp_nn, X_pp_nn) # done
X_pp_nn_X_nn_pp = plumbing_sum(X_pp_nn, X_nn_pp)

#X_nn_pp_X_pp_pp = plumbing_sum(X_nn_pp, X_pp_pp)
#X_nn_pp_X_nn_nn = plumbing_sum(X_nn_pp, X_nn_nn)
#X_nn_pp_X_np_pn = plumbing_sum(X_nn_pp, X_np_pn)
#X_nn_pp_X_pn_np = plumbing_sum(X_nn_pp, X_pn_np)
#X_nn_pp_X_pp_nn = plumbing_sum(X_nn_pp, X_pp_nn)
#X_nn_pp_X_nn_pp = plumbing_sum(X_nn_pp, X_nn_pp)

bar_X_pp_nn = plumbing_sum(bar, X_pp_nn)

bar_X_pp_nn_bar = plumbing_sum(bar, X_pp_nn, bar)

bar_X_pp_pp = plumbing_sum(bar, X_pp_pp)

bar_X_pp_pp_bar = plumbing_sum(bar, X_pp_pp, bar)

X_pn_np_bar = plumbing_sum(X_pn_np, bar)

bar_X_pn_np_bar = plumbing_sum(bar, X_pn_np, bar)

X_pp_nn_bar_bar = plumbing_sum(X_pp_nn, bar, bar)

X_pp_pp_bar_bar = plumbing_sum(X_pp_pp, bar, bar)

X_pn_np_bar_bar = plumbing_sum(X_pn_np, bar, bar)

X_slash_ppn_npp = [
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(1, 0, 1),  (2, 0, 0):(0, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(2, 0, 1),  (2, 1, 1):(2, 1, 0)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(0, 1, 0),  (2, 0, 0):(2, 0, 1),
     (0, 1, 1):(2, 1, 0),  (1, 1, 1):(1, 1, 0),  (2, 1, 1):(1, 0, 1)},
]

X_slash_ppn_nnn = [
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(2, 0, 1),  (2, 0, 0):(0, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(1, 0, 1)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(0, 1, 0),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(2, 1, 0),  (1, 1, 1):(2, 0, 1),  (2, 1, 1):(1, 1, 0)},
]

X_slash_ppp_npn = [
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(1, 0, 1),  (2, 0, 0):(2, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 0, 1)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(0, 1, 0),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(2, 0, 1),  (1, 1, 1):(1, 1, 0),  (2, 1, 1):(2, 1, 0)},
]

X_slash_npn_ppp = [
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(1, 0, 1),  (2, 0, 0):(0, 1, 0),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 0, 1),  (2, 1, 1):(2, 1, 0)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(2, 1, 0),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(2, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(1, 1, 0),  (2, 1, 1):(1, 0, 1)},
]

X_slash_npn_pnn = [
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(2, 0, 1),  (2, 0, 0):(0, 1, 0),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(1, 0, 1)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(2, 1, 0),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(2, 0, 1),  (2, 1, 1):(1, 1, 0)},
]

X_slash_npp_ppn = [
    {(0, 0, 0):(0, 0, 1),  (1, 0, 0):(1, 0, 1),  (2, 0, 0):(2, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(0, 1, 0),  (1, 1, 1):(1, 1, 0),  (2, 1, 1):(2, 1, 0)},
]

X_slash_nnn_npp = [
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 1, 0),  (2, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 0, 1),  (2, 1, 1):(2, 1, 0)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(2, 0, 1),
     (0, 1, 1):(2, 1, 0),  (1, 1, 1):(0, 1, 0),  (2, 1, 1):(1, 0, 1)},
]

X_slash_nnn_nnn = [
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 1, 0),  (2, 0, 0):(0, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(1, 0, 1)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(2, 1, 0),  (1, 1, 1):(2, 0, 1),  (2, 1, 1):(0, 1, 0)},
]

X_slash_nnp_npn = [
    {(0, 0, 0):(1, 0, 1),  (1, 0, 0):(0, 1, 0),  (2, 0, 0):(2, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 0, 1)},
    {(0, 0, 0):(2, 0, 1),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(1, 1, 0),  (1, 1, 1):(2, 1, 0),  (2, 1, 1):(0, 1, 0)},
    {(0, 0, 0):(1, 1, 0),  (1, 0, 0):(0, 0, 1),  (2, 0, 0):(1, 0, 1),
     (0, 1, 1):(2, 0, 1),  (1, 1, 1):(0, 1, 0),  (2, 1, 1):(2, 1, 0)},
]


def crossings(M):
    '''Given a PerfectMatching on [2m] as a list of pairs (a, b) with a < b,
       a k-fold crossing is a k-element set of pairs (a1, b1), ..., (ak, bk) such
       that a1 < a2 < ... < ak < b1 < b2 < ... bk. Returns the list of maximal
       k-fold crossings.

       The algorithm is as follows. First compute the 2-crossings directly. Form a graph
       whose vertices are matching arcs and whose edges are 2-crossings. One can check
       that k-fold crossings correpond precisely to k-cliques.

       sage: T = StandardTableau([[1, 3, 4], [2, 5, 8], [6, 7, 9], [10, 11, 12]])
       sage: crossings(middle_matching(T))
       [((1, 7), (2, 12)),
        ((1, 7), (3, 9), (5, 11)),
        ((3, 9), (8, 10)),
        ((5, 11), (4, 6))]
       '''
    return [tuple(_) for _ in Graph(M.crossings(), format='list_of_edges').cliques_maximal()]

def maxes(a, key=None):
    if key is None:
        key = lambda x: x

    a = iter(a)
    try:
        a0 = next(a)
        m, max_list = key(a0), [a0]
    except StopIteration:
        raise ValueError("maxes() arg is an empty sequence")

    for s in a:
        k = key(s)
        if k > m:
            m, max_list = k, [s]
        elif k == m:
            max_list.append(s)
    return m, max_list

def prom_order_L(L, m):
    pps = prom_perms_L(L, m)
    ord = 1
    si = Permutation(list(range(2, len(L)+1)) + [1])
    si_inv = si.inverse()
    pps_cur = [Permutation(_) for _ in pps]
#    print([_.cycle_string() for _ in pps_cur])
    while True:
        for i in range(m):
            pps_cur[i] = si_inv*pps_cur[i]*si
#        print([_.cycle_string() for _ in pps_cur])

        if all(pps[i] == pps_cur[i] for i in range(m)):
            return ord

        ord += 1