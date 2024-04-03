import sys

code_path = "C:/Users/haras/Uni_SourceCodes/NICO/drawing-nico/"   #for Bratislava

images_dir = code_path +"Images/"
experiment_dir = images_dir + "Experiments_raw/"

# Set the color and size for drawing
draw_color = 'black'
draw_size = 4

# specify resolutions of both screens
width_main, height_main = 1366, 768
width_side, height_side = 1920, 1080

### These variables are set as arguments when executing, so they may differ from initial config
line_args = {
    'country': "en"
}