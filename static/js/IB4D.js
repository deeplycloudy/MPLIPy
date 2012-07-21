var kernel = IPython.notebook.kernel;

/* 
After a kernel.execute, it's necessary to hand off the output to a valid output area that's
part of the browser DOM. Previously, output was winding up back in a javascript function call,
in this script, which prevented future javascript calls from getting to the browser.
*/

// kernel.execute("some_python()", {'output': backend_done}); // Doesn't work.
//   vs.
// kernel.execute("some_python()", {'output': $.proxy(output_area.handle_output, output_area)});

var output = $('<div></div>');
output_area = new IPython.OutputArea(output, true);    
    
/*backend_done = function(msg_type, content){
    console.log(msg_type);
    console.log(content);
};*/

ui_callback = function(event_spec){
    kernel.execute("ui_callback(\'" + JSON.stringify(event_spec)  + "\')", $.proxy(output_area.handle_output, output_area));
};


set_sliders = function(bounds){
    /* Give a JSON bounds dictionary, set position of the slider */
    bounds = JSON.parse(bounds);
    
    $('div#x_slider').slider("values", 0, bounds["x"][0]);
    $('div#x_slider').slider("values", 1, bounds["x"][1]);
    $('div#y_slider').slider("values", 0, bounds["y"][0]);
    $('div#y_slider').slider("values", 1, bounds["y"][1]);
    $('div#z_slider').slider("values", 0, bounds["z"][0]);
    $('div#z_slider').slider("values", 1, bounds["z"][1]);
    $('div#t_slider').slider("values", 0, bounds["t"][0]);
    $('div#t_slider').slider("values", 1, bounds["t"][1]);
    
    update_slider_labels(bounds);

};

read_slider_positions = function() {
    // Create a bounds dictionary from the current slider position
    
    var positions = {};
    positions["x"] = [$('div#x_slider').slider("values", 0), $('div#x_slider').slider("values", 1)];
    positions["y"] = [$('div#y_slider').slider("values", 0), $('div#y_slider').slider("values", 1)];
    positions["z"] = [$('div#z_slider').slider("values", 0), $('div#z_slider').slider("values", 1)];
    positions["t"] = [$('div#t_slider').slider("values", 0), $('div#t_slider').slider("values", 1)];
    return positions      
};

update_slider_labels = function(bounds) {
    
    $('span#x_label').text("x = " + bounds["x"][0] + " to " + bounds["x"][1] );
    $('span#y_label').text("y = " + bounds["y"][0] + " to " + bounds["y"][1] );
    $('span#z_label').text("z = " + bounds["z"][0] + " to " + bounds["z"][1] );
    $('span#t_label').text("t = " + bounds["t"][0] + " to " + bounds["t"][1] );

};

slide_event = function(){
    // Called when a slider is dragged
    if (!kernel) return;
    // execute update on the kernel
    
    var bounds = read_slider_positions();
    update_slider_labels(bounds);
    
    // console.log("Got slide event")
        
    kernel.execute("update_limits(\'" + JSON.stringify(bounds)  + "\')", {'output': $.proxy(output_area.handle_output, output_area)});

};


// set_sliders_msg = function(msg_type, content){
//     // call this from Python to set the sliders
//     // What's the right msg_type to use here? How do we actually call this
//     if (msg_type !== 'display_data')
//         return;
//     var bounds = content['data']['application/json'];
//     if (bounds != undefined){
//         set_sliders(bounds);
//         
//         console.log("no bounds?!");
//         console.log(data);
//     }  
// };

// request_update = function(){
//     if (!kernel) return;
//     // execute update on the kernel
//     
//     var bounds = read_slider_position();
//     update_slider_labels(bounds)
//     
//     // kernel.execute("update_limits(\'" + JSON.stringify(bounds)  + "\')", {'output': backend_done});
//     kernel.execute("update_limits(\'" + JSON.stringify(bounds)  + "\')");
// 
// };

// request_update();

