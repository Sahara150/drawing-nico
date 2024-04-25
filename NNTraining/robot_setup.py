from nicomotion.Motion import Motion
from global_static_vars import default_speed, width_side, height_side
from global_static_vars import  ready_position, steady_position, parking_position, leftArmDofs, rightArmDofs, parking_time
from keras.models import load_model
import keras
import numpy as np
from mover3 import move_to_position_through_time_ext, play_movement, robot
import time

model = load_model("../perceptron_high_data.h5", safe_mode=True, custom_objects={
    'mse'.encode('cp1252'): keras.losses.mean_squared_error
})
print(model.summary())

#TODO: If not too much work, replace that with mover3
def load_robot() -> Motion :
    return robot

def look_down(robot : Motion):
    robot.setAngle("head_y", -40.0, default_speed)
    robot.setAngle("head_z", 0.0, default_speed)

def setup_robot(robot : Motion):
    robot.enableTorqueAll()

# This returns the poses_left & durations_left
# It also adds elements to poses_right & durations_right
def get_poses_and_durations_left(rescaled_angles_left : list[list[float]], poses_right : list[list[float]], durations_right : list[list[float]]):
    poses_left = []
    durations_left = []
    if len(rescaled_angles_left) != 0:
        # We don't call it now, but add it to the buffer for right, so that it happens, once
        # right arm finished drawing
        poses_right.append(parking_position[:-1])
        durations_right.append(1.500)
        poses_left.append(ready_position[:-1])
        poses_left.append(steady_position[:-1])
        poses_left.append([angle if index != 5 else -180.0] for index, angle in enumerate(rescaled_angles_left[0]))
        poses_left += rescaled_angles_left
        # We rather do it right here, assuming that left arm will rarely be used, to avoid waiting 
        # for arms to move back, when they are already parking all the time when we use the right arm
        poses_left.append(steady_position[:-1])
        poses_left.append(ready_position[:-1])

        durations_left += [
            (ready_position[-1]-parking_position[-1])/1000.0,
            (steady_position[-1]-ready_position[-1])/1000.0,
            0.25
        ]

        durations_left += [ angles[0]*0.25 for angles in rescaled_angles_left]

        durations_left += [
            (steady_position[-1]-ready_position[-1])/1000.0,
            (ready_position[-1]-parking_position[-1])/1000.0
        ]

    return (poses_left, durations_left)    

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

def duration_movement(angles_curr : list[float], angles_old : list[float]):
    return abs(angles_curr[0] - angles_old[0])*0.2 + abs(angles_curr[1] - angles_old[1]) * 0.2
