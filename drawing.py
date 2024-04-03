import tkinter as tk
import sys
import time
import numpy as np
from psychopy import event, visual, monitors, core
from PIL import Image, ImageTk, ImageGrab
import pandas as pd
import os
from datetime import datetime
import json
import ndjson
from global_static_vars import draw_color, draw_size, experiment_dir, country
from global_static_vars import width_main, width_side, height_side
from helper_functions import tr

# Store the coordinates of the previous point
prev_x = None
prev_y = None
start_drawing_time = 0.0

x = []
y = []
t = []
strokes = []
detailed_strokes = []

# Keep track of the number of strokes
stroke_count = 0

do_one_time = True
total_drawing_time = 0.0
latency = 0.0
temp = 0.0
margin = 0.0

def open_canvas(_category : str, _participant : str, _condition : str):
    global category, participant, condition, start, strokes_file_path, root, canvas
    category = _category
    participant = _participant
    condition = _condition
    strokes_file_path = experiment_dir + "raw_" + category + ".ndjson"
    start = time.time()
    (root, canvas) = setup_UI()

    # Bind the mouse movement event to the canvas
    canvas.bind('<B1-Motion>', on_mouse_move)

    # Bind the mouse release event to the canvas
    canvas.bind('<ButtonRelease-1>', on_mouse_release)


    # Start the main Tkinter event loop
    root.mainloop()

def setup_UI() -> "tuple[object, object]":

    # Initialize Tkinter
    root = tk.Tk(screenName="Standardmonitor")
    #if second_display:
     #   root.geometry(f"{width_side}x{height_side}+{width_main}+0")
    root.attributes('-fullscreen', True)

    ######### CONFIGURATION OF THE GLOBAL VARIABLES OF THE CANVAS AND SCREENSHOTS ###########

    # Create the drawing canvas

    button = tk.Button(text=tr("If you finished, press the button", "Ak ste skončili, kliknite pre pokračovanie"), command=lambda: quit_program(), height=4)
    button.pack(side="bottom")

    canvas = tk.Canvas(root, bg='white')
    canvas.pack(anchor='center', expand=True, fill="both")

    return (root, canvas)   
############ FUNCTIONS TO DRAW AND TO SAVE THE FINAL DRAWINGS #############
# Define the event handler for mouse movements
def on_mouse_move(event):
    global prev_x, prev_y, stroke_count, do_one_time, latency, x, y, t, start_drawing_time

    while do_one_time:
        latency = time.time() - start
        root.after(53000, lambda: time.sleep(2))
        root.after(55000, lambda: alert_window())
        root.after(65000, lambda: quit_program())
        start_drawing_time = time.time()*1000
        do_one_time = False
        #print(latency)


    c_x = event.x
    c_y = event.y
    c_t = time.time()*1000

    x.append(c_x)
    y.append(c_y)
    temp = int(c_t-start_drawing_time)
    t.append(temp)

    if prev_x is not None and prev_y is not None:
        canvas.create_line(prev_x, prev_y, c_x, c_y, fill=draw_color, width=draw_size)
        detailed_strokes.append([c_x, c_y, c_t])
    prev_x = c_x
    prev_y = c_y


# Define the event handler for releasing the mouse button
def on_mouse_release(event):
    global prev_x, prev_y, stroke_count, total_drawing_time, x, y, t, strokes
    #Appending invalid to signal end of stroke
    detailed_strokes.append([-1, -1, -1])
    prev_x = None
    prev_y = None

    strokes.append([x, y, t])

    x = []
    y = []
    t = []
    
    stroke_count += 1



def alert_window():
    global temp, margin, prev_y, prev_x

    ### PSYCHOPY
    widthPix = 1920
    heightPix = 1080
    monitorWidth = 50.2
    viewdist = 25.4
    monitorname = 'testMonitor'
    scrn = 1
    mon = monitors.Monitor(monitorname, width=monitorWidth, distance=viewdist)
    mon.setSizePix((widthPix, heightPix))

    win = visual.Window(
        monitor=mon,
        size=(widthPix, heightPix),
        color=(1, 1, 1),
        colorSpace='rgb',
        units='deg',
        screen=scrn,
        allowGUI=False,
        fullscr=True
    )

    ###

    temp = time.time() - start

    text = visual.TextStim(win, text=tr("Time to finish your drawing...", "Je čas aby ste dokončili svoju kresbu…"), color=(-1, -1, -1), pos=(0.0, 11.0),
                           colorSpace='rgb', bold=False, height=3.5, anchorHoriz="center", wrapWidth=500)
    text.draw()
    win.flip()
    time.sleep(3)
    win.close()

    margin = time.time()
    prev_y = None
    prev_x = None

def quit_program():
    global total_drawing_time, latency, stroke_count, temp, margin, root

    data = []

    time.sleep(0.5)


    ImageGrab.grab().crop((65, 65, 1920, 1015)).save(participant + "/" + category + ".png")

    if temp > 0:
        #Pretty sure this is broken: Fix.
        temp2 = time.time() - margin
        total_drawing_time = temp + temp2
    else:
        total_drawing_time = time.time() - start

    data = np.array([latency, total_drawing_time, stroke_count])

    print(','.join(map(str, data)))

    timestamp = str(datetime.fromtimestamp(time.time()))

    strokes_data = {
        'word': category,
        'condition': condition,
        'country': country,
        'timestamp': timestamp,
        'strokes': strokes,
        'detailed_strokes' : detailed_strokes
    }

    # This is super ugly, use dependency for that
    if os.path.isfile(strokes_file_path):
        with open(strokes_file_path) as f:
            data = []
            reader = ndjson.reader(f)
            for i in reader:
                data.append(i)
        data.append(strokes_data)

        with open(strokes_file_path, "w") as f:
            writer = ndjson.writer(f, ensure_ascii=False)
            for d in data:
                writer.writerow(d)

    else:
        open(strokes_file_path, "x")
        with open(strokes_file_path, "w") as file:
            json.dump(strokes_data, file)

    root.destroy()

    



######################### END OF THE FUNCTIONS #############################

