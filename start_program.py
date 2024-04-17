from drawing import open_canvas
import os
from datetime import datetime
import time
import threading
from global_static_vars import images_dir, experiment_dir, line_args
from helper_functions import read_newest_results, flatten_data, transform_coordinates, rescale_and_shift_image
from canvas_functions import create_canvas_with_data_from_strokes, open_canvas_for_robot, close_canvas
from robot_setup import load_robot, look_down, robot_draws_strokes

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
    participant_dir = "nicodraws" + str(date_hour)
    path_folder_participant = images_dir + participant_dir
    os.mkdir(path_folder_participant)

    line_args['country'] = "sk"
    for i in range(0,1):
        open_canvas(f"robot_repeats_{i}", path_folder_participant, "robot")

# We're not putting this in an extra agent, as the robot should just wake up and look down
# once in the beginning
robot = load_robot()
# Sleep 3 seconds til robot got woken up
time.sleep(3)
look_down(robot)
user_draws()
data = read_newest_results("robot_repeats_0")
flattened_data = flatten_data(data)
create_canvas_with_data_from_strokes(data)
#create_canvas_with_flattened_data(flattened_data)
# Setting true for now, as we will use the learned model with Perceptrons
mirrored_data = transform_coordinates(flattened_data, True)
mirrored_data_left = transform_coordinates(flatten_data, False)
rescaled_data = rescale_and_shift_image(mirrored_data)
rescaled_data_left = rescale_and_shift_image(mirrored_data_left)
drawing_robot_thread = threading.Thread(robot_draws_strokes, rescaled_data, rescaled_data_left)
canvas_thread = threading.Thread(open_canvas_for_robot)
canvas_thread.start()
drawing_robot_thread.start()
drawing_robot_thread.join()
# When drawing robot thread is finished, we can close canvas
close_canvas()