import tkinter as tk
from global_static_vars import draw_color, draw_size

######### CANVAS HELPERS ###########
prev_x = None
prev_y = None
canvas = None
root = None

def create_canvas_with_data_from_strokes(data : list[list[list[int]]]):
    (root, canvas) = setup_UI()
    for stroke in data:
        for i in range(1, len(stroke[0])): 
            #canvas.create_line(stroke[0][i-1], stroke[1][i-1], stroke[0][i], stroke[1][i], fill=draw_color, width=draw_size)
            #HOME SOLUTION: multiplies the pixels by 0.71 due to smaller screen
            canvas.create_line(stroke[0][i-1]*0.71, stroke[1][i-1]*0.71, stroke[0][i]*0.71, stroke[1][i]*0.71, fill=draw_color, width=draw_size)
    root.mainloop()        

def create_canvas_with_flattened_data(data : list[list[list[int]]]):
    (root, canvas) = setup_UI()
    for stroke in data:
        for i in range(1, len(stroke)):
            #canvas.create_line(stroke[i-1][0], stroke[i-1][1], stroke[i][0], stroke[i][1], fill='red', width=draw_size)
            #HOME SOLUTION: multiplies the pixels by 0.71 due to smaller screen
            canvas.create_line(stroke[i-1][0]*0.71, stroke[i-1][1]*0.71, stroke[i][0]*0.71, stroke[i][1]*0.71, fill='red', width=draw_size)
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

# TODO: Actually, we need to store all the strokes for the robot, so we can compare them to should-be
def on_mouse_release(event):
    global prev_x, prev_y
    # Just setting last coordinate to none, so that new stroke begins
    prev_x = None
    prev_y = None

def on_mouse_move(event):
    global prev_x, prev_y

    c_x = event.x
    c_y = event.y
    
    if prev_x is not None and prev_y is not None:
        canvas.create_line(prev_x, prev_y, c_x, c_y, fill=draw_color, width=draw_size, tags=('stroke', stroke_count))
    
    prev_x = c_x
    prev_y = c_y

def open_canvas_for_robot():
    global canvas, root
    (canvas, root) = setup_UI()

    # Bind the mouse movement event to the canvas
    canvas.bind('<B1-Motion>', on_mouse_move)

    # Bind the mouse release event to the canvas
    canvas.bind('<ButtonRelease-1>', on_mouse_release)

    root.mainLoop()

def close_canvas():
    root.destroy()