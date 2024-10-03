import math
from sage.all import Graph
from .vertex import Vertex
from .face import Face
from .idgenerator import ID

class HourglassPlabicGraph:
    '''Represents an hourglass plabic graph.'''
    def __init__(self, n=0):
        # dictionaries pairing IDs to vertices and faces
        self._inner_vertices = dict()
        self._boundary_vertices = dict()
        self._faces = dict()
        
        self.layout = 'circular'
        if n > 0: self.create_boundary(n)

    # Construction functions

    def create_boundary(self, n, r=10):
        r"""
        Creates n boundary vertices, labeled from 0 to n-1, and connects them with phantom edges.
        The vertices will be filled. This function can only be called on an empty graph.

        INPUT:
    
        - ``n`` -- integer; the number of boundary vertices to create.
        - ``r`` -- float; the radius of the boundary.

        EXAMPLES:
    
            sage: HPG = HourglassPlabicGraph()
            sage: HPG.create_boundary()
        """
        assert self.order() == 0, "Cannot call create_boundary on a non-empty graph."

        for i in range(0, n):
            id = str(i)
            self._boundary_vertices[id] = Vertex(id, r*math.sin((i+0.5)*2*math.pi/n), r*math.cos((i+0.5)*2*math.pi/n), True, True, id)

        for i in range(0, n-1):
            Vertex.create_hourglass_between(self._boundary_vertices[str(i)], self._boundary_vertices[str(i+1)], 0)
        hh = Vertex.create_hourglass_between(self._boundary_vertices[str(n-1)], self._boundary_vertices[str(0)], 0)

        inner_face = Face(ID.get_new_id("face"), hh)
        outer_face = Face(ID.get_new_id("face"), hh.twin())
        self._faces[inner_face.id] = inner_face
        self._faces[outer_face.id] = outer_face
                          
    def create_vertex(self, v_id, x, y, filled, boundary=False, label='', verify_id=False):
        ''' Adds a vertex to the graph.
            v_id: The id given to the vertex. Should be unique.
            label: 
            x: The x position of the vertex
            y: The y position of the vertex
            filled: Whether the vertex is to be filled or not.
            boundary: Whether the vertex is on the boundary. Defaults to False.
            verify_id: Check whether v_id is already in use. Defaults to False.
            '''
        if verify_id and ((not boundary and v_id in self._inner_vertices) or (boundary and v_id in self._boundary_vertices)): raise ValueError("v_id already in use.")

        vertex = Vertex(v_id, x, y, filled, boundary, label)
        if boundary: self._boundary_vertices[v_id] = vertex
        else: self._inner_vertices[v_id] = vertex

    def remove_vertex_by_id(self, v_id):
        del_vertex = self._get_vertex(v_id)
        self.remove_vertex(del_vertex)

    def remove_vertex(self, del_vertex):
        # Store hourglasses in a list to avoid issues with removing
        # elements while iterating over dihedral element
        del_hourglasses = del_vertex.get_hourglasses_as_list()
        for hh in del_hourglasses:
            self._remove_hourglass_internal(hh, del_vertex, hh.v_to())
        
        if del_vertex.id in self._inner_vertices: del self._inner_vertices[del_vertex.id]
        else: del self._boundary_vertices[del_vertex.id]

    def create_hourglass_by_id(self, v1_id, v2_id, multiplicity=1):
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)

        self.create_hourglass(v1, v2, multiplicity)

    def create_hourglass(self, v1, v2, multiplicity=1):
        new_hh = Vertex.create_hourglass_between(v1, v2, multiplicity)

        # Create faces

        face = None
        # First, find an already existing reference to this hourglass's right face
        # There is a chance we are connecting two faces, so we should find the second one
        # and remove it from our list
        for hh in new_hh.iterate_right_turns():
            if hh.right_face is not None:
                if face is None: face = hh.right_face
                elif face is not hh.right_face:
                    del self._faces[hh.right_face.id]
                    break
        if face is not None:
            face.initialize_half_hourglasses(new_hh)
        # If none exists, create a new one
        else: 
            face = Face(ID.get_new_id("face"), new_hh)
            self._faces[face.id] = face

        # Either the twin's face will be the same as this, or we will need to create a new face since the old face
        # will be the same as the one reused for the hourglass and will no longer be valid
        if new_hh.twin().right_face is None:
            face = Face(ID.get_new_id("face"), new_hh.twin())
            self._faces[face.id] = face
        
    def remove_hourglass_by_id(self, v1_id, v2_id):
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)
        self.remove_hourglass(v1, v2)

    def remove_hourglass(self, v1, v2):
        self._remove_hourglass_internal(self._get_hourglass(v1, v2), v1, v2)

    def _remove_hourglass_internal(self, del_hh, v1, v2):
        face1 = None
        hh1 = None
        face2 = None
        hh2 = None
        # get a new hourglass for each face the hourglass belongs to
        for hh in del_hh.iterate_right_turns():
            if hh is not del_hh and hh is not del_hh.twin() and hh.right_face is not None:
                face1 = hh.right_face
                hh1 = hh
                break
        for hh in del_hh.twin().iterate_right_turns():
            if hh is not del_hh and hh is not del_hh.twin() and hh.right_face is not None:
                face2 = hh.right_face
                hh2 = hh
                break
        
        Vertex.remove_hourglass_between(v1, v2)

        if face1 is not None:
            face1.initialize_half_hourglasses(hh1)
        if face2 is not None:
            if face2 is not face1:
                del self._faces[face2.id]
            # This should only happen if deletion results in seperate subgraphs
            # This check avoids creating a new face for an isolated vertex
            elif not (del_hh.right_turn() is del_hh.twin() or del_hh.twin().right_turn() is del_hh):
                face2 = Face(ID.get_new_id("face"), hh2)
                self._faces[face2.id] = face2
        # case: this is the last hourglass of the face
        if face1 is None and face2 is None:
            del self._faces[del_hh.right_face.id]

    def thicken_hourglass_by_id(self, v1_id, v2_id):
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)
        self.thicken_hourglass(v1, v2)
    def add_strand_by_id(self, v1_id, v2_id): # alias
        self.thicken_hourglass_by_id(v1_id, v2_id)

    def thicken_hourglass(self, v1, v2):
        self._get_hourglass(v1, v2).thicken()
    def add_strand(self, v1, v2): # alias
        self.thicken_hourglass(v1, v2)
        
    def thin_hourglass_by_id(self, v1_id, v2_id):
        v1 = self._get_vertex(v1_id)
        v2 = self._get_vertex(v2_id)
        self.thin_hourglass(v1, v2)
    def remove_strand_by_id(self, v1_id, v2_id): # alias
        self.thin_hourglass_by_id(v1_id, v2_id)

    def thin_hourglass(self, v1, v2):
        self._get_hourglass(v1, v2).thin()
    def remove_strand(self, v1, v2): # alias
        self.thin_hourglass(v1, v2)
    
    # Moves

    def is_square_move_valid(self, face_id):
        return self._get_face(face_id).is_square_move_valid()

    def is_benzene_move_valid(self, face_id):
        return self._get_face(face_id).is_benzene_move_valid()

    def square_move(self, face_id):
        face = self._get_face(face_id)
        # A square move does not add or remove any faces, but faces adjacent faces
        # should have their hourglass heads set to hourglasses that are guaranteed
        # to persist.
        # Note that hh will have face as its right face.
        for hh in face:
            hh.left_face._half_hourglasses_head = hh.twin()
        
        tup = face.square_move()
        # Returned tuple is (new_vertices, removed_vertices)
        # NOTE: By assumption, all vertices involved in a square move are inner vertices
        for v in tup[0]:
            self._inner_vertices[v.id] = v
        for v in tup[1]:
            del self._inner_vertices[v.id]

    def benzene_move(self, face_id):
        self._get_face(face_id).benzene_move()

    # Checks

    def is_r_valent(self, r=4):
        for v in self._inner_vertices.values():
            if v.total_degree() != r: 
                print("vertex " + str(v.id) + " does not have degree " + str(r) + ". Instead, degree is " + str(v.total_degree()))
                return False
        return True

    def is_fully_reduced(self, r=4):
        '''
        The conditions for being fully reduced:
        - r-valent
        - Trips should have no self-intersections
        - No trip_i should have an essential double crossing with another trip_i
        - No trip_i should have an essential double crossing with trip_i+1 starting from the same vertex
        An essential double crossing occurs when two paths intersect (cross rather than reflect) twice 
        while travelling in the same direction.
        Ignore starting/ending vertices and consecutive intersections.
        '''

        # Verify r-valence
        if (not self.is_r_valent(r)): 
            print("Graph is not r-valent.") # TESTING
            return False

        trips = [[self.get_trip(v, i, 'half_hourglasses') for v in self._boundary_vertices.values()] for i in range(1, r)]

        # Returns true if trip does not intersect with itself.
        def validate_no_self_intersections(trip):
            vertices = { trip[0].v_from() }
            for hh in trip:
                if hh.v_to() in vertices: 
                    return False
                vertices.add(hh.v_to())
            return True

        # Verify no self-intersections
        count = 0 # TESTING
        for trip_is in trips:
            count += 1 # TESTING
            for trip in trip_is: 
                if not validate_no_self_intersections(trip):
                    print("trip" + str(count) + " from vertex " + str(trip[0].v_from().id) + " self-intersects.") # TESTING
                    return False

        # Internal helper functions for double crossing checks
        
        # Returns an integer.
        # If the resulting crossing is valid - that is, the 
        # orientations of the hourglasses going in and out 
        # of the crossing genuinely intersect - returns the 
        # number of shared vertices along the trips. Otherwise,
        # returns -1.
        def validate_crossing(trip1, ind1, trip2, ind2):
            # Keep track of ingoing hourglasses
            in_ind1 = ind1
            in_ind2 = ind2
            out_ind1 = ind1
            out_ind2 = ind2
            count = 0

            # Trace the shared trip intil it diverges
            while (out_ind1 < len(trip1) and out_ind2 < len(trip2)
                   and trip1[out_ind1].v_to() is trip2[out_ind2].v_to()):
                out_ind1 += 1
                out_ind2 += 1
                count += 1

            # If the crossing begins or ends at the boundary, we can assume it is valid.
            if in_ind1 == 0 or out_ind1 == len(trip1): return count

            inhh1 = trip1[in_ind1].twin()
            inhh2 = trip2[in_ind2].twin()
            outhh1 = trip1[out_ind1]
            outhh2 = trip2[out_ind2]

            # Validate crossing orientation
            # Case 1: Crossing is immediate
            # Verify that the order of hourglasses around the vertex
            # alternates between trip1 and trip2.
            if (count == 1):
                for hh in inhh1.iterate_clockwise():
                    if hh is outhh1: return -1
                    elif hh is inhh2 or outhh2: break
                for hh in inhh1.iterate_counterclockwise():
                    if hh is outhh1: return -1
                    elif hh is inhh2 or outhh2: return count
                # this should never be reached in a well-formed graph
                raise Exception("Issue with crossing validation. Hourglasses do not belong to same vertex.")
                
            # Case 2: Some shared edges along crossing
            # verify that that either the trip2 hourglasses
            # or the shared hourglasses are first in clockwise
            # order from the trip1 hourglasses
            else:
                inhh_shared = trip1[in_ind1+1]
                outhh_shared = trip1[out_ind1-1].twin()

                encounter_first = None
                encounter_second = None
                for hh in inhh1.iterate_clockwise():
                    if hh is inhh_shared:
                        encounter_first = outhh_shared
                        encounter_second = outhh2
                        break
                    elif hh is inhh2:
                        encounter_first = outhh2
                        encounter_second = outhh_shared
                        break
                for hh in outhh1.iterate_clockwise():
                    if hh is encounter_first: return count
                    elif hh is encounter_second: return -1
                # this should never be reached in a well-formed graph
                raise Exception("Issue with crossing validation. Hourglasses do not belong to same vertex.")

        # Finds the first crossing between trip1 and trip2
        # starting at the hourglasses indicated by ind1 and ind2.
        # If a crossing is found, returns the indices of the
        # outgoing hourglasses for each trip in a tuple.
        # If no crossing is found, returns None.
        def find_crossing_from(trip1, ind1, trip2, ind2):
            for i1 in range(ind1, len(trip1) - 1):
                for i2 in range(ind2, len(trip2) - 1):                        
                    # We only care if we see an intersection
                    if trip1[i1].v_to() is not trip2[i2].v_to(): continue
                    
                    count = validate_crossing(trip1, i1, trip2, i2)
                    # Because there are no self intersections, if we encounter
                    # a potential self intersection on trip1's hourglass but it
                    # fails, we won't encounter another one for that hourglass.
                    if count == -1: break
                    return (i1 + count, i2 + count)
            return None

        def do_trips_double_cross(trip1, trip2):
            next_inds = find_crossing_from(trip1, 0, trip2, 0)
            if next_inds is None: return False
            final_inds = find_crossing_from(trip1, next_inds[0], trip2, next_inds[1])
            return (final_inds is not None)

        # Validate no double crossings
        for i in range(0, len(trips)):
            trip_is = trips[i]
            all_compare_trips = trips[i] + (trips[i+1] if i < len(trips)-1 else [])
            for a in range(0, len(trip_is)):
                trip1 = trip_is[a]
                for b in range(a+1, len(all_compare_trips)):
                    trip2 = all_compare_trips[b]
                    if (do_trips_double_cross(trip1, trip2)):
                        print("trip" + str(i+1) + " from vertex " + str(trip1[0].v_from().id) # TESTING
                              + " and trip" + (str(i+1) if b < len(trip_is) else str(i+2)) + " from vertex " + str(trip2[0].v_from().id) + " double cross.") # TESTING
                        return False

        return True
    
    # Layout functions
    
    def make_circular(self, r=10):
        n = len(self._boundary_vertices.values())
        for i,v in self._boundary_vertices:
            v.x = r*math.sin((i+0.5)*2*math.pi/n)
            v.y = r*math.cos((i+0.5)*2*math.pi/n)
            
        self.tutte_layout()
        self.layout = "circular"

    def tutte_layout(self, error=0.01, max_iter = 1000):
        '''from https://cs.brown.edu/people/rtamassi/gdhandbook/chapters/force-directed.pdf.'''
        for i in range(max_iter):
            err = 0
            for v in self._inner_vertices:
                neighbours = v.get_neighbors()
                x_new = sum(w.x for w in neighbours)/len(neighbours)
                y_new = sum(w.y for w in neighbours)/len(neighbours)
                err += (v.x-x_new)**2 + (v.y-y_new)**2
                v.x, v.y = x_new, y_new
            if err < error:
                break

    # Trip functions

    def get_trip(self, vertex, i, output='half_strands'):
        ''' vertex: the initial boundary Vertex; assumes multiplicity 1
            i: computes trip_i by taking the ith left at unfilled/ith right at filled
            output: if output = 'half_strands', returns an array of HalfStrands. Otherwise, returns HalfHourglasses.

            Returns the list of HalfHourglasses/HalfStrands the trip visits in order.'''

        assert vertex.boundary, "Vertex should be on the boundary."
        assert vertex.total_degree() == 1, "Total degree of vertex should be 1. Instead is " + str(vertex.total_degree())
        
        return vertex.get_trip(i, output)

    def get_trip_perm(self, i, output='half_strands'):
        ''' Computes the ith trip permutation.
            The trip i permutation is generated by finding where trip i sends each boundary vertex to.
            Boundary vertices are assumed to be numbered 1, 2, ..., n CW starting slightly east of due north.'''
        perm = []
        for vertex in self._boundary_vertices.values():
            trip = vertex.get_trip(i, output)
            final_vertex = trip[-1].v_to()
            perm.append(final_vertex.id)
        return perm

    def get_trip_perms(self, output='half_strands'):
        '''Returns a list [t_1, ..., t_{r-1}] where t_i is the ith trip permutation
           and r is the maximum degree of an internal vertex.'''
        r = max(v.total_degree() for v in self._inner_vertices.values()) # This is quite inefficient, could be a cached value provided by user?
        return [self.get_trip_perm(i, output) for i in range(1, r)]

    # Internal accessors

    def _get_face(self, f_id):
        face = self._faces.get(f_id)
        if face is None: raise ValueError("id " + str(f_id) + " does not correspond to any face.")
        return face
        
    def _get_vertex(self, v_id):
        ''' Internal helper function that gets the vertex with the given id from either _inner_vertices or _boundary_vertices, and throws if the id is not found.'''
        v = self._inner_vertices.get(v_id)
        if v is None: 
            v = self._boundary_vertices.get(v_id)
            if v is None: raise ValueError("id " + str(v_id) + " does not correspond to any vertex.")
        return v

    def _get_hourglass_by_id(self, v1_id, v2_id):
        return self._get_hourglass(self._get_vertex(v1_id), self._get_vertex(v2_id))
    def _get_hourglass(self, v1, v2):
        return v1.get_hourglass_to(v2)

    def order(self):
        ''' The number of vertices in this graph.'''
        return len(self._inner_vertices) + len(self._boundary_vertices)

    def print_faces(self):
        for f in self._faces.values():
            print(f.id + ":")
            f.print_vertices()

    # Serialization/Data Conversion

    def to_graph(self, hourglass_labels=False): # TODO: VERIFY/TEST
        '''Creates an equivalent sagemath Graph. Represents strands in an hourglass in the label.'''
        vertex_refs = list(self._inner_vertices.values()) + list(self._boundary_vertices.values())
        edge_refs = set()
        for v in vertex_refs:
            for hh in v:
                if not hh.twin() in edge_refs:
                    edge_refs.add(hh)

        vertices = [v.id for v in vertex_refs]
        edges = [(h.v_from().id, h.v_to().id, h.label if hourglass_labels else h.strand_count()) for h in edge_refs]
        pos = {v.id:(v.x,v.y) for v in vertex_refs}
        g = Graph([vertices, edges], format='vertices_and_edges', pos=pos)
        return g

    # Update with **kwds argument?
    def plot(self):
        vertex_refs = list(self._inner_vertices.values()) + list(self._boundary_vertices.values())
        vertex_colors = {"gray":[v.id for v in vertex_refs if v.filled],  "white":[v.id for v in vertex_refs if not v.filled]}
        return self.to_graph().plot(vertex_colors=vertex_colors, edge_labels=True)

    @classmethod
    def from_dict(cls, data):
        '''Constructs a new hourglass plabic graph from a dictionary representing
        a JSON encoding of the graph.'''
        HPG = cls()

        if 'layout' in data: HPG.layout = data['layout']

        # prepare internal data for graph
        for v_data in data['vertices']:
            label = v_data['label'] if 'label' in v_data else ''
            HPG.create_vertex(v_data['id'], v_data['x'], v_data['y'], v_data['filled'], v_data['boundary'], label)

        for e in data['edges']:
            label = e['label'] if 'label' in e else ''
            HPG.create_hourglass_by_id(e['sourceId'], e['targetId'], e['multiplicity']) # Use label?
            
         # add boundary edges
        sorted_boundary_vertices = list(HPG._boundary_vertices.values())
        if HPG.layout == 'circular':
            sorted_boundary_vertices.sort(key = lambda v: math.atan2(-v.x, -v.y)) # cw orientation
        elif HPG.layout == 'linear':
            sorted_boundary_vertices.sort(key = lambda v: v.x) # left to right
        else:
            raise NotImplementedError("Layout must be circular or linear.")
        for i in range(0, len(sorted_boundary_vertices)):
            v_from = sorted_boundary_vertices[i]
            v_to   = sorted_boundary_vertices[(i+1)%len(sorted_boundary_vertices)]
            HPG.create_hourglass(v_from, v_to, 0)

        return HPG

    def to_dict(self):
        '''Encode this HourglassPlabicGraph as a dictionary representing
           a JSON encoding of the graph.'''
        vertices = list(self._inner_vertices.values()) + list(self._boundary_vertices.values())
        edges = set()
        for v in vertices:
            for hh in v:
                # do not record boundary edges
                if not (hh.is_boundary() or hh.twin() in edges):
                    edges.add(hh)
        
        d = {
            'edges': [{
                "multiplicity": e.multiplicity(),
                "sourceId": e.v_from().id,
                "targetId": e.v_to().id,
                "label": e.label,
                } for e in edges],
            'vertices': [{
                "id": v.id,
                "x": float(v.x),
                "y": float(v.y),
                "filled": v.filled,
                "boundary": v.boundary,
                "label": v.label,
                } for v in vertices],
            'layout': self.layout,
        }
        return d