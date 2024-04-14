from nicomotion.Motion import Motion
from global_static_vars import default_speed, width_side, height_side
from global_static_vars import  ready_position, steady_position, parking_position, leftArmDofs, rightArmDofs
from keras.models import load_model
import numpy as np
from mover3 import move_to_position_through_time, play_movement, robot

model = load_model("perceptron.h5")

#TODO: If not too much work, replace that with mover3
def load_robot() -> Motion :
    return robot

def look_down(robot : Motion):
    robot.setAngle("head_y", -40.0, default_speed)

def setup_robot(robot : Motion):
    robot.enableTorqueAll()

def robot_draws_strokes(strokes: list[list[list[int]]], mirrored_strokes : list[list[list[int]]]):
    # We get each point, get the angles for it and then implement the 
    # continuous movement
    for index, stroke in strokes:
        (angles_right, angles_left) = get_angles_for_stroke(stroke, mirrored_strokes[index])
        angles_right = [limit_index_finger(output) for output in angles_right]
        angles_left = [limit_index_finger(output) for output in angles_left]
        rescaled_angles_right = list(np.round(angles_right*180))
        rescaled_angles_left = list(np.round(angles_left*180))
        poses_right = []
        poses_left = []
        if len(angles_right) != 0:
            #If right arm will draw, put left arm away
            move_to_position_through_time(leftArmDofs, parking_position, 1000)            
            poses_right += ready_position
            poses_right += rescaled_angles_right
            poses_right += ready_position
            poses_right += steady_position

        if len(angles_left) != 0:
            # We don't call it now, but add it to the buffer for right, so that it happens, once
            # right arm finished drawing
            poses_right += parking_position
            poses_left += ready_position
            poses_left += rescaled_angles_left
            poses_left += ready_position
            poses_left += steady_position

        #TODO: Setup durations and then start movement    

def get_angles_for_stroke(stroke : list[list[int]], mirrored_stroke : list[list[int]]):
    angles_for_points = list(map(get_output_for_point, stroke))
    # Checks, if elbow is over possible value, therefore point out of reach,
    # fall back to left arm
    if any(output[3] > 1.0 for output in angles_for_points):
        angles_for_points_left = list(map(get_output_for_point, mirrored_stroke))
        # If it is again out of reach, the stroke must be split between the two arms
        if any(output[3] > 1.0 for output in angles_for_points_left):
            # TODO: Of course, theoretically there could be an indefinite amount of switches 
            # required between the two arms: Return a 2D-array with Nones and outputs iterating 
            # between the arms in that case, to ensure the clean switch, if you have time
            # but this is a highly unlikely case
            first_index = get_index_for_first(angles_for_points)   
            return (angles_for_points[0:first_index], angles_for_points_left[first_index:len(angles_for_points_left)])  
        else:
            return ([], angles_for_points_left)
    else:
        return(angles_for_points, [])
            
def get_output_for_point(point : list[int]):
    inps = np.array([point],np.float32) / np.array([width_side, height_side],np.float32)
    return model(inps).numpy()[0]

def get_index_for_first(angles_for_points: list[list[int]]):
    for index, output in enumerate(angles_for_points):
        if output[3] > 1.0:
            yield index

def limit_index_finger(output: list[float]):
    if output[5] > 1.0:
        output[5] = 1.0
    return output