r"""
Abstract class for half hourglasses and half strands.

Enables efficient access and modification of edges in embedded planar graphs such as HourglassPlabicGraphs.

AUTHORS:

- Stefano L. Corno (2024-05-10): initial version

"""

# ****************************************************************************
#       Copyright (C) 2024 Stefano Corno <stlecorno@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

class DihedralElement:
    r"""
    Abstract class for half hourglasses and half strands.
    Has a twin, cw_next, and ccw_next.
    cw_next and ccw_next are always assumed to be defined; if this is the only element in the list,
    these should point to itself.
    twin must be set and managed by the inherited class (see :func: DihedralElement.twin()).
    Acts as a circular, doubly linked list where each element links to another such list.
    """
    
    def __init__(self, id):
        r"""
        Constructs a DihedralElement with the given ID.

        INPUT:

        - `id` -- hashable, unique object

        OUTPUT: DihedralElement; the constructed DihedralElement.

        .. WARNING::

            This class is intended to be abstract and should not be used directly.
        """
        self.id = id
        self._twin = None
        self._cw_next = self
        self._ccw_next = self

    # List modification functions
    
    def insert_cw_next(self, element):
        r"""
        Inserts element into the list as the next clockwise element.

        INPUT:

        - `element` -- DihedralElement; the element to insert.

        EXAMPLES:
        
        This example constructs a list of three elements using insert_cw_next.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: d1.get_elements_as_list() == [d1, d3, d2]
            True

        .. NOTE::

            This function is aliased by insert_ccw_prev and append_ccw.
        """
        element._ccw_next = self
        element._cw_next = self._cw_next
        self._cw_next._ccw_next = element
        self._cw_next = element
    insert_ccw_prev = insert_cw_next # alias
    append_ccw = insert_cw_next # alias

    def insert_ccw_next(self, element):
        r"""
        Inserts element into the list as the next counterclockwise element.

        INPUT:

        - `element` -- DihedralElement; the element to insert.

        EXAMPLES:

        This example constructs a list of three elements using insert_ccw_next.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_ccw_next(d2)
            sage: d1.insert_ccw_next(d3)
            sage: d1.get_elements_as_list() == [d1, d2, d3]
            True

        .. NOTE::

            This function is aliased by insert_cw_prev and append_cw.
        """
        element._cw_next = self
        element._ccw_next = self._ccw_next
        self._ccw_next._cw_next = element
        self._ccw_next = element
    insert_cw_prev = insert_ccw_next # alias
    append_cw = insert_ccw_next # alias

    def remove(self):
        r"""
        Removes this DihedralElement from its list.
        The element will also become its own list to facilitate reuse.

        EXAMPLES:

        This example constructs a list of three elements, then removes one.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: d2.remove()
            sage: d1.get_num_elements()
            2

        .. NOTE::

            This function has no effect if called on a 1-element list.

        TESTS:

            sage: d = DihedralElement(1)
            sage: d.remove()
            sage: d.get_num_elements()
            1
        """
        self._cw_next._ccw_next = self._ccw_next
        self._ccw_next._cw_next = self._cw_next
        self._cw_next = self
        self._ccw_next = self

    # Accessor functions
    
    def cw_next(self):
        r"""
        Returns the element clockwise from this one.
    
        OUTPUT: DihedralElement; the element clockwise from this one.
    
        EXAMPLES: 
    
        This example constructs a list of two elements.
        
            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d1.insert_cw_next(d2)
            sage: d1.cw_next() == d2
            True
    
        .. NOTE::
    
            This function is aliased by ccw_prev and ccw_last.
    
        TESTS::
    
            sage: d1 = DihedralElement(1)
            sage: d1.cw_next() == d1
            True
        """
        return self._cw_next
    ccw_prev = cw_next # alias
    ccw_last = cw_next # alias

    def ccw_next(self):
        r"""
        Returns the element counterclockwise from this one.
    
        OUTPUT: DihedralElement; the element counterclockwise from this one.
    
        EXAMPLES: 
    
        This example constructs a list of two elements.
        
            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d1.insert_cw_next(d2)
            sage: d1.ccw_next() == d2
            True
    
        .. NOTE::
    
            This function is aliased by cw_prev and cw_last.
    
        TESTS::
    
            sage: d1 = DihedralElement(1)
            sage: d1.ccw_next() == d1
            True
        """
        return self._ccw_next
    cw_prev = ccw_next # alias
    cw_last = ccw_next # alias

    def twin(self):
        r"""
        Returns an element of the same type representing movement in the opposite direction.

        OUTPUT: DihedralElement; the element traveling opposite this element.

        .. NOTE::

            ``d1.twin() == d2`` does not guarantee ``d1.cw_next() == d2.ccw_next()`` or 
            ``d1.ccw_next() == d2.cw_next()``; in fact, this is typically not the case,
            depending on the implementation.

        .. WARNING::

            Functionality related to twin is not implemented in the base class; this should
            be implemented in derived class constructors.

        .. SEEALSO:
            :meth:halfstrand.__init__
            :meth:halfhourglass.__init__
        """
        return self._twin
        
    def get_cw_ith_element(self, i):
        r"""
        Returns the element i elements clockwise of this one.

        INPUT:
        
        - ``i`` -- positive integer; how many elements to iterate. Assumed to be an integer `\geq 1`.

        OUTPUT: DihedralElement

        EXAMPLES:

        This example constructs a list of three elements.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: d1.get_cw_ith_element(2) == d3
            True

        If i is 0 or less, this element is returned.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d1.insert_cw_next(d2)
            sage: d1.get_cw_ith_element(-5) == d1
            True
            
        .. NOTE::

            Runtime: O(n)
        """
        e = self
        while i > 0:
            e = e.cw_next()
            i -= 1
        return e

    def get_ccw_ith_element(self, i):        
        r"""
        Returns the element i elements counterclockwise of this one.

        INPUT:
        
        - ``i`` -- positive integer; how many elements to iterate. Assumed to be an integer `\geq 1`.

        OUTPUT: DihedralElement

        EXAMPLES:

        This example constructs a list of three elements.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_ccw_next(d2)
            sage: d1.insert_ccw_next(d3)
            sage: d1.get_ccw_ith_element(2) == d3
            True

        If i is 0 or less, this element is returned.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d1.insert_ccw_next(d2)
            sage: d1.get_ccw_ith_element(-5) == d1
            True
            
        .. NOTE::

            Runtime: O(n)
        """
        e = self
        while i > 0:
            e = e.ccw_next()
            i -= 1
        return e

    # Turn functions
    
    def left_turn(self):
        r"""
        Returns the element representing taking a left turn from this element; 
        that is, traveling in the direction of this element, then traversing clockwise
        relative to this element's twin.

        OUTPUT: DihedralElement

        .. WARNING::

            Functionality related to twin is not implemented in the base class; this should
            be implemented in derived class constructors.

        .. SEEALSO:

            :func:`twin`
        """
        return self.twin().cw_next()

    def right_turn(self):
        r"""
        Returns the element representing taking a right turn from this element; 
        that is, traveling in the direction of this element, then traversing counterclockwise
        relative to this element's twin.

        OUTPUT: DihedralElement

        .. WARNING::

            Functionality related to twin is not implemented in the base class; this should
            be implemented in derived class constructors.

        .. SEEALSO:

            :func:`twin`
        """
        return self.twin().ccw_next()

    def get_ith_left(self, i):
        r"""
        Returns the element representing taking the ith left turn from this element; 
        that is, traveling in the direction of this element, then traversing clockwise i times
        relative to this element's twin.

        INPUT:

        - ``i`` -- positive integer; how far to turn left.  Assumed to be an integer `\geq 1`.

        OUTPUT: DihedralElement
        
        .. NOTE::

            Runtime: O(n)

        .. WARNING::

            Functionality related to twin is not implemented in the base class; this should
            be implemented in derived class constructors.

        .. SEEALSO:

            :func:`twin`
        """
        return self.twin().get_cw_ith_element(i)
        
    def get_ith_right(self, i):
        r"""
        Returns the element representing taking the ith right turn from this element; 
        that is, traveling in the direction of this element, then traversing counterclockwise i times
        relative to this element's twin.

        INPUT:

        - ``i`` -- positive integer; how far to turn right.  Assumed to be an integer `\geq 1`.

        OUTPUT: DihedralElement
        
        .. NOTE::

            Runtime: O(n)

        .. WARNING::

            Functionality related to twin is not implemented in the base class; this should
            be implemented in derived class constructors.

        .. SEEALSO:

            :func:`twin`
        """
        return self.twin().get_ccw_ith_element(i)

    # Directly connects two elements. Use insert functions instead if possible.
    
    def link_cw_next(self, element):
        r"""
        Directly connects this element clockwise to element.

        INPUT:

        - `element` -- DihedralElement

        EXAMPLES:

        This example demonstrates how to combine two lists.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: e1 = DihedralElement(11)
            sage: e2 = DihedralElement(12)
            sage: e3 = DihedralElement(13)
            sage: e1.insert_cw_next(e2)
            sage: e1.insert_cw_next(e3)
            sage: d1.link_cw_next(e1)
            sage: e2.link_cw_next(d3)
            sage: d1.get_elements_as_list() == [d1, e1, e3, e2, d3, d2]
            True

        .. NOTE::

            This function is aliased by link_ccw_prev.

        .. WARNING::

            Use insert_cw_next if possible. This function may break lists if not used properly.
            It is intended to be used internally, but may be useful outside.
        """
        self._cw_next = element
        element._ccw_next = self
    link_ccw_prev = link_cw_next # alias

    def link_ccw_next(self, element):
        r"""
        Directly connects this element counterclockwise to element.

        INPUT:

        - `element` -- DihedralElement

        EXAMPLES:

        This example demonstrates how to combine two lists.

            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: e1 = DihedralElement(11)
            sage: e2 = DihedralElement(12)
            sage: e3 = DihedralElement(13)
            sage: e1.insert_cw_next(e2)
            sage: e1.insert_cw_next(e3)
            sage: d3.link_ccw_next(e2)
            sage: e1.link_ccw_next(d1)
            sage: d1.get_elements_as_list() == [d1, e1, e3, e2, d3, d2]
            True

        .. NOTE::

            This function is aliased by link_cw_prev.

        .. WARNING::

            Use insert_ccw_next if possible. This function may break lists if not used properly.
            It is intended to be used internally, but may be useful outside.
        """
        self._ccw_next = element
        element._cw_next = self
    link_cw_prev = link_ccw_next # alias

    # List data functions

    def get_num_elements(self):
        r"""
        Returns the number of elements in the linked list.

        OUTPUT: integer

        EXAMPLES:

        Used on a single element list.

            sage: d1 = DihedralElement(1)
            sage: d1.get_num_elements()
            1

        Used on a three-element list.
        
            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: d3.get_num_elements()
            3
        """
        count = 0
        for element in self: count += 1
        return count

    def get_elements_as_list(self, clockwise=True):
        r"""
        Returns the elements in the linked list in a python list.

        INPUT:
        
        - `clockwise` -- boolean (default: `True`); If true, the list will be in clockwise order. Otherwise it will be in counterclockwise order.

        OUTPUT: DihedralElement list

        EXAMPLES:

        Used on a single element list.

            sage: d1 = DihedralElement(1)
            sage: d1.get_elements_as_list() == [d1]
            True

        Used on a three-element list.
        
            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: d2.get_elements_as_list(False) == [d2, d3, d1]
            True            
        """
        if clockwise: return [element for element in self.iterate_clockwise()]
        else: [element for element in self.iterate_counterclockwise()]

    def __iter__(self): # by default, iteration will go clockwise
        r"""
        Iterates over the elements in the linked list clockwise.

        OUTPUT: _DihedralIterator; Set as clockwise iterator

        EXAMPLES:

        Used on a three-element list.
        
            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: [d for d in d1]
            [1, 3, 2]

        .. NOTE::

            Use iterate_clockwise if the direction of iteration is important to indicate for legibility.
        """
        return _DihedralIterator(self, True)
    
    def iterate_clockwise(self): # for specificity, if it's important
        r"""
        Iterates over the elements in the linked list clockwise.

        OUTPUT: _DihedralIterator; Set as clockwise iterator

        EXAMPLES:

        Used on a three-element list.
        
            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: [d for d in d1.iterate_clockwise()]
            [1, 3, 2]
        """
        return _DihedralIterator(self, True)

    def iterate_counterclockwise(self):
        r"""
        Iterates over the elements in the linked list counterclockwise.

        OUTPUT: _DihedralIterator; Set as counterclockwise iterator

        EXAMPLES:

        Used on a three-element list.
        
            sage: d1 = DihedralElement(1)
            sage: d2 = DihedralElement(2)
            sage: d3 = DihedralElement(3)
            sage: d1.insert_cw_next(d2)
            sage: d1.insert_cw_next(d3)
            sage: [d for d in d1.iterate_counterclockwise()]
            [1, 2, 3]
        """
        return _DihedralIterator(self, False)

class _DihedralIterator:
    r"""
    Internal class for iterating over dihedral elements. Iteration can be specified to occur in clockwise or counterclockwise order.
    Modification of the list while iterating can cause errors with iteration.
    """
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
        