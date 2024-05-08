# How to use this project:

Clone the project with the following command:

`git clone https://github.com/Sahara150/drawing-nico.git`

Use pip install to install all requirements from requirements.txt
For the nico requirement, see https://github.com/incognite-lab/myGym/tree/nico-sim2real?tab=readme-ov-file#real-nico-robot-software to see how to install it.

# Different parts of the program

The folder NNTraining contains code that got used to produce training data for the neural network by pointing to points in a 32x32px grid. This code is probably not relevant for most and is currently set-up onto the left arm.

## Canvas_functions.py
canvas_functions.py contains a number of functions related to the tablets UI. 
The most relevant ones are 
- open_canvas_for_robot: This method will open the canvas on which the robot can draw and register all the touch events. You need to pass a category which will be relevant later for the naming of the file when it stores the image.
- close_canvas: automatically called when robot finished drawing
- create_canvas_with ...: these functions create a canvas and draw the strokes on it that were submitted to the function. There is one function for the original strokes returned from the canvas and one for flattened data. This is all data after the flatten_data function got called that reduces complexity. These are useful helper-functions when one wants to visualize what got saved or how different transformations affect the image.

Experiments:
- configure_and_show: This displays a psychopy window. Should only be called if none is currently open or there will be multiple windows overlaying each other and there may be problems with UI not reacting to interaction.
- show_category_prompt: First asks user if he is ready to draw, then shows category that got specified as function parameter. Additional bool can specify, if this is a repetition of a previous category.
- show_prompt: displays whatever text got specified in method call with a "click to continue" button.

## Drawing.py
This script only has one relevant function:
open_canvas: it opens the canvas for the user with a button at the bottom to finish the drawing. If the user takes too long there will be a bluescreen in between telling them to finish soon. It automatically stores all the data in a file, including the exact strokes.

## File_helper.py
This contains helpers relevant for interaction with files.
There are two functions to read strokes from a file (either at a specific index or the last one) and one to append data to any file specified.

## Global_static_vars.py
This is a collection of all variables that are needed from a variety of files and stay the same throughout the whole execution of the program.

## Helper_functions.py
This file contains a variety of functions to transform strokes and maths.
- flatten_data : Reduces data complexity based on Ramer-Douglas-Peucker algorithm.
- transform_coordinates: Mirrors the image (optional also on x-axis)
- rescale_and_shift_image: Rescales and shifts image within limits defined by in global_static_vars. Also returns rescale_factor and shifts so they can be stored if needed.
- calculate_error: Takes as input the strokes passed to the robot for drawing (flattened) and the strokes resulting from the robots drawing. It is important to not use the regular canvas for the robot but only the open_canvas_for_robot, because this contains additional information on which stroke a coordinate list should belong to (take for example, that the robot messes up and one stroke gets interrupted resulting in two strokes for one). 
- display_camera_image and close_cameras: This opens a screen showing the imagery of Nicos eyes and closes them respectively. display_camera_image should be executed in thread as it runs endlessly until close_cameras.

## Robot_setup.py
This contains all the functions that control the robot.
- load_robot: returns robot.
- to_default_position, look_down, look_to_side: calls to control respective parts of robot.
- robot_draws_strokes: the truly important function. After transforming the strokes and getting them ready this is the function called to make the robot actually perform the drawing movement. This function sleeps for 1s giving the code enough time to first start this thread and then open the canvas (since the canvas needs to run in the main-thread and nothing can be performed until it is closed again).

## texts.py
This file contains the translate function which can be used to localize texts between english and Slovak as well as two much used strings.

## Start_program.py
This file runs the experiment. 
It can be executed by the following line of code:
```python start_program.py <participant> <country> <condition>```
The conditions are either no_repeat or repeat.

## Just draw one image for the robot and let him repeat
If you just want to draw one image for the robot and let him repeat, there's the "user_draws" function that may be very useful for it. The category entered as parameter does not get displayed, but it is used for saving the data in a file. An example code to do the whole process can be found below:

```
setup_for_participant()
robot = load_robot()

time.sleep(3)

to_default_position(robot)
look_down(robot)
user_draws("tulip")
data = read_newest_results("tulip")
flattened_data = flatten_data(data)
# Setting true for now, as we will use the learned model with Perceptrons
mirrored_data = transform_coordinates(flattened_data, True)
(rescaled_data, rescale_factor, shift_x, shift_y) = rescale_and_shift_image(mirrored_data)
# Important because it is a map, so we can use it multiple times
rescaled_data = list(rescaled_data)
drawing_robot_thread = threading.Thread(target = robot_draws_strokes, args = (rescaled_data, ))
drawing_robot_thread.start()
open_canvas_for_robot(rescaled_data, "tulip")
error = calculate_error(rescaled_data, strokes)
print(f"Error is: {error}")
time.sleep(1)
sys.exit()
```