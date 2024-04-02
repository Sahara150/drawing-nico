#!/usr/bin/env python3

import os
import time
import datetime
from psychopy import monitors, visual, event
import sys
import numpy as np
import subprocess
from datetime import datetime

code_path = "C:/Users/haras/Uni_SourceCodes/NICO/drawing-nico/"   #for Bratislava

images_dir = code_path+"Images/"
experiment_dir = images_dir + "Experiments_raw/"
script_path = code_path + "drawing.py"
category = "test"
category_counter = 1

latency_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
total_drawing_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
number_of_strokes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

#Create image dir if not yet existant
if os.path.isdir(images_dir):
    print("folder already exist")
else:
    os.mkdir(images_dir)
    os.mkdir(experiment_dir)

####### CHANGE THE PATH
now = datetime.now()
date_hour = now.strftime("_%d-%m-%Y_%H-%M-%S")
participant_dir = "nicodraws" + str(date_hour)
python_path = "C:/ProgramData/miniconda3/python"
path_folder_participant = images_dir + participant_dir
os.mkdir(path_folder_participant)

global win

# function to wait for the touch of the mouse
def wait_touch():
    myMouse.clickReset()
    buttons = myMouse.getPressed()
    print(buttons)
    while buttons[0] == False | buttons[1] == False | buttons[2] == False:
        buttons = myMouse.getPressed()

    print(buttons)
    print("click")
    time.sleep(1)

    return


def drawing_activity(i):
    global category, category_counter

    win.close()
    print("window closed, ready to open drawing")
    print(f"{category}{category_counter}")
    
    # for Bratislava: ToDo, parameterize again when transferring to class
    p = subprocess.Popen([python_path, script_path, f"{category}{category_counter}",
                        path_folder_participant, "no_robot", "sk", experiment_dir], stdout=subprocess.PIPE)
    p.wait()

    category_counter+=1
    
    output = []
    output = p.stdout.read()

    array = np.fromstring(output.decode(), dtype=float, sep=',')

    number_of_strokes[i] = array[2]

    #Why do we call it that often? Is this really necessary?
    configure()

    return


def configure():
    global win, widthPix, heightPix, monitorWidth, viewdist, monitorname, scrn, mon, myMouse, myKey

    widthPix = 1920
    heightPix = 1080
    monitorWidth = 50.2
    #monitorWidth = 30.9
    viewdist = 25.4
    monitorname = 'testMonitor'
    scrn = 1

    mon = monitors.Monitor(monitorname, width=monitorWidth, distance=viewdist)
    mon.setSizePix((widthPix, heightPix))

    win = visual.Window(
        monitor=mon,
        size=(widthPix, heightPix),
        color=(-0.4, -0.4, 1),
        colorSpace='rgb',
        units='deg',
        screen=scrn,
        allowGUI=True,
        fullscr=True
    )

    myMouse = event.Mouse(win)
    #myMouse.setPos(newPos=(300, 300))

    return



def main():

    configure()

    #Running 10 times to generate some samples
    for i in range(0,10):
        drawing_activity(i)

    wait_touch()

if __name__ == '__main__':
    main()

    sys.exit()
