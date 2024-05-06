import tkinter as tk
from global_static_vars import draw_color, draw_size
from PIL import ImageGrab
from global_static_vars import width_side, height_side, line_args, experiment_dir
from file_helper import append_to_ndjson

######### CANVAS HELPERS ###########
prev_x = None
prev_y = None
canvas = None
root = None
x = []
y = []
strokes = []
stroke_count = 0


def increase_stroke_count():
    global stroke_count
    stroke_count += 1

def create_canvas_with_data_from_strokes(data : list[list[list[int]]]):
    (root, canvas) = setup_UI()
    colors = ["black", "red", "green", "yellow", "blue"]
    index = 0
    for stroke in data:
        index += 1
        for i in range(1, len(stroke[0])): 
            canvas.create_line(stroke[0][i-1], stroke[1][i-1], stroke[0][i], stroke[1][i], fill=colors[index%5], width=draw_size)
            #HOME SOLUTION: multiplies the pixels by 0.71 due to smaller screen
            #canvas.create_line(stroke[0][i-1]*0.71, stroke[1][i-1]*0.71, stroke[0][i]*0.71, stroke[1][i]*0.71, fill=colors[index%5], width=draw_size)
    root.mainloop()        

def create_canvas_with_flattened_data(data : list[list[list[int]]]):
    (root, canvas) = setup_UI()
    draw_template(data, canvas)
    root.mainloop()

# TODO: Old code, clean up before submission
def create_canvas_with_data_from_detailed_strokes(data : list[list[int]]):
    (root, canvas) = setup_UI()
    for i in range(1, len(data)):
        if data[i-1][2] != -1:
            # No end of stroke before, draw connection
            canvas.create_line(data[i-1][0], data[i-1][1], data[i][0], data[i][1], fill=draw_color, width=draw_size)
            #HOME SOLUTION: multiplies the pixels by 0.71
            #canvas.create_line(data[i-1][0]*0.71, data[i-1][1]*0.71, data[i][0]*0.71, data[i][1]*0.71, fill=draw_color, width=draw_size)
    root.mainloop()

def setup_UI() -> "tuple[object, object]":

    # Initialize Tkinter
    root = tk.Tk()
    root.attributes('-fullscreen', True)

    canvas = tk.Canvas(root, bg='white')
    canvas.pack(anchor='center', expand=True, fill="both")

    return (root, canvas)   

def on_mouse_release(event):
    global prev_x, prev_y, x, y, stroke_count
    #We will not increase stroke count here, but manually in robot, because
    # there may be unintentional stroke interruptions and that way the error function
    # still knows which stroke it belongs to
    # Just setting last coordinate to none, so that new stroke begins
    print("Mouse release")
    strokes.append([x, y, stroke_count])

    x = []
    y = []
    
    prev_x = None
    prev_y = None

def on_mouse_down(event):
    print("Mouse down")
    global prev_x, prev_y
    prev_x = event.x
    prev_y = event.y

def on_mouse_move(event):
    global prev_x, prev_y
    c_x = event.x
    c_y = event.y

    x.append(c_x)
    y.append(c_y)

    
    if prev_x is not None and prev_y is not None:
        canvas.create_line(prev_x, prev_y, c_x, c_y, fill=draw_color, width=draw_size)
    
    prev_x = c_x
    prev_y = c_y

def open_canvas_for_robot(data : list[list[list[int]]]):
    global canvas, root
    
    #Reset variables so it deletes data of last drawing
    reset_variables()

    (root, canvas) = setup_UI()
    draw_template(data, canvas)
    
    canvas.bind('<ButtonPress-1>', on_mouse_down)

    # Bind the mouse movement event to the canvas
    canvas.bind('<B1-Motion>', on_mouse_move)

    # Bind the mouse release event to the canvas
    canvas.bind('<ButtonRelease-1>', on_mouse_release)

    root.bind("<<close_canvas>>", close_canvas_event)
    root.mainloop()

def close_canvas():

    ImageGrab.grab().crop((0, 0, width_side, height_side)).save(line_args['path_folder_participant'] + "/" + "drawing_robot.png")
    strokes_file_path = experiment_dir + "raw_robot_result.ndjson"
    
    stroke_data = {
        "strokes": strokes
    }
    append_to_ndjson(strokes_file_path, stroke_data)
    root.event_generate("<<close_canvas>>", when="tail", state=123) # trigger event in main thread

def close_canvas_event(evt):        
    root.destroy()

def draw_template(data : list[list[list[int]]], canvas):
    for stroke in data:
        for i in range(1, len(stroke)):
            canvas.create_line(stroke[i-1][0], stroke[i-1][1], stroke[i][0], stroke[i][1], fill='red', width=draw_size)
            canvas.create_oval(stroke[i][0], stroke[i][1], stroke[i][0]+ 3, stroke[i][1] + 3)
            #HOME SOLUTION: multiplies the pixels by 0.71 due to smaller screen
            #canvas.create_line(stroke[i-1][0]*0.71, stroke[i-1][1]*0.71, stroke[i][0]*0.71, stroke[i][1]*0.71, fill='red', width=draw_size)

def reset_variables():
    global prev_x, prev_y, canvas, root, x, y, strokes, stroke_count
    prev_x = None
    prev_y = None
    canvas = None
    root = None
    x = []
    y = []
    strokes = []
    stroke_count = 0
