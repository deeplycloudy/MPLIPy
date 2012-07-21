class Bounds(object):
    '''Bounds is a class to hold a set of ranges (start,end) for different
    variables.  Bounds can be optionally initialized with another Bounds
    instance as a parent.  If bounds for a particular variable cannot be found
    within itself, the Bounds will try its parent.'''

    def __init__(self, parent = None, **kwargs):
        self._parent = parent
        self._vars = []
        for bound, limits in kwargs.items():
            setattr(self, bound, limits)

    def __getattr__(self, attr):
        #If we're in this function, a straight lookup of the attribute within
        #the instance's dictionary has failed.  Therefore, we look to the
        #parent, if one exists, otherwise
        if self._parent:
            return getattr(self._parent, attr)
        else:
            return (None, None)

    def __setattr__(self, attr, val):
        if attr not in ['_parent','_vars']:
            # Check to see if we already have a value for this attribute. If so, just change the value.
            # Only look at vars, not parent, since want to be able to override parent
            if attr not in self._vars:
                self._vars.append(attr)
        self.__dict__[attr] = val

    def __getitem__(self, var):
        return getattr(self, var)
    
    def __iter__(self):
        #Return an iterator over all bounded variables, including those in
        #parent
        if self._parent:
            return iter(self._vars +
                [v for v in self._parent if v not in self._vars])
        else:
            return iter(self._vars)
    
    def limits(self):
        vars = [v for v in self]
        return zip(vars, (getattr(self, v) for v in vars))
