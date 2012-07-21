import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from pipeline import coroutine, broadcast, segment, Segment

from panels import Panels
# class AxesBundle(object):
#     def __init__(self):
#         """ Each axes spec should minimally contain x,y to variable name mappings, 
#             plus optional color by and size by defaults.
# 
#         """
#         self.bounds = None
# 
#         # these should be properties for use when the ax_specs don't specify what the artists need
#         self.fallback_color_by = 'time'
#         self.fallback_size_by  = None
#         self.ui = None
# 
#         self.datasets = [] # probably actually should be a set, not list. Just add to this.
#         self.ax_specs = {} # {ax0:ax0_spec, ax1:ax1_spec}
# 
#     def on_axes_changed(self):
#         for d in self.datasets:
#             d.resend()



class Data(object):
    """ UI code will usually call a function to load some data and set up
        a processing pipeline, which is used to create this object. This object
        is then added to any axes bundles after creation.
    """
    def __init__(self, data, target=[], suppress_initial_send=True):
        self.data = data
        self.target = target
        if suppress_initial_send != True:
            self.resend()
    def resend(self):
        self.target.send(self.data)

@coroutine
def random_segment(ax_bundle, target):
    """ randomize all the data in an array.
    """
    while True:
        a_in = (yield)
        
        a = a_in.copy()
        
        factor = 10
        
        # normally we'd only touch a few specific axes pertinent to the pipeline
        # but instead we'll modify the whole thing for simplicity
        for k in a.dtype.names:
            a[k] = np.random.random(a.shape) * factor
        target.send(a)
        del a
    
  
class PanelAxesFilter(Segment):
    """ Filter showing use of the axes bounds to filter data from an array
        for a single pair of coorindate axes.
    
        Can't use one of these per panel instance, and then re-call the
        coroutine as necessary to set up individual segments, because the targets
        are different and we want the target in the class so we can hook/unhook 
        later. Would be interesting to chart out where things should live if
        we want to hook/unhook vs. save on memory or efficiency.
        
        The mechanics of how one breaks the pipeline and reconnects with a 
        modified filter are yet to be worked out.
        
        There is another version of this class, below, that filters across
        all coordinates based on the bounds for all the axes.
     
    """
    @coroutine
    def filter(self, mpl_axes):
        """ We set up the bounds and target here to save on lookup overhead.
            It also allows the pipeline to be broken and reinitialized if the
            target needs to change.
            
            Initialize with a matplotlib axes instance that is the target plot.
        """
        bounds = self.ax_bundle.bounds
        target = self.target
        coords = self.ax_bundle.ax_specs[mpl_axes]
        x_name, y_name = coords['x'], coords['y']
        while True:
            a = (yield)
            a_x, a_y  = a[[x_name, y_name]]
            ((x0, x1), (y0, y1)) = bounds[x_name], bounds[y_name]
            good = (a_x >= x0) & (a_x <= x1) & (a_y >= y0) & (a_y <= y1) 
            target.send(a[good])

            
  
class PanelBoundsFilter(Segment):
    """ Filter showing use of the axes bounds to filter data from an array.

        Can't use one of these per panel instance, and then re-call the
        coroutine as necessary to set up individual segments, because the targets
        are different and we want the target in the class so we can hook/unhook 
        later. Would be interesting to chart out where things should live if
        we want to hook/unhook vs. save on memory or efficiency.

        The mechanics of how one breaks the pipeline and reconnects with a 
        modified filter are yet to be worked out.

        There is another version of this class, to be written, that filters across
        all coordinates based on the bounds for all the axes.

    """
    @coroutine
    def filter(self):
        """ We set up the bounds and target here to save on lookup overhead.
            It also allows the pipeline to be broken and reinitialized if the
            target needs to change.

            Initialize with a matplotlib axes instance that is the target plot.
        """
        bounds = self.ax_bundle.bounds
        target = self.target
        coords_xy = self.ax_bundle.ax_specs[self.ax_bundle.panels['xy']]
        coords_tz = self.ax_bundle.ax_specs[self.ax_bundle.panels['tz']]
        x_name, y_name = coords_xy['x'], coords_xy['y']
        t_name, z_name = coords_tz['x'], coords_tz['y']
        
        while True:
            a = (yield)
            print 
            # a_x, a_y, a_z, a_t  = a[[x_name, y_name, z_name, t_name]]
            ((x0, x1), (y0, y1)) = bounds[x_name], bounds[y_name]
            ((t0, t1), (z0, z1)) = bounds[t_name], bounds[z_name]
            good  = (a[x_name] >= x0) & (a[x_name] <= x1) 
            good &= (a[y_name] >= y0) & (a[y_name] <= y1)
            good &= (a[z_name] >= z0) & (a[z_name] <= z1) 
            good &= (a[t_name] >= t0) & (a[t_name] <= t1)
            target.send(a[good])
            

class LineArtistOutlet(object):
    def __init__(self, ax_bundle, artist):
        self.artist = artist
        self.ax_bundle = ax_bundle

    @coroutine
    def process(self):
        # print "now processing {0}".format(self.artist)
        while True:
            a = (yield)
            # print "artist got data ", a
            ax = self.artist.axes
            coords = self.ax_bundle.ax_specs[ax]
            # print "artist got coords ", coords
            x, y = a[coords['x']], a[coords['y']]
            self.artist.set_data(x, y)
            ax.figure.canvas.draw()


def load_new_data(ax_bundle):
    import numpy as np
    
    dtype = np.dtype([  ('x', np.float32), 
                        ('y', np.float32),
                        ('z', np.float32),
                        ('t', np.float32)
                        ])
                        
    N = 10
    factor = 10
    a = np.empty(N, dtype=dtype)
    a['x'] = np.random.random(N) * factor
    a['y'] = np.random.random(N) * factor
    a['z'] = np.random.random(N) * factor
    a['t'] = np.random.random(N) * factor
    
    art_xy = LineArtistOutlet(ax_bundle, Line2D([0,1], [0,1], linestyle=None, marker='.'))
    art_tz = LineArtistOutlet(ax_bundle, Line2D([0,1], [0,1], linestyle=None, marker='.')) 
    art_zy = LineArtistOutlet(ax_bundle, Line2D([0,1], [0,1], linestyle=None, marker='.')) 
    art_xz = LineArtistOutlet(ax_bundle, Line2D([0,1], [0,1], linestyle=None, marker='.')) 
    ax_bundle.panels['xy'].add_line(art_xy.artist)
    ax_bundle.panels['xz'].add_line(art_xz.artist)
    ax_bundle.panels['zy'].add_line(art_zy.artist)
    ax_bundle.panels['tz'].add_line(art_tz.artist)
        
    xy_pipeline = segment(ax_bundle, art_xy.process())
    zy_pipeline = segment(ax_bundle, art_zy.process())
    xz_pipeline = segment(ax_bundle, art_xz.process())
    tz_pipeline = segment(ax_bundle, art_tz.process())
    
    broadcaster= broadcast([xy_pipeline, tz_pipeline, xz_pipeline, zy_pipeline])
    bnd_filter = PanelBoundsFilter(ax_bundle, broadcaster).filter()
    
    d = Data(a, target=bnd_filter)
    ax_bundle.datasets.append(d)
    
    return d
        

fig = plt.figure()

p = Panels(fig)

p.panels['xy'].set_xlabel('East')
p.panels['xy'].set_ylabel('North')
p.panels['tz'].set_xlabel('Time')
p.panels['tz'].set_ylabel('Altitude')
p.panels['zy'].set_xlabel('Altitude')
p.panels['xz'].set_ylabel('Altitude')


p.panels['xy'].axis((0,10,0,10))
p.panels['tz'].axis((0,10,0,10))

p.update_bounds_after_interaction(p.axes_managers['xy'])
p.update_bounds_after_interaction(p.axes_managers['tz'])

# set_sliders_py = SliderManager(p)

d = load_new_data(p)

p.bounds_updated_callback = d.resend

# set_sliders_py()
plt.show()

