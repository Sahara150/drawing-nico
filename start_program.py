from drawing import open_canvas
import os
from datetime import datetime
import time
import threading
from global_static_vars import images_dir, experiment_dir, line_args
from global_static_vars import categories_no_imitation, categories_imitation, categories_sk_imitation
from helper_functions import flatten_data, transform_coordinates, rescale_and_shift_image, calculate_error
from file_helper import read_newest_results, append_to_ndjson
from canvas_functions import create_canvas_with_data_from_strokes, create_canvas_with_flattened_data, open_canvas_for_robot, strokes, ask_question
from robot_setup import load_robot, look_down, robot_draws_strokes
from texts import tr, rating_scale_text
#from nntest import compare_old_to_new

def setup_for_participant():
    #Create image dir if not yet existant
    if os.path.isdir(images_dir):
        print("folder already exist")
    else:
        os.mkdir(images_dir)
        os.mkdir(experiment_dir)

    ## Create new folder for participant
    now = datetime.now()
    date_hour = now.strftime("_%d-%m-%Y_%H-%M-%S")
    participant_dir = line_args['participant'] + str(date_hour)
    path_folder_participant = images_dir + participant_dir
    os.mkdir(path_folder_participant)

    line_args['path_folder_participant'] = path_folder_participant

def user_draws():
    for i in range(0,1):
        open_canvas(f"robot_repeats_{i}", line_args['path_folder_participant'], "robot")

def draw_without_imitation():
    for index, category in enumerate(categories_no_imitation):
        category_text = categories_sk_imitation[index] if line_args['country'] == "sk" else category
        show_category_prompt(category_text)
        look_down(robot)
        open_canvas(category, line_args['path_folder_participant'], "no_robot")
        ask_questions(category_text, category)

def draw_with_imitation():
    for index, category in enumerate(categories_imitation):
        for i in range(0,2):
            category_text = categories_sk_imitation[index] if line_args['country'] == "sk" else category
            show_category_prompt(category_text)
            look_down(robot)
            open_canvas(category, line_args['path_folder_participant'], "robot")
        
            data = read_newest_results(category)
            flattened_data = flatten_data(data)
            # Setting true for now, as we will use the learned model with Perceptrons
            mirrored_data = transform_coordinates(flattened_data, True)
            (rescaled_data, rescale_factor, shift_x, shift_y) = rescale_and_shift_image(mirrored_data)
            rescaled_data = list(rescaled_data)
            drawing_robot_thread = threading.Thread(target = robot_draws_strokes, args = (rescaled_data,))
            drawing_robot_thread.start()
            open_canvas_for_robot(rescaled_data, category)
            print("Calculating error now")
            error = calculate_error(rescaled_data, strokes)
            drawing_data = {
                'participant': line_args['participant'],
                'trial': i,
                'rescale_factor': rescale_factor,
                'shift_x': shift_x,
                'shift_y': shift_y,
                'strokes': strokes,
                'error': error
            }
            strokes_file_path = experiment_dir + "raw_" + category + "_robot.ndjson"
            append_to_ndjson(strokes_file_path, drawing_data)
            ask_questions(category_text, category, True)
       
def ask_questions(category : str, category_en : str, robot_imitated : bool = False):
    text_self = tr("How much do you like your drawing of the ","Ako veľmi sa Vám páči Váš výkres: ") + category + "? \n"
    text_self.append(rating_scale_text())
    image_path_self = line_args['path_folder_participant'] + "/" + category_en + ".png"
    rating_self = ask_question(text_self, image_path_self)
    if robot_imitated:
        text_robot = tr("How much do you like the robots drawing of the ", "Ako veľmi sa vám páči kresba robotov s: " + category + "? \n")
        text_robot.append(rating_scale_text())
        image_path_robot = line_args['path_folder_participant'] + "/" + category + "_drawing_robot.png"
        rating_robot = ask_question(text_robot, image_path_robot)
        return (rating_self, rating_robot)
    else:
        return (rating_self, None)

def show_category_prompt(category : str):
    pass

#line_args['country'] = "sk"
# We're not putting this in an extra agent, as the robot should just wake up and look down
# once in the beginning
robot = load_robot()
# Sleep 3 seconds til robot got woken up
#time.sleep(3)
#look_down(robot)
setup_for_participant()
#user_draws()
data = read_newest_results("robot_repeats_0")
#data = read_newest_results("robot_results")
flattened_data = flatten_data(data)
create_canvas_with_data_from_strokes(data)
#create_canvas_with_flattened_data(flattened_data)
# Setting true for now, as we will use the learned model with Perceptrons
#mirrored_data = transform_coordinates(flattened_data, True)
#(rescaled_data, rescale_factor, shift_x, shift_y) = rescale_and_shift_image(mirrored_data)
#rescaled_data = list(rescaled_data)
#drawing_robot_thread = threading.Thread(target = robot_draws_strokes, args = (rescaled_data,))
#drawing_robot_thread.start()
#open_canvas_for_robot(rescaled_data)
#print("Calculating error now")
#error = calculate_error(rescaled_data, strokes)
#print(f"Error is: {error}")