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
drawing_area_y = 850
left_limit_x = 164
center_y = drawing_area_y/2
center_x = width_side/2
### These variables are set as arguments when executing in command line, 
### so they may differ from initial config
line_args = {
    'country': "en"
}