from drawing import open_canvas
import os
from datetime import datetime
import time
import threading
from global_static_vars import images_dir, experiment_dir, line_args
from helper_functions import read_newest_results, flatten_data, transform_coordinates, rescale_and_shift_image, calculate_error
from canvas_functions import create_canvas_with_data_from_strokes, create_canvas_with_flattened_data, open_canvas_for_robot, strokes
from robot_setup import load_robot, look_down, robot_draws_strokes
#from nntest import compare_old_to_new

def user_draws():

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
    
    for i in range(0,1):
        open_canvas(f"robot_repeats_{i}", path_folder_participant, "robot")


line_args['country'] = "sk"
# We're not putting this in an extra agent, as the robot should just wake up and look down
# once in the beginning
robot = load_robot()
# Sleep 3 seconds til robot got woken up
time.sleep(3)
look_down(robot)
user_draws()
data = read_newest_results("robot_repeats_0")
flattened_data = flatten_data(data)
#create_canvas_with_data_from_strokes(data)
#create_canvas_with_flattened_data(flattened_data)
# Setting true for now, as we will use the learned model with Perceptrons
mirrored_data = transform_coordinates(flattened_data, True)
(rescaled_data, rescale_factor) = rescale_and_shift_image(mirrored_data)
rescaled_data = list(rescaled_data)
drawing_robot_thread = threading.Thread(target = robot_draws_strokes, args = (rescaled_data,))
drawing_robot_thread.start()
open_canvas_for_robot(rescaled_data)
print("Calculating error now")
error = calculate_error(rescaled_data, strokes)