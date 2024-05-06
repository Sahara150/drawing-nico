from drawing import open_canvas
import os
from datetime import datetime
import time
import threading
import numpy as np
from global_static_vars import images_dir, experiment_dir, line_args
from global_static_vars import categories_no_imitation, categories_sk_no_imitation, categories_fixed_imitation, categories_fixed_imitation_sk
from global_static_vars import categories_imitation_mixed, categories_sk_imitation_mixed, category_imitation_last, category_sk_imitation_last
from helper_functions import flatten_data, transform_coordinates, rescale_and_shift_image, calculate_error
from file_helper import read_newest_results, append_to_ndjson
from canvas_functions import create_canvas_with_data_from_strokes, create_canvas_with_flattened_data, open_canvas_for_robot, strokes
from canvas_functions import ask_question, configure_and_show, show_category_prompt
from robot_setup import load_robot, look_down, robot_draws_strokes
from texts import tr, rating_scale_text
import random
import sys
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
        open_canvas(f"tulip", line_args['path_folder_participant'], "robot")

def draw_without_imitation():
    configure_and_show()
    seq = [0, 1, 2, 3, 4]  # 0 is leaf, 1 is spider, 2 is pizza
    ratings = np.zeros(5)
    random.shuffle(seq)
    for index in seq:
        category = categories_no_imitation[index]
        category_text = categories_sk_no_imitation[index] if line_args['country'] == "sk" else category
        rating = drawing_activity(category, category_text)
        ratings[index] = rating[0][0]

    drawing_data = {
        'condition' : "no_repeat",
        'ratings' : list(ratings)
    }
    strokes_file_path = line_args['path_folder_participant'] + "/ratings_no_repeat.ndjson"
    append_to_ndjson(strokes_file_path, drawing_data)  

def draw_with_imitation():
    configure_and_show()
    ratings = np.zeros(7)
    for index, category in enumerate(categories_fixed_imitation):
        category_text = categories_fixed_imitation_sk[index] if line_args['country'] == "sk" else category
        rating = drawing_activity(category, category_text, True)
        ratings[index] = rating
    seq = [0, 1, 2, 3]    
    random.shuffle(seq)
    for index in seq:
        category = categories_imitation_mixed[index]
        category_text = categories_sk_imitation_mixed[index] if line_args['country'] == "sk" else category
        rating = drawing_activity(category, category_text, True)
        ratings[index+2] = rating

    category_text = category_sk_imitation_last if line_args['country']  == "sk" else category_imitation_last   
    rating = drawing_activity(category_imitation_last, category_text, True)
    ratings[-1] = rating
    drawing_data = {
        'condition' : 'repeat',
        'ratings_self_1' : list(ratings[:][0][0]),
        'ratings_robot_1' : list(ratings[:][0][1]),
        'ratings_self_2': list(ratings[:][1][0]),
        'ratings_robot_2' : list(ratings[:][1][1]),
    }
    strokes_file_path = line_args['path_folder_participant'] + "/ratings_repeat.ndjson"
    append_to_ndjson(strokes_file_path, drawing_data)

def drawing_activity(category : str, category_text: str, robot_active : bool = False):
    # TODO: We need to tell user that he draws it again for the robot, and it will repeat again
    repetitions = 2 if robot_active else 1
    ratings = []
    for i in range(0,repetitions):
        show_category_prompt(category_text)
        look_down(robot)
        open_canvas(category, line_args['path_folder_participant'], "second" if i == 2 else "first")

        if robot_active:
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
        ratings.append(ask_questions(category_text, category, robot_active))
    return ratings    

def ask_questions(category : str, category_en : str, robot_imitated : bool = False):
    text_self = tr("How much do you like your drawing of the ","Ako veľmi sa Vám páči Váš výkres: ") + category + "? \n"
    text_self += rating_scale_text()
    image_path_self = line_args['path_folder_participant'] + "/" + category_en + ".png"
    rating_self = ask_question(text_self, image_path_self)
    if robot_imitated:
        text_robot = tr("How much do you like the robots drawing of the ", "Ako veľmi sa vám páči kresba robotov s: " + category + "? \n")
        text_robot += rating_scale_text()
        image_path_robot = line_args['path_folder_participant'] + "/" + category + "_drawing_robot.png"
        rating_robot = ask_question(text_robot, image_path_robot)
        return (rating_self, rating_robot)
    else:
        return (rating_self, None)

line_args['participant'] = "test" #sys.argv[1]
line_args['country'] = "sk" # sys.argv[2]
condition = "no_repeat" # sys.argv[3]

setup_for_participant()
robot = load_robot()


if condition == 'repeat':
    draw_with_imitation()
else:
    draw_without_imitation()
# We're not putting this in an extra agent, as the robot should just wake up and look down
# once in the beginning
# Sleep 3 seconds til robot got woken up
#time.sleep(3)
#look_down(robot)
#user_draws()
#data = read_newest_results("tulip")
#data = read_newest_results("robot_results")
#flattened_data = flatten_data(data)
#create_canvas_with_data_from_strokes(data)
#create_canvas_with_flattened_data(flattened_data)
# Setting true for now, as we will use the learned model with Perceptrons
#mirrored_data = transform_coordinates(flattened_data, True)
#(rescaled_data, rescale_factor, shift_x, shift_y) = rescale_and_shift_image(mirrored_data)
#rescaled_data = list(rescaled_data)
#drawing_robot_thread = threading.Thread(target = robot_draws_strokes, args = (rescaled_data, ))
#drawing_robot_thread.start()
#open_canvas_for_robot(rescaled_data, "tulip")
#print("Calculating error now")
#error = calculate_error(rescaled_data, strokes)
#print(f"Error is: {error}")
sys.exit()