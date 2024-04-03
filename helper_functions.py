import pandas as pd
from global_static_vars import experiment_dir
import tkinter as tk
from global_static_vars import draw_color, draw_size, width_main, width_side, height_side, country


def read_results(category : str, iteration : int):
    path_results = experiment_dir + f"raw_{category}.ndjson"
    file = pd.read_json(path_results, lines=True)
    # This gets the detailed strokes for each iteration of category
    detailed_strokes = file["detailed_strokes"]
    data = detailed_strokes[iteration]
    return data

def tr(a,b):
    if country == 'SK' or country == 'sk':
        return b
    else:
        return a
    
######### CANVAS HELPERS ###########


def create_canvas_with_data(data : list[list[int]]):
    (root, canvas) = setup_UI()
    for i in range(1, len(data)):
        if data[i-1][2] != -1:
            # No end of stroke before, draw connection
            canvas.create_line(data[i-1][0], data[i-1][1], data[i][0], data[i][1], fill=draw_color, width=draw_size)

def setup_UI(second_display : bool = True) -> "tuple[object, object]":

    # Initialize Tkinter
    root = tk.Tk()
    if second_display:
        root.geometry(f"{width_side}x{height_side}+{width_main}+0")
    root.attributes('-fullscreen', True)

    canvas = tk.Canvas(root, bg='white')
    canvas.pack(anchor='center', expand=True, fill="both")

    return (root, canvas)   