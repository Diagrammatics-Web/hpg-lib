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
    def insert_ccw_prev(self, element): # alias
        self.insert_cw_next(element)
    def append_ccw(self, element): # alias
        self.insert_cw_next(element)

    def insert_ccw_next(self, element):
        '''Inserts element into the list as the next counterclockwise element.'''
        element._cw_next = self
        element._ccw_next = self._ccw_next
        self._ccw_next._cw_next = element
        self._ccw_next = element
    def insert_cw_prev(self, element): # alias
        self.insert_ccw_next(element)
    def append_cw(self, element): # alias
        self.insert_ccw_next(element)

    def remove(self):
        ''' Removes itself from the list.
            Once removed, this element is assumed deleted
            and should not be used further.'''
        self._cw_next._ccw_next = self._ccw_next
        self._ccw_next._cw_next = self._cw_next
        self._cw_next = None
        self._ccw_next = None

    # Accessor functions
    
    def cw_next(self):
        return self._cw_next
    def ccw_prev(self): # alias
        return self.cw_next()
    def ccw_last(self): # alias
        return self.cw_next()

    def ccw_next(self):
        return self._ccw_next
    def cw_prev(self): # alias
        return self.ccw_next()
    def cw_last(self): # alias
        return self.ccw_next()

    def twin(self):
        '''Returns an object of the same type representing movement in the opposite direction.'''
        return self._twin

    def get_cw_ith_element(self, i):
        ''' Returns the element i elements clockwise.
            This corresponds to the ith left from this element's twin.
            i: how many elements to travel. Relates to trip i.'''
        return self._cw_next if i == 1 else self._cw_next.get_cw_ith_element(i-1)

    def get_ccw_ith_element(self, i):
        ''' Returns the element i elements counterclockwise.
            This corresponds to the ith right from this element's twin.
            i: how many elements to travel. Relates to trip i.'''
        return self._ccw_next if i == 1 else self._ccw_next.get_ccw_ith_element(i-1)

    # Directly connects two elements. Use insert functions instead if possible.
    
    def link_cw_next(self, element):
        self._cw_next = element
        element._ccw_next = self
    def link_ccw_prev(self, element): # alias
        self.link_cw_next(element)

    def link_ccw_next(self, element):
        self._ccw_next = element
        element._cw_next = self
    def link_cw_prev(self, element): # alias
        self.link_ccw_next(element)

    # List data functions

    def get_num_elements(self):
        '''Returns the number of elements in the linked list.'''
        count = 0
        for element in self.iterate_clockwise(): count += 1
        return count

    def get_elements_as_list(self, clockwise=True):
        ''' Returns the elements in a list.
            clockwise: The list will be in clockwise order. Otherwise it will be in counterclockwise order. Defaults to True.'''
        if clockwise: return [element for element in self.iterate_clockwise()]
        else: [element for element in self.iterate_counterclockwise()]

    def iterate_clockwise(self):
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
        if self.iter == self.head:
            if self.begin: raise StopIteration
            else: self.begin = True
        if self.clockwise:
            self.iter = self.iter.cw_next()
            return self.iter.cw_prev()
        else:
            self.iter = self.iter.ccw_next()
            return self.iter.ccw_prev()
        