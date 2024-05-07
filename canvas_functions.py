import tkinter as tk
from global_static_vars import draw_color, draw_size
from PIL import ImageGrab
from global_static_vars import width_side, height_side, line_args, experiment_dir
from file_helper import append_to_ndjson
from psychopy import event, visual, monitors
from texts import clickToContinue, tr
import time
from global_static_vars import monitorname, monitorWidth, viewdist, scrn

global win
######### CANVAS HELPERS ###########
prev_x = None
prev_y = None
canvas = None
root = None
category = None
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
    for stroke in data[4:10]:
    #for stroke in data:
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
    print(f"Strokes length is {len(strokes)}")
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

def open_canvas_for_robot(data : list[list[list[int]]], _category : str):
    global canvas, root, category

    category = _category
    #Reset variables so it deletes data of last drawing
    print("Reset variables")
    reset_variables()

    (root, canvas) = setup_UI()
    draw_template(data, canvas)
    
    canvas.bind('<ButtonPress-1>', on_mouse_down)

    # Bind the mouse movement event to the canvas
    canvas.bind('<B1-Motion>', on_mouse_move)
    
    # Bind the mouse movement event to the canvas
    canvas.bind('<B3-Motion>', on_mouse_move)

    canvas.bind('<ButtonRelease-3>', on_mouse_release)
    
    # Bind the mouse release event to the canvas
    canvas.bind('<ButtonRelease-1>', on_mouse_release)

    root.bind("<<close_canvas>>", close_canvas_event)
    root.mainloop()

def close_canvas():
    ImageGrab.grab().crop((0, 0, width_side, height_side)).save(line_args['path_folder_participant'] + "/" + category + "_drawing_robot.png")

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
    global prev_x, prev_y, canvas, root, stroke_count
    prev_x = None
    prev_y = None
    canvas = None
    root = None
    x.clear()
    y.clear()
    strokes.clear()
    stroke_count = 0

### Visual PY functions ###

def configure_and_show():
    global win, myMouse
    try:
        # Try to flip the window
        win.flip()
    except Exception as e:
        # No window open, open window
        mon = monitors.Monitor(monitorname, width=monitorWidth, distance=viewdist)
        mon.setSizePix((width_side, height_side))

        win = visual.Window(
            monitor=mon,
            size=(width_side, height_side),
            color=(-0.4, -0.4, 1),
            colorSpace='rgb',
            units='deg',
            screen=scrn,
            allowGUI=True,
            fullscr=True
        )

        myMouse = event.Mouse(win)
        # myMouse.setPos(newPos=(300, 300))

def ask_question(question : str, image_path : str):
    configure_and_show()
        
    text = visual.TextStim(win, text= question, color=(1, 1, 1), font='Helvetica', 
                           pos=(0.0, 15.0), colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center", wrapWidth=400)
    text.draw()

    image = visual.ImageStim(win, image=image_path, size=(600, 337),
                             units='pix', pos=(0.0, -5.0))
    image.draw()

    button_continue = visual.ButtonStim(win, text=clickToContinue(), color=[1, 1, 1], colorSpace='rgb',
                                        fillColor=[-0.3, -0.3, -0.3], pos=[0, -450], size=(400, 150), units='pix')

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
            touch = True
            return rating
        
def show_category_prompt(category : str, second_time : bool = False):

    time.sleep(1.5)
    if second_time:
        textShown = tr(f"Are you ready to draw {category} for the robot a second time?", f"Ste pripravení nakresliť {category} pre robota druhýkrát?")
    else: 
        textShown = tr("Are you ready to draw?","Ste pripravení začať kresliť?")
    text = visual.TextStim(win, text=textShown, color=(1, 1, 1), pos=(0.0, 11.0),
                           colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center", font='Helvetica', wrapWidth=400)
    text.draw()
    button = visual.ButtonStim(win, text=clickToContinue(), color=[1, 1, 1], colorSpace='rgb',
                               fillColor=[-0.3, -0.3, -0.3], pos=[0, -250], size=(400, 150), units='pix')
    button.draw()

    win.flip()

    touch = False

    while touch == False:
        if myMouse.isPressedIn(button):
            touch = True

    time.sleep(0.2)
    buttons = myMouse.getPressed()
    myMouse.clickReset(buttons)

    text = visual.TextStim(win, text=tr("Please draw with your finger the...\n","Prosím, prstom nakreslite...\n"), color=(1, 1, 1), pos=(0.0, 11.0),
                           colorSpace='rgb', bold=False, height=2.5, anchorHoriz="center", font='Helvetica', wrapWidth=400)

    text2 = visual.TextStim(win, text=category, color=(1, -0.7, -0.7), pos=(0.0, -1.0),
                            colorSpace='rgb', bold=True, height=4.5, anchorHoriz="center", font='Helvetica', wrapWidth=400)

    text.draw()
    text2.draw()

    win.flip()

    time.sleep(4)

    win.close()