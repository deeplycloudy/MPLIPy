import time

import numpy as np
import matplotlib.pyplot as plt

def coroutine(func):
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start

            
# if we want ax_bundle to be in every segment, can we get it in there in the coroutine as part of that block?
@coroutine
def segment(ax_bundle, target):
    """ >>> segment(ax_bundle, (segment(ax_bundle, target)))
    """
    while True:
        a = (yield)
        print "segment passthrough to ", target
        target.send(a)


class Segment(object):
    """ Class-based version useful for tracking a changing state or adjusting targets
        at a later time. Some '.dot' access overhead this way, of course.

        >>> Segment( ax_bundle, Segment(ax_bundle, None).process() )

        Is it also easier to disconnect and replumb the pipeline later if we use classes for
        all segments? Hopefully we're dealing with big chunks of data all at once so the
        call overhead isn't too bad.
    """

    def __init__(self, ax_bundle, target=None): 
        self.target = target # this perhaps should be a set and not a list, so it remains unique
        self.ax_bundle = ax_bundle
        
    @coroutine
    def process(self):
        while True:
            a = (yield)
            print "segment passthrough to ", target
            self.target.send(a)

            
@coroutine
def broadcast(targets):
    while True:
        stuff = (yield)
        for target in targets:
            # print "broadcast to ", target
            target.send(stuff)
        del stuff



