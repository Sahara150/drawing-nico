from drawing import open_canvas
import os
from datetime import datetime

code_path = "C:/Users/haras/Uni_SourceCodes/NICO/drawing-nico/"   #for Bratislava

images_dir = code_path+"Images/"
experiment_dir = images_dir + "Experiments_raw/"

## Create new folder for participant
now = datetime.now()
date_hour = now.strftime("_%d-%m-%Y_%H-%M-%S")
participant_dir = "nicodraws" + str(date_hour)
python_path = "C:/ProgramData/miniconda3/python"
path_folder_participant = images_dir + participant_dir
os.mkdir(path_folder_participant)


for i in range(0,1):
    open_canvas("test", path_folder_participant, "robot", "sk", experiment_dir)

