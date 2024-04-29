import sys

code_path = "C:/Users/haras/Uni_SourceCodes/NICO/drawing-nico/"   #for Bratislava

images_dir = code_path +"Images/"
experiment_dir = images_dir + "Experiments_raw/"

# Set the color and size for drawing
draw_color = 'black'
draw_size = 4
lower_edge_canvas = 1009

# specify resolutions of both screens
width_main, height_main = 1366, 768
width_side, height_side = 1920, 1080

#Speed of robot movements
default_speed = 0.08

#The maximum rescale applied, so that the robot doesn't overdo the increase in size
max_rescale = 1.5
#The size of the drawing field the robot can use
drawing_area_x = 1592
drawing_area_y = 840
left_limit_x = 164
center_y = drawing_area_y/2 + 10
center_x = width_side/2

# Static vars of robot
rightArmDofs = ['r_shoulder_z','r_shoulder_y','r_arm_x','r_elbow_y','r_wrist_z','r_wrist_x','r_thumb_z','r_thumb_x','r_indexfinger_x','r_middlefingers_x']
leftArmDofs = ['l_shoulder_z','l_shoulder_y','l_arm_x','l_elbow_y','l_wrist_z','l_wrist_x','l_thumb_z','l_thumb_x','l_indexfinger_x','l_middlefingers_x']

# Last column is time stamp
parking_position = [-8.0, -15.0, 16.0, 74.0, -24.0, 35.0, -71.0, -104.0, -180.0, -180.0, 0]
ready_position = [-8.0, 46.0, 13.0, 99.0, 44.0, 99.0, -70.0, 32.0, -180.0, 180.0, 510]
steady_position = [13.0, 36.0, 25.0, 106.0, 66.0, -180.0, -70.0, 26.0, -180.0, 172.0, 800]

parking_time = 1.500
### These variables are set as arguments when executing in command line, 
### so they may differ from initial config
line_args = {
    'country': "en",
    'participant': "nicodraws",
    'path_folder_participant': "empty"
}