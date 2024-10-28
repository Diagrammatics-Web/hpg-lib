class DihedralElement:
    ''' Base class for half hourglasses and half strands.
        Has a twin, cw_next, and ccw_next.
        Twin must be set by the inherited class.
        Acts as a circular, doubly linked list where each element links to another such list.'''
    def __init__(self, id):
        self.id = id
        self._twin = None
        self._cw_next = self
        self._ccw_next = self

    # List modification functions
    
    def insert_cw_next(self, element):
        '''Inserts element into the list as the next clockwise element.'''
        element._ccw_next = self
        element._cw_next = self._cw_next
        self._cw_next._ccw_next = element
        self._cw_next = element
    insert_ccw_prev = insert_cw_next # alias
    append_ccw = insert_cw_next # alias

    def insert_ccw_next(self, element):
        '''Inserts element into the list as the next counterclockwise element.'''
        element._cw_next = self
        element._ccw_next = self._ccw_next
        self._ccw_next._cw_next = element
        self._ccw_next = element
    insert_cw_prev = insert_ccw_next # alias
    append_cw = insert_ccw_next # alias

    def remove(self):
        ''' Removes itself from the list.
            This element will also become its own list to facilitate reuse.'''
        self._cw_next._ccw_next = self._ccw_next
        self._ccw_next._cw_next = self._cw_next
        self._cw_next = self
        self._ccw_next = self

    # Accessor functions
    
    def cw_next(self):
        return self._cw_next
    ccw_prev = cw_next # alias
    ccw_last = cw_next # alias

    def ccw_next(self):
        return self._ccw_next
    cw_prev = ccw_next # alias
    cw_last = ccw_next # alias

    def twin(self):
        '''Returns an object of the same type representing movement in the opposite direction.'''
        return self._twin
        
    def get_cw_ith_element(self, i):
        ''' Returns the element i elements clockwise.
            i: how many elements to travel. Assumed to be an integer >= 1.'''
        print("get_cw_ith_element(", i, ") called on ", self) # TESTING
        e = self
        while i > 0:
            e = e.cw_next()
            i -= 1
        return e

    def get_ccw_ith_element(self, i):
        ''' Returns the element i elements counterclockwise.
            i: how many elements to travel. Assumed to be an integer >= 1.'''
        print("get_ccw_ith_element(", i, ") called on ", self) # TESTING
        e = self
        while i > 0:
            e = e.ccw_next()
            i -= 1
        return e

    # Turn functions
    
    def left_turn(self):
        return self.twin().cw_next()
    def right_turn(self):
        return self.twin().ccw_next()

    def get_ith_left(self, i):
        print("get_ith_left(", i, ") called on ", self) # TESTING
        return self.twin().get_cw_ith_element(i)
    def get_ith_right(self, i):
        print("get_ith_right(", i, ") called on ", self) # TESTING
        return self.twin().get_ccw_ith_element(i)

    # Directly connects two elements. Use insert functions instead if possible.
    
    def link_cw_next(self, element):
        self._cw_next = element
        element._ccw_next = self
    link_ccw_prev = link_cw_next # alias

    def link_ccw_next(self, element):
        self._ccw_next = element
        element._cw_next = self
    link_cw_prev = link_ccw_next # alias

    # List data functions

    def get_num_elements(self):
        '''Returns the number of elements in the linked list.'''
        count = 0
        for element in self: count += 1
        return count

    def get_elements_as_list(self, clockwise=True):
        ''' Returns the elements in a list.
            clockwise: The list will be in clockwise order. Otherwise it will be in counterclockwise order. Defaults to True.'''
        if clockwise: return [element for element in self.iterate_clockwise()]
        else: [element for element in self.iterate_counterclockwise()]

    def __iter__(self): # by default, iteration will go clockwise
        return _DihedralIterator(self, True)
    
    def iterate_clockwise(self): # for specificity, if it's important
        return _DihedralIterator(self, True)

    def iterate_counterclockwise(self):
        return _DihedralIterator(self, False)

class _DihedralIterator:
    ''' Internal class for iterating over dihedral elements. Iteration can be specified to occur in clockwise or counterclockwise order.
        Modification of the list while iterating can cause errors with iteration.'''
    def __init__(self, head, clockwise): 
        self.head = head
        self.iter = head
        self.begin = False
        self.clockwise = clockwise
        
    def __iter__(self):
        return self
        
    def __next__(self):
        if self.iter is self.head:
            if self.begin: raise StopIteration
            else: self.begin = True
                
        old = self.iter
        self.iter = self.iter.cw_next() if self.clockwise else self.iter.ccw_next()
        return old
        