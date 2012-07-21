from IPython.core.display import JSON, display, Javascript
            
def set_sliders():
    bounds = {}
    xy = p.panels['xy'].axis()
    tz = p.panels['tz'].axis()
    bounds['x'] = xy[0:2]
    bounds['y'] = xy[2:4]
    bounds['t'] = tz[0:2]
    bounds['z'] = tz[2:4]
    print bounds

    js = "set_sliders(\'{0}\');".format(json.dumps(bounds))
    display(Javascript(js))


class MenuCallbackCenter(object):
    def __init__(self, trigger_dict):
        self.triggers = trigger_dict
        
    def __call__(self, menu_id):
        self.triggers[menu_id]
    
