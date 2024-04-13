from drawing import open_canvas
import os
from datetime import datetime
from global_static_vars import images_dir, experiment_dir, line_args
from helper_functions import read_results, flatten_data, transform_coordinates, rescale_and_shift_image
from helper_functions import create_canvas_with_data_from_strokes, create_canvas_with_flattened_data
from robot_setup import setup_robot, look_down

def draw_ten_times():

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
        open_canvas(f"display_{i}", path_folder_participant, "robot")

#draw_ten_times()
#robot = setup_robot()
#look_down(robot)
data = read_results("test_0", 1)
flattened_data = flatten_data(data)
create_canvas_with_data_from_strokes(data)
create_canvas_with_flattened_data(flattened_data)
# Setting true for now, as we will print it on canvas and not yet draw it
mirrored_data = transform_coordinates(flattened_data, True)
create_canvas_with_flattened_data(mirrored_data)
rescaled_data = rescale_and_shift_image(mirrored_data)
create_canvas_with_flattened_data(rescaled_data)