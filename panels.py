from bounds import Bounds


class Accumulator(object):
    """ Provides for event callbacks for matplotlib drag/release events and 
        axis limit changes by accumulating a series of event occurrences.
        Produces a single call to func after a user interacts with the plot.

        Also stores the axes that got the event, and passes them to func.

        Sample usage:

        from pylab import figure, show

        def simple(axes):
            print "update ", axes
        a = Accumulator(simple)

        f=figure()
        ax=f.add_subplot(111)
        plt=ax.plot(range(10))
        f.canvas.mpl_connect('draw_event', a.draw_event)
        f.canvas.mpl_connect('button_release_event', a.mouse_up_event)
        f.canvas.mpl_connect('button_press_event', a.mouse_down_event)
        ax.callbacks.connect('xlim_changed', a.axis_limit_changed)
        ax.callbacks.connect('ylim_changed', a.axis_limit_changed)
        show()

        """

    def __init__(self, func):
        self.func=func
        self.reset()
        self.mouse_up = True

    def reset(self):
        """ Reset flags after the update function is called.
            Mouse is tracked separately.
            """
        # print 'reset'
        self.limits_changed = 0
        self.got_draw = False
        self.axes = None

    def axis_limit_changed(self, ax):
        # print 'ax limits'
        self.limits_changed += 1
        self.axes = ax
        self.check_status()

    def draw_event(self, event):
        # print 'draw event'
        if self.limits_changed > 0:
            # only care about draw events if one of the axis limits has changed
            self.got_draw=True
        self.check_status()

    def mouse_up_event(self, event):
        # print 'mouse up'
        self.mouse_up = True
        self.check_status()

    def mouse_down_event(self, event):
        # print 'mouse down'
        self.mouse_up = False

    def both_limits_changed(self):
        """ Both x and y limits changed and the mouse is up (not dragging)
            This condition takes care of the limits being reset outside of a
            dragging context, such as the view-reset (home) button on the
            Matplotlib standard toolbar. 
            """
        # print "both_lim_chg"
        return (self.limits_changed >= 2) & self.mouse_up

    def interaction_complete(self):
        """ x, y, or both limits changed, and the mouse is up (not dragging).
            Also checks if matplotlib has done its final redraw of the screen, 
            which comes after the call to *both* set_xlim and set_ylim 
            have been triggered. The check for the draw event is the crucial 
            step in not producing two calls to self.func.
            
            New problem: with zoom, after a reset, get a draw event. on next axes change, the draw
            event  combines with an axis change to trigger interaction_complete. Then get another
            reset and ax limit change, and draw, and this passes again.
            Fixed this by adding a check on self.limits_changed > 0  in draw_event.
        """
        # print "interaction_complete"
        return (self.limits_changed>0) & self.got_draw & self.mouse_up

    def check_status(self):        
        if self.both_limits_changed() | self.interaction_complete():
            # print 'both limits:', self.both_limits_changed(), ', interaction:', self.interaction_complete()
            self.func(self.axes)
            self.reset()


class MPLaxesManager(object):

    def __init__(self, axes, coordinate_names):
        self.axes   = axes
        self.coordinate_names = coordinate_names
        self.events = Accumulator(self.on_axes_changed)

        self.pcolors = {}
        self.scatters = {}
        self.lines = {}
        
        
        # If pan/zoom events involve time ('t') on one axis,
        #   don't change the bounds on the other axis
        self.select_time_only = True

        self.interaction_callback = None

        self.callback_ids = {}
        self.callback_ids['draw_event'] = self.axes.figure.canvas.mpl_connect('draw_event', self.events.draw_event)
        self.callback_ids['button_press_event'] = self.axes.figure.canvas.mpl_connect('button_press_event', self.events.mouse_down_event)
        self.callback_ids['button_release_event'] = self.axes.figure.canvas.mpl_connect('button_release_event', self.events.mouse_up_event)
        self.callback_ids['xlim_changed'] = self.axes.callbacks.connect('xlim_changed', self.events.axis_limit_changed)
        self.callback_ids['ylim_changed'] = self.axes.callbacks.connect('ylim_changed', self.events.axis_limit_changed)


    def on_axes_changed(self, axes):
        """ Examine axes to see if axis limits really changed, and update bounds. """

        # Expect that the axes where the event was generated are this instance's axes
        if axes != self.axes:
            return

        # bounds = self.bounds
        # x_var, y_var = self.coordinate_names
        # 
        # # Figure out if the axis limits have changed, and set any new bounds
        # new_limits = axes.axis(emit=False)    # emit = False prevents infinite recursion    
        # old_x, old_y = getattr(bounds, x_var), getattr(bounds, y_var)
        # new_x, new_y = new_limits[0:2], new_limits[2:4]
        # 
        # if (new_x != old_x) | (new_y != old_y):
        #     setattr(bounds, x_var, new_x)
        #     setattr(bounds, y_var, new_y)
        #     self.bounds_updated()

        if self.interaction_callback != None:
            self.interaction_callback(self)


class Panels(object):
    """ Class to create and maintain a 4-D plot with four orthogonal projections of the data.
        x-y, x-z, z-y, t-z, t

        Instance variables:
            pool_manager is an associated manager of a pool of data
            view_bounds is this view's specific view bounds
        
        Issues:
            Should be able to choose any variable vs. time instead of hard-coding z.
    """
    # 1.618
    # 89,55,34,21,13,8,5,3,2,1,1,0
    
    dx = .89*0.55
    dz = .89*0.21
    mg = .89*0.05
    dy = dx
    dt = dx+dz 
    w = mg+dt+mg
    h = mg+dy+dz+mg+dz+mg
    aspect = h/w # = 1.30
           
    # Left, bottom, width, height
    margin_defaults = {
        'xy':(mg*aspect, mg, dx*aspect, dy),
        'xz':(mg*aspect, mg+dy, dx*aspect, dz),
        'zy':((mg+dx)*aspect, mg, dz*aspect, dy),
        'tz':(mg*aspect, mg+dy+dz+mg, dt*aspect, dz),
        }
    
    # margin_defaults = {
    #         'xy':(0.1, 0.1, 0.7, 0.4),
    #         'xz':(0.1, 0.5, 0.7, 0.15),
    #         'zy':(0.8, 0.1, 0.15, 0.4),
    #         'tz':(0.1, 0.8, 0.85, 0.15),
    #         # 't': (0.1, 0.85, 0.8, 0.1),
    #         }        
    #     
    def __init__(self, figure, ctr_lat=35.0, ctr_lon=-95.0):
        self.figure = figure
        self.panels = {}
        self.axes_managers = {}
        self.figure_manager = None
        self.bounds = Bounds()
        
        self.bounds_updated_callback = None
        
        self._panel_setup()
        
    def reset_axes_events(self):
        for mgr in self.axes_managers.values():
            mgr.events.reset()
        
  
    def bounds_updated(self):
        if self.bounds_updated_callback != None:
            self.bounds_updated_callback()

    def update_bounds_after_interaction(self, ax_mgr):
        bounds = self.bounds
        x_var, y_var = ax_mgr.coordinate_names
        axes = ax_mgr.axes
                
        # Figure out if the axis limits have changed, and set any new bounds
        new_limits = axes.axis(emit=False)    # emit = False prevents infinite recursion    
        old_x, old_y = getattr(bounds, x_var), getattr(bounds, y_var)
        new_x, new_y = new_limits[0:2], new_limits[2:4]

        

        # Handle special case of the z axis that's part of the zy axes,
        # which isn't shared with any other axis
        if ax_mgr is self.axes_managers['zy']:
            # Update one of the shared Z axes since zy changed
            self.axes_managers['tz'].axes.set_ylim(new_x)
            self.reset_axes_events()
            # axes.figure.canvas.draw()
        if (ax_mgr is self.axes_managers['tz']) | (ax_mgr is self.axes_managers['xz']):
            # One of the shared axes changed, so update zy
            self.axes_managers['zy'].axes.set_xlim(new_y)
            self.reset_axes_events()
            # axes.figure.canvas.draw()        
         
        if (new_x != old_x) | (new_y != old_y):
            setattr(bounds, x_var, new_x)
            setattr(bounds, y_var, new_y)
            self.bounds_updated()
    
    
    def _panel_setup(self):
        fig    = self.figure
        
        # --------- Set up data display axes ---------
        panels = self.panels
        panels['xy'] = fig.add_axes(Panels.margin_defaults['xy'])
        panels['xz'] = fig.add_axes(Panels.margin_defaults['xz'], sharex=panels['xy'])
        panels['zy'] = fig.add_axes(Panels.margin_defaults['zy'], sharey=panels['xy'])
        panels['tz'] = fig.add_axes(Panels.margin_defaults['tz'], sharey=panels['xz'])
        
        panels['xz'].xaxis.set_visible(False)
        panels['zy'].yaxis.set_visible(False)
        
        xy_manager = MPLaxesManager(panels['xy'], ('x','y'))    
        xz_manager = MPLaxesManager(panels['xz'], ('x','z'))
        zy_manager = MPLaxesManager(panels['zy'], ('z','y'))
        tz_manager = MPLaxesManager(panels['tz'], ('t','z'))
        
        self.axes_managers['xy'] = xy_manager
        self.axes_managers['xz'] = xz_manager
        self.axes_managers['zy'] = zy_manager
        self.axes_managers['tz'] = tz_manager
        
        for mgr in self.axes_managers.values():
            mgr.interaction_callback = self.update_bounds_after_interaction
        

    
    def panel_name_for_axis(self, ax):
        for panel_name, axis in self.panels.iteritems():
            if axis is ax:
                return panel_name