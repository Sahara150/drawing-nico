from drawing import open_canvas
import os
from datetime import datetime
from global_static_vars import images_dir, experiment_dir, line_args
from helper_functions import read_results, create_canvas_with_data_from_strokes


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
        open_canvas(f"test {i}", path_folder_participant, "robot")

#draw_ten_times()
data = read_results("robot", 2)
create_canvas_with_data_from_strokes(data)