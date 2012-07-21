import matplotlib.pyplot as plt



import json
decoder = json.JSONDecoder()

from IB4Dui import CallbackCenter, SliderManager
from panels import Panels

def load_lma():
    print "Loading LMA now"

def do_animate(duration=0):
    # do int(duration) - comes in as a string
    print "Animating some stuff for {0} seconds".format(duration)


menu_callback_triggers = {
    'lma_load': load_lma,
    'do_animate': do_animate,
}
ui_callback = CallbackCenter(menu_callback_triggers)


def update_limits(bounds_json):
    """ This is called by the UI after a slider changes"""
    
    
    # I think we need to set the bounds in the panels object here.

    bounds = decoder.decode(bounds_json)
    xy = bounds["x"] + bounds["y"]
    zy = bounds["z"] + bounds["y"]
    xz = bounds["x"] + bounds["z"]
    tz = bounds["t"] + bounds["z"]
    p.panels['xy'].axis(xy, emit=False)
    p.panels['zy'].axis(zy, emit=False)
    p.panels['xz'].axis(xz, emit=False)
    p.panels['tz'].axis(tz, emit=False)  
        
    p.figure.canvas.draw()
    
    p.update_bounds_after_interaction()

    p.reset_axes_events()
    # for mgr in p.axes_managers.values():
        # mgr.events.reset()
    

# =======

fig = plt.figure()

p = Panels(fig)

p.panels['xy'].plot(range(10))
p.panels['xy'].set_xlabel('East')
p.panels['xy'].set_ylabel('North')

p.panels['zy'].plot(range(10))
p.panels['zy'].set_xlabel('Altitude')

p.panels['xz'].plot(range(10))
p.panels['xz'].set_ylabel('Altitude')

p.panels['tz'].plot(range(10))
p.panels['tz'].set_xlabel('Time')
p.panels['tz'].set_ylabel('Altitude')

set_sliders_py = SliderManager(p)

p.bounds_updated_callback = set_sliders_py

p.bounds.x = (0,7)
p.bounds.y = (0,8)
p.bounds.z = (0,6)
p.bounds.t = (0,4)

set_sliders_py()

plt.show()

# =======

