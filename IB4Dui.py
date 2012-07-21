from IPython.core.display import JSON, display, Javascript
import json


ui_json_decoder = json.JSONDecoder()


class SliderManager(object):
    def __init__(self, panels):
        self.panels = panels
        
    def __call__(self):
        bounds = dict(self.panels.bounds.limits())

        
        
        js = "set_sliders(\'{0}\');".format(json.dumps(bounds))
        display(Javascript(js))


class CallbackCenter(object):
    def __init__(self, trigger_dict):
        self.triggers = trigger_dict
        
    def __call__(self, event_spec):
        event_spec = ui_json_decoder.decode(event_spec)
        item_id = event_spec.pop('item_id')
        func = self.triggers[item_id]
        func(**event_spec)
    
