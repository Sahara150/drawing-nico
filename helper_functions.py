from drawing import open_canvas
import os
from datetime import datetime
import pandas as pd
import tkinter as tk
from global_static_vars import images_dir, experiment_dir, draw_color, draw_size

def draw_ten_times():
    ## Create new folder for participant
    now = datetime.now()
    date_hour = now.strftime("_%d-%m-%Y_%H-%M-%S")
    participant_dir = "nicodraws" + str(date_hour)
    path_folder_participant = images_dir + participant_dir
    os.mkdir(path_folder_participant)


    for i in range(0,10):
        open_canvas("test", path_folder_participant, "robot", "sk")

def read_results(category : str, iteration : int):
    path_results = experiment_dir + f"raw_{category}.ndjson"
    file = pd.read_json(path_results, lines=True)
    # This gets the detailed strokes for each iteration of category
    detailed_strokes = file["detailed_strokes"]
    data = detailed_strokes[iteration]
    return data

def create_canvas_with_data(data : list[list[int]]):
    (root, canvas) = setup_UI()
    for i in range(1, len(data)):
        if data[i-1][2] != -1:
            # No end of stroke before, draw connection
            canvas.create_line(data[i-1][0], data[i-1][1], data[i][0], data[i][1], fill=draw_color, width=draw_size, tags=('stroke', stroke_count))

def setup_UI(show_button : bool) -> "tuple[object, object]":

    # Initialize Tkinter
    root = tk.Tk()
    root.attributes('-fullscreen', True)

    ######### CONFIGURATION OF THE GLOBAL VARIABLES OF THE CANVAS AND SCREENSHOTS ###########

    # Create the drawing canvas
    if show_button:
        button = tk.Button(text=tr("If you finished, press the button", "Ak ste skončili, kliknite pre pokračovanie"), command=lambda: quit_program(), height=4)
        button.pack(side="bottom")

    canvas = tk.Canvas(root, bg='white')
    canvas.pack(anchor='center', expand=True, fill="both")

    return (root, canvas)

data = read_results("test", 0)