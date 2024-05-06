#!/usr/bin/env python3

import os
import time
import pandas as pd
import random
import wx
from psychopy import event, visual, monitors, core
import datetime
import sys
import numpy as np
import subprocess
import csv
from datetime import datetime
import json
import ndjson
from nico.main import start_video, stop_video, enableTorque, disableTorque
from nico.CameraAgent import CameraAgent
from nico.RecorderAgent import RecorderAgent
from nico.ViewerAgent import ViewerAgent


participant = sys.argv[1]
country = sys.argv[2]

def tr(a,b):
    if country == 'SK' or country == 'sk':
        return b
    else:
        return a

condition = sys.argv[3]


CameraAgent('HD Pro Webcam C920',1,'humanImage',fps=10)
time.sleep(1)
CameraAgent('HD Pro Webcam C920',0,'robotImage',fps=10)
time.sleep(1)
ViewerAgent('robotImage','humanImage', 'camera', 'wide camera', 'points','face point','point') # view image from camera
time.sleep(1)
RecorderAgent()
time.sleep(1)
disableTorque() # do not move

input("Press Enter to continue...")

start_video(participant + '_' + condition)


#code_path = "/usr/local/src/robot/cognitiveinteraction/stimulivalidation/"  #for Italy
code_path = "C:/Experiment/Drawing/"   #for Bratislava

images_dir = code_path+"Images/"
experiment_dir = images_dir + "Experiments_raw/"
script_path = code_path + "drawing.py"
script_path_trial = code_path + "drawing_trial.py"
clickToContinue = tr("Click to continue","Kliknite pre pokračovanie")

if os.path.isdir(images_dir):
    print("folder already exist")
else:
    os.mkdir(images_dir)
    os.mkdir(experiment_dir)

####### CHANGE THE PATH
now = datetime.now()
date_hour = now.strftime("_%d-%m-%Y_%H-%M-%S")
participant_dir = participant + str(date_hour)
path_folder_participant = images_dir + participant_dir
os.mkdir(path_folder_participant)

seq_1 = [0, 1, 2]
seq_2 = [3, 4, 5, 6, 7, 8, 9, 10, 11]
seq_3 = [12, 13, 14]

random.shuffle(seq_1)
random.shuffle(seq_2)
random.shuffle(seq_3)

categories = [tr('Sheep','Ovca'), tr('Bus','Autobus'), tr('Bee','Včela'),
              tr('Face','Tvár'), tr('Computer','Počítač'), tr('Duck','Kačka'),
              tr('Penguin','Tučniak'), tr('Drums','Bicie'), tr('Ambulance','Sanitka'),
              tr('Crab','Krab'), tr('Ant','Mravec'), tr('Alarm Clock','Budík'),
              tr('Sheep','Ovca'), tr('Bus','Autobus'), tr('Bee','Včela')]
categories_eng = ['Sheep', 'Bus', 'Bee',
              'Face', 'Computer', 'Duck',
              'Penguin', 'Drums', 'Ambulance',
              'Crab', 'Ant', 'Alarm Clock',
              'Sheep', 'Bus', 'Bee']

global win

####### CHANGE THE PATH

drawing_enjoyment = 0.0
drawing_frequency = 0.0
drawing_percentage = 0.0

difficulty_ranking = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
enjoyment_ranking = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
likeability_ranking = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

latency_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
total_drawing_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
number_of_strokes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


def save_rankings(n):

    if n <= 11:
        path_var = images_dir + "/" + str(categories_eng[n]) + "_quantitative_data.ndjson"
    else:
        path_var = images_dir + "/" + str(categories_eng[n]) + "_repetition_quantitative_data.ndjson"

    ranking_data = {
        'Participant_ID': participant,
        'Country': country,
        'Condition': condition,
        'Latency_time': round(latency_time[n], 2),
        'Total_time': round(total_drawing_time[n], 2),
        'Number_of_Strokes': number_of_strokes[n],
        'Enjoyment_ranking': enjoyment_ranking[n],
        'Difficulty_ranking': difficulty_ranking[n],
        'Likeability_ranking': likeability_ranking[n]
    }

    if os.path.isfile(path_var):
        with open(path_var) as f:
            data = []
            reader = ndjson.reader(f)
            for i in reader:
                data.append(i)
        data.append(ranking_data)

        # Writing items to a ndjson file
        with open(path_var, 'w') as f:
            writer = ndjson.writer(f, ensure_ascii=False)
            for d in data:
                writer.writerow(d)

    else:
        open(path_var, "x")
        with open(path_var, "w") as file:
            json.dump(ranking_data, file)

    return

def drawing_questions(n):
    text = visual.TextStim(win, text=tr("How difficult it was to draw the ","Aké náročné bolo nakresliť: ") + categories[n] + "? \n" +
                            tr("(1 - not difficult, 7 - extremely difficult)","(1 - vôbec to nebolo náročné, 7 - bolo to extrémne náročné)"), color=(1, 1, 1),
                           pos=(0.0, 11.0), colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center", font='Helvetica',
                           wrapWidth=400)
    
    text.draw()

    button_continue = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                                        fillColor=[-0.3, -0.3, -0.3],
                                        pos=[0, -350], size=(400, 150), units='pix')
    #button_continue.draw()

    slider = visual.Slider(win, ticks=(0, 7), labels=(0, 7), granularity=0.1, pos=(0, -100), size=(1000, 50), font='Helvetica',
                           units='pix')

    slider.setMarkerPos(200)
    slider.getMouseResponses()
    slider.setReadOnly(False, log=None)
    slider.draw()
    win.flip()

    touch = False
    rating = None
    print(slider.markerPos)

    while touch == False:
        if slider.getMouseResponses():
            rating = slider.getRating()
            slider.setMarkerPos(rating)
            button_continue.draw()
            text.draw()
            slider.draw()
            win.flip()

        if myMouse.isPressedIn(button_continue) and rating != None:
            difficulty_ranking[n] = rating
            touch = True
    
    blue_window()


    text = visual.TextStim(win, text=tr("How much did you enjoy drawing the ", "Ako veľmi sa Vám páčilo kresliť: ") + categories[n] + "? \n" +
                            tr("(1 - not enjoyed, 7 - extremely enjoyed)", "(1 - vôbec sa mi nepáčilo, 7 - veľmi sa mi páčilo)"),
                           color=(1, 1, 1), pos=(0.0, 11.0), colorSpace='rgb', font='Helvetica', bold=False, height=2.5, anchorHoriz="center",
                           wrapWidth=400)
    text.draw()

    button_continue = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                                        fillColor=[-0.3, -0.3, -0.3],
                                        pos=[0, -350], size=(400, 150), units='pix')
    #button_continue.draw()

    slider = visual.Slider(win, ticks=(0, 7), labels=(0, 7), granularity=0.1, pos=(0, -100), size=(1000, 50), font='Helvetica',
                           units='pix')


    slider.setMarkerPos(200)
    slider.getMouseResponses()
    slider.setReadOnly(False, log=None)
    slider.draw()
    win.flip()

    touch = False
    rating = None
    print(slider.markerPos)

    while touch == False:
        if slider.getMouseResponses():
            rating = slider.getRating()
            slider.setMarkerPos(rating)
            button_continue.draw()
            text.draw()
            slider.draw()
            win.flip()

        if myMouse.isPressedIn(button_continue) and rating != None:
            enjoyment_ranking[n] = rating
            touch = True
    
    blue_window()

    text = visual.TextStim(win, text=tr("How much do you like your drawing of the ","Ako veľmi sa Vám páči Váš výkres: ") + categories[n] + "? \n" +
                            tr("(1 - not liked, 7 - liked a lot)", "(1 - vôbec sa mi nepáči, 7 - veľmi sa mi páči)"), font='Helvetica',
                           color=(1, 1, 1), pos=(0.0, 15.0), colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center",
                           wrapWidth=400)
    text.draw()

    if n <= 11:
        image = visual.ImageStim(win, image=path_folder_participant + "/" + categories_eng[n] + ".png", size=(600, 337),
                             units='pix', pos=(0.0, -5.0))
        image.draw()
    else:
        image = visual.ImageStim(win, image=path_folder_participant + "/" + categories_eng[n] + "_repetition.png", size=(600, 337),
                             units='pix', pos=(0.0, -5.0))
        image.draw()

    button_continue = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                                        fillColor=[-0.3, -0.3, -0.3],
                                        pos=[0, -450], size=(400, 150), units='pix')
    #button_continue.draw()

    slider = visual.Slider(win, ticks=(0, 7), labels=(0, 7), granularity=0.1, pos=(0, -250), size=(1000, 50), font='Helvetica',
                           units='pix')

    slider.setMarkerPos(200)
    slider.getMouseResponses()
    slider.setReadOnly(False, log=None)
    slider.draw()
    win.flip()

    touch = False
    rating = None
    print(slider.markerPos)

    while touch == False:
        if slider.getMouseResponses():
            rating = slider.getRating()
            slider.setMarkerPos(rating)
            button_continue.draw()
            text.draw()
            image.draw()
            slider.draw()
            win.flip()

        if myMouse.isPressedIn(button_continue) and rating != None:
            likeability_ranking[n] = rating
            touch = True
    
    blue_window()
    save_rankings(n)


    return


def drawing_activity(i):

    win.close()
    print("window closed, ready to open drawing")
    print(categories[i])

    if i <= 11:

        #for Italy
        #p = subprocess.Popen(["python3", script_path, categories[i], path_folder_participant,
        #                condition, country, experiment_dir], stdout=subprocess.PIPE)

        # for Bratislava
        p = subprocess.Popen(["C:/Experiment/Drawing/drawing_venv/Scripts/python", script_path, categories_eng[i],
                           path_folder_participant, condition, country, experiment_dir], stdout=subprocess.PIPE)
        p.wait()
    else:
        cat_repetition = categories_eng[i]+"_repetition"

        #p = subprocess.Popen(["python3", script_path, cat_repetition, path_folder_participant,
        #        condition, country, experiment_dir], stdout=subprocess.PIPE)

        # for Bratislava
        p = subprocess.Popen(["C:/Experiment/Drawing/drawing_venv/Scripts/python", script_path, cat_repetition,
                              path_folder_participant, condition, country, experiment_dir], stdout=subprocess.PIPE)
        p.wait()


    output = []
    output = p.stdout.read()

    array = np.fromstring(output.decode(), dtype=float, sep=',')

    latency_time[i] = array[0]    	
    total_drawing_time[i] = array[1]
    number_of_strokes[i] = array[2]

    configure()

    text = visual.TextStim(win, text=tr("Now please answer to some questions.", "Teraz, prosím, odpovedzte na zopár otázok."), color=(1, 1, 1), pos=(0.0, 11.0),
                           colorSpace='rgb', bold=False, height=2.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)
    text.draw()
    
    button = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb', fillColor=[-0.3, -0.3, -0.3],
                              pos=[0, -250], size=(400, 150), units='pix')
    button.draw()
    
    win.flip()
    
    touch = False
    
    while touch==False:
        if myMouse.isPressedIn(button):
            touch=True

    blue_window()

    drawing_questions(i)

    return


def drawing_task(n):

    text = visual.TextStim(win, text=tr("Are you ready to draw?","Ste pripravení začať kresliť?"), color=(1, 1, 1), pos=(0.0, 11.0),
                           colorSpace='rgb', bold=False, height=2.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)
    text.draw()
    
    button = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb', fillColor=[-0.3, -0.3, -0.3],
                              pos=[0, -250], size=(400, 150), units='pix')
    button.draw()
    
    win.flip()
    
    touch=False
    
    while touch==False:
        if myMouse.isPressedIn(button):
            touch=True

    time.sleep(0.2)
    buttons = myMouse.getPressed()
    myMouse.clickReset(buttons)


    text = visual.TextStim(win, text=tr("Please draw with your finger the...\n","Prosím, prstom nakreslite...\n"), color=(1, 1, 1), pos=(0.0, 11.0),
                           colorSpace='rgb', bold=False, height=2.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)

    text2 = visual.TextStim(win, text=categories[n], color=(1, -0.7, -0.7), pos=(0.0, -1.0),
                           colorSpace='rgb', bold=True, height=4.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)

    text.draw()
    text2.draw()

    win.flip()

    time.sleep(4)

    drawing_activity(n)

    return




def artistic_questions():
    global drawing_enjoyment, drawing_frequency, drawing_percentage

    text = visual.TextStim(win, text=tr("How much do you enjoy free-hand drawing? \n (1 - extremely little, 7 - extremely much) \n","Ako veľmi sa Vám páčilo kreslenie prstom? \n (1 - vôbec sa mi nepáčilo, 7 - veľmi sa mi páčilo) \n") +
                           tr("(click on the slider and then drag the marker)","(Kliknite na posuvník a potom potiahnite značku)"), color=(1, 1, 1),
                           pos=(0.0, 11.0), colorSpace='rgb', bold=False, height=2.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)
    text.draw()

    button_continue = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                                        fillColor=[-0.3, -0.3, -0.3],
                                        pos=[0, -350], size=(400, 150), units='pix')
    #button_continue.draw()

    slider = visual.Slider(win, ticks=(0, 7), labels=(0, 7), granularity=0.1, pos=(0, -100), size=(1000, 50), font='Helvetica',
                           units='pix')

    slider.setMarkerPos(200)
    slider.getMouseResponses()
    slider.setReadOnly(False, log=None)
    slider.draw()
    win.flip()

    touch = False
    rating = None
    print(slider.markerPos)

    while touch == False:
        if slider.getMouseResponses():
            rating = slider.getRating()
            slider.setMarkerPos(rating)
            button_continue.draw()
            text.draw()
            slider.draw()
            win.flip()

        if myMouse.isPressedIn(button_continue) and rating != None:
            drawing_enjoyment = rating
            touch = True
    
    blue_window()

    text = visual.TextStim(win, text=tr("How often do you draw sketches? \n (1 - extremely little, 7 - extremely much)", "Ako často kreslíte? \n (1 - veľmi zriedkavo, 7 - veľmi často)"), color=(1, 1, 1),
                           pos=(0.0, 11.0), colorSpace='rgb', bold=False, height=2.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)
    text.draw()

    button_continue = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                                        fillColor=[-0.3, -0.3, -0.3],
                                        pos=[0, -350], size=(400, 150), units='pix')
    #button_continue.draw()

    slider = visual.Slider(win, ticks=(0, 7), labels=(0, 7), granularity=0.1, pos=(0, -100), size=(1000, 50), font='Helvetica',
                           units='pix')


    slider.setMarkerPos(200)
    slider.getMouseResponses()
    slider.setReadOnly(False, log=None)
    slider.draw()
    win.flip()

    touch = False
    rating = None
    print(slider.markerPos)

    while touch == False:
        if slider.getMouseResponses():
            rating = slider.getRating()
            slider.setMarkerPos(rating)
            button_continue.draw()
            text.draw()
            slider.draw()
            win.flip()

        if myMouse.isPressedIn(button_continue) and rating != None:
            drawing_frequency = rating
            touch = True
    
    blue_window()

    text = visual.TextStim(win, text=tr("Imagine other 100 people drawing the same sketches as yours: \n","Predstavte si, že ďalších 100 ľudí kreslí rovnaké náčrty ako Vy: \n") +
    tr(" how many of them do you think will draw better than you? \n "," Koľko z nich podľa Vás nakreslí lepšie ako Vy? \n "), color=(1, 1, 1), pos=(0.0, 11.0), colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center",
                           wrapWidth=400, font='Helvetica')
    text.draw()

    button_continue = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                               fillColor=[-0.3, -0.3, -0.3],
                               pos=[0, -350], size=(400, 150), units='pix')
    #button_continue.draw()

    slider = visual.Slider(win, ticks=(0, 100), labels=(0, 100), granularity=0.1, pos=(0, -100), size=(1000, 50), font='Helvetica',
                           units='pix')

    slider.setMarkerPos(200)
    slider.getMouseResponses()
    slider.setReadOnly(False, log=None)
    slider.draw()
    win.flip()

    touch = False
    rating = None
    print(slider.markerPos)

    while touch == False:
        if slider.getMouseResponses():
            rating = slider.getRating()
            slider.setMarkerPos(rating)
            button_continue.draw()
            text.draw()
            slider.draw()
            win.flip()

        if myMouse.isPressedIn(button_continue) and rating != None:
            drawing_percentage = rating
            touch = True

    blue_window()

    return


def blue_window():
    blue_poly = visual.Polygon(win, edges=4, fillColor=[-0.4, -0.4, 1], colorSpace='rgb', pos=[0, 0], size=[4000, 4000], units='pix', ori=0)
    blue_poly.draw()
    win.flip()  # show the stim
    time.sleep(0.05)

    return


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

    #subprocess.run(["xrandr", "--output", "eDP", "--off"])
    
    configure()

    text = visual.TextStim(win, text=tr("Welcome!\nThis is a first trial to help\n", "Vitajte! \nToto je prvá skúška, ktorá Vám pomôže\n") +
                                     tr("you understand how the drawing activity will work.", "porozumieť ako bude aktivita prebiehať")
                                     , color=(1, 1, 1), pos=(0.0, 11.0), font='Helvetica', colorSpace='rgb', bold=False, height=2.5, 
                                     anchorHoriz="center", wrapWidth=400)
    print("the font of our text is ", text.font)
    text.draw()

    button = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                               fillColor=[-0.3, -0.3, -0.3],
                               pos=[0, -250], size=(400, 150), units='pix')
    button.draw()

    win.flip()


    touch = False

    while touch == False:
        #print(myMouse.isPressedIn(button))

        if myMouse.isPressedIn(button):
            print(myMouse.isPressedIn(button))
            touch = True

    blue_window()

    text = visual.TextStim(win, text=tr("When you are ready, press the button and\n", "Akonáhle budete pripravení stlačte tlačidlo\n") +
                                     tr("a subject to be drawn will appear on the screen.", "a objekt, ktorý máte nakresliť sa ukáže na obrazovke.")
                                     , color=(1, 1, 1), pos=(0.0, 11.0), font='Helvetica',
                           colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center", wrapWidth=400)
    text.draw()

    button = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                               fillColor=[-0.3, -0.3, -0.3],
                               pos=[0, -250], size=(400, 150), units='pix')
    button.draw()

    win.flip()

    touch = False

    while touch == False:
        if myMouse.isPressedIn(button):
            touch = True

    blue_window()

    text = visual.TextStim(win, text=tr("Please draw with your finger the...\n", "Prosím, prstom nakreslite...\n"), color=(1, 1, 1), pos=(0.0, 11.0),
                           colorSpace='rgb', bold=False, height=2.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)

    text2 = visual.TextStim(win, text=tr("Tree", "Strom"), color=(1, -0.7, -0.7), pos=(0.0, -1.0),
                            colorSpace='rgb', bold=True, height=4.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)

    text.draw()
    text2.draw()

    win.flip()

    time.sleep(4)

    win.close()

    #for Italy
    #p = subprocess.Popen(["python3", script_path_trial])

    p = subprocess.Popen(["C:/Experiment/Drawing/drawing_venv/Scripts/python", script_path_trial])
    p.wait()

    configure()

    text = visual.TextStim(win, text=tr("Great!\n Is everything clear? Then you can\n", "Výborne!\n Je všetko jasné? Ak áno, môžeme pokračovať\n") +
                                     tr("proceed with the actual experiment.", "s experimentom.")
                           , color=(1, 1, 1), pos=(0.0, 11.0), font='Helvetica',
                           colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center", wrapWidth=400)
    text.draw()

    button = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb',
                               fillColor=[-0.3, -0.3, -0.3],
                               pos=[0, -250], size=(400, 150), units='pix')
    button.draw()

    win.flip()

    touch = False

    while touch == False:
        if myMouse.isPressedIn(button):
            touch = True

    blue_window()

    text = visual.TextStim(win, text=tr("Welcome!\nWe will ask you to draw several pictures\n", "Vitajte!\n Požiadame Vás, aby ste nakreslili pár obrázkov\n") +
                                     tr("and then answer some simple questions.\n", "a potom odpovedali na zopár otázok.\n") +
                                     tr("Are you ready? ", "Ste pripravení? ")
                                     , color=(1, 1, 1), pos=(0.0, 11.0), font='Helvetica',
                           colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center", wrapWidth=400)
    text.draw()
    
    button = visual.ButtonStim(win, text=clickToContinue, color=[1, 1, 1], colorSpace='rgb', fillColor=[-0.3, -0.3, -0.3],
                              pos=[0, -250], size=(400, 150), units='pix') 
    button.draw()
    
    win.flip()

    touch=False
    
    while touch==False:
        if myMouse.isPressedIn(button):
            touch=True

    blue_window()

    artistic_questions()

    for i in seq_1:
        drawing_task(i)

    for i in seq_2:
        drawing_task(i)

    for i in seq_3:
        drawing_task(i)


    path_var = code_path + "/artistic_skills.ndjson"

    artistic_data = {
        'Participant_ID': participant,
        'Country': country,
        'Condition': condition,
        'Artistic_enjoyment': drawing_enjoyment,
        'Artistic_frequency': drawing_frequency,
        'Artistic_percentage': drawing_percentage,
        'Average_latency_time': round(np.mean(latency_time), 2),
        'Average_total_time': round(np.mean(total_drawing_time), 2),
        'Average_number_strokes': round(np.mean(number_of_strokes), 2),
        'Average_enjoyment_ranking': round(np.mean(enjoyment_ranking), 2),
        'Average_difficulty_ranking': round(np.mean(difficulty_ranking), 2),
        'Average_likeability_ranking': round(np.mean(likeability_ranking), 2)
    }

    if os.path.isfile(path_var):
        with open(path_var) as f:
            data = []
            reader = ndjson.reader(f)
            for i in reader:
                data.append(i)
        data.append(artistic_data)

        # Writing items to a ndjson file
        with open(path_var, 'w') as f:
            writer = ndjson.writer(f, ensure_ascii=False)
            for d in data:
                writer.writerow(d)

    else:
        open(path_var, "x")
        with open(path_var, "w") as file:
            json.dump(artistic_data, file)

    text = visual.TextStim(win, text=tr("Thank you very much!", "Ďakujeme veľmi pekne!"), color=(1, 1, 1), pos=(0.0, 11.0),
                           colorSpace='rgb', bold=False, height=2.5, font='Helvetica', anchorHoriz="center", wrapWidth=400)
    text.draw()
    win.flip()
    
    stop_video()

    wait_touch()
    
    #subprocess.run(["xrandr", "--output", "eDP", "--mode", "1920x1080", "--panning", "1920x1080", "--pos", "1920x0", "--primary"])

if __name__ == '__main__':
    main()

    sys.exit()
