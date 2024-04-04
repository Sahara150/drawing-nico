import pandas as pd
from global_static_vars import experiment_dir
import tkinter as tk
import numpy
from rdp import rdp
from global_static_vars import draw_color, draw_size, line_args, lower_edge_canvas, width_side

def read_results(category : str, iteration : int):
    path_results = experiment_dir + f"raw_{category}.ndjson"
    file = pd.read_json(path_results, lines=True)
    # This gets the detailed strokes for each iteration of category
    strokes = file["strokes"]
    data = strokes[iteration]
    return data

def tr(a,b):
    country = line_args['country']
    if country == 'SK' or country == 'sk':
        return b
    else:
        return a
    
def flatten_data(data: list[list[list[int]]]):
    flattened_strokes = []
    for stroke in data:
        #This is a 3D-array of x, y and t arrays 
        #Skip all empty strokes
        if len(stroke[0])!=0:
            #We drop the time as it is irrelevant for flattening the data 
            shortened_stroke = [stroke[0], stroke[1]]      
            transformed_stroke = numpy.transpose(shortened_stroke)
            #It may be discussed, how much we wanna reduce the point-clouds, 
            #but that for sure is a start
            flattened = rdp(transformed_stroke, epsilon=3)
            flattened_strokes.append(flattened)
    return flattened_strokes

# This function mirrors the y values by calculating "lower edge of canvas"-y as new y
# x stays untouched when the robot shall draw, as we just invert the axis, so that (0|0) 
# is at the lower left of robot
# If the image gets turned around later to calculate the error, x gets mirrored too
def transform_coordinates(data: list[list[list[int]]], transform_x : bool = False):
    return map(lambda stroke: map(lambda coordinate: transform_coordinate(coordinate, transform_x), stroke), data)

def transform_coordinate(coordinate: list[int], transform_x : bool):
    if transform_x:
        return [width_side-coordinate[0], lower_edge_canvas-coordinate[1]]
    else:
        return [coordinate[0], lower_edge_canvas-coordinate[1]]
    
######### CANVAS HELPERS ###########

def create_canvas_with_data_from_strokes(data : list[list[list[int]]]):
    (root, canvas) = setup_UI()
    for stroke in data:
        for i in range(1, len(stroke[0])): 
            canvas.create_line(stroke[0][i-1], stroke[1][i-1], stroke[0][i], stroke[1][i], fill=draw_color, width=draw_size)
            #HOME SOLUTION: multiplies the pixels by 0.71
            #canvas.create_line(stroke[0][i-1]*0.71, stroke[1][i-1]*0.71, stroke[0][i]*0.71, stroke[1][i]*0.71, fill=draw_color, width=draw_size)
    root.mainloop()        

def create_canvas_with_flattened_data(data : list[list[list[int]]]):
    (root, canvas) = setup_UI()
    for stroke in data:
        for i in range(1, len(stroke)):
            canvas.create_line(stroke[i-1][0], stroke[i-1][1], stroke[i][0], stroke[i][1], fill='red', width=draw_size)
            #HOME SOLUTION: multiplies the pixels by 0.71
            #canvas.create_line(stroke[i-1][0]*0.71, stroke[i-1][1]*0.71, stroke[i][0]*0.71, stroke[i][1]*0.71, fill='red', width=draw_size)
    root.mainloop()

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