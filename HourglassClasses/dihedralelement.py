class DihedralElement:
    ''' Base class for half hourglasses and half strands.
        Has a twin, cw_next, and ccw_next.
        Twin must be set by the inherited class.
        Functionally acts as a circular, doubly linked list.'''
    def __init__(self):
        self._twin = None
        self._cw_next = self
        self._ccw_next = self

    # List modification functions
    
    def insert_cw_next(self, element):
        '''Inserts element into the list as the clockwise next element.'''
        element._ccw_next = self
        element._cw_next = self._cw_next
        self._cw_next._ccw_next = element
        self._cw_next = element
    def insert_ccw_prev(self, element): # alias
        self.insert_cw_next(element)
    def append_ccw(self, element): # alias
        self.insert_cw_next(element)

    def insert_ccw_next(self, element):
        '''Inserts element into the list as the counterclockwise next element.'''
        element._cw_next = self
        element._ccw_next = self._ccw_next
        self._ccw_next._cw_next = element
        self._ccw_next = element
    def insert_cw_prev(self, element): # alias
        self.insert_ccw_next(element)
    def append_cw(self, element): # alias
        self.insert_ccw_next(element)

    def remove(self):
        '''Removes itself from the list. Also makes itself into a 1-element list for the purposes of consistency and reference counting.'''
        self._cw_next._ccw_next = self._ccw_next
        self._ccw_next._cw_next = self._cw_next
        self._cw_next = self
        self._ccw_next = self

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

    def get_ith_cw_element(self, i):
        return self if i == 0 else self._cw_next.get_ith_cw_element(i-1)

    def get_ith_ccw_element(self, i):
        return self if i == 0 else self._ccw_next.get_ith_ccw_element(i-1)

    # CW/CCW next modifiers. Use insert functions instead if possible.def cw_next(self):
    
    def set_cw_next(self, element):
        self._cw_next = element
        element._ccw_next = self
    def set_ccw_prev(self, element): # alias
        self.set_cw_next(element)

    def set_ccw_next(self, element):
        self._ccw_next = element
        element._cw_next = self
    def set_cw_prev(self, element): # alias
        self.set_ccw_next(element)

    # List data functions

    def get_num_elements(self):
        '''Returns the number of elements in the linked list.'''
        count = 1
        iter = self._cw_next
        while(iter != self):
            count += 1
            iter = iter._cw_next
        return count

    def get_elements_as_list(self, clockwise=True):
        ''' Returns the elements in an list.
            clockwise: The list will be in clockwise order. Otherwise it will be in counterclockwise order. Defaults to True.'''
        list = [self]
        iter = self._cw_next if clockwise else self._ccw_next
        while(iter != self):
            list.append(iter)
            iter = iter._cw_next if clockwise else iter._ccw_next
        return list