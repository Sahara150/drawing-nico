from nicomotion.Motion import Motion
from global_static_vars import default_speed, width_side, height_side
from global_static_vars import  ready_position, steady_position, parking_position, leftArmDofs, rightArmDofs, parking_time
from keras.models import load_model
import keras
import numpy as np
from mover3 import move_to_position_through_time_ext, play_movement, robot
from canvas_functions import close_canvas, increase_stroke_count
import time

model = load_model("perceptron_high_data.h5", safe_mode=True, custom_objects={
    'mse'.encode('cp1252'): keras.losses.mean_squared_error
})
model_left = load_model("perceptron_left.h5")
print(model.summary())

#TODO: If not too much work, replace that with mover3
def load_robot() -> Motion :
    return robot

def look_down(robot : Motion):
    robot.setAngle("head_y", -40.0, default_speed)
    robot.setAngle("head_z", 0.0, default_speed)

def setup_robot(robot : Motion):
    robot.enableTorqueAll()

def robot_draws_strokes(strokes: list[list[list[int]]]):
    #Wait a second so the robot won't start drawing, before canvas is opened on main thread
    time.sleep(1)
    strokes = list(strokes)
    # At start of drawing, move both arms to parking position, then go through ready and steady  
    # with right arm
    move_to_position_through_time_ext(leftArmDofs, parking_position[:-1], parking_time)  
    poses_right_arm = [
        parking_position[:-1],
        ready_position[:-1],
        steady_position[:-1]
    ]
    durations_right_arm = [
        parking_time,
        (ready_position[-1]-parking_position[-1])/1000.0,
        (steady_position[-1]-ready_position[-1])/1000.0
    ]   

    play_movement(rightArmDofs, poses_right_arm, durations_right_arm)       
    
    # We get each point, get the angles for it and then implement the 
    # continuous movement
    for index, stroke in enumerate(strokes):
        (angles_right, angles_left) = get_angles_for_stroke(stroke)
        angles_right = [limit_index_finger(output) for output in angles_right]
        angles_left = [limit_index_finger(output) for output in angles_left]
        rescaled_angles_right = list(np.round(np.array(angles_right)*180.0))
        rescaled_angles_left = list(np.round(np.array(angles_left)*180.0))

        (poses_right, durations_right) = get_poses_and_durations_right(rescaled_angles_right)
        # This will have side effects on poses_right & durations_right. We still made it a function to 
        # improve readability in the main code
        (poses_left, durations_left) = get_poses_and_durations_left(rescaled_angles_left, poses_right, durations_right)
        
        if len(rescaled_angles_right)!=0:
            touch_timestamp = 450 + rescaled_angles_right[0][0]*250
            move_to_position_through_time_ext(rightArmDofs, [(angle if index != 5 else -180.0) for index, angle in enumerate(rescaled_angles_right[0])], round(touch_timestamp)/1000.0)  
            time.sleep(touch_timestamp/1000.0)
            time.sleep(1)
        
        play_movement(rightArmDofs, poses_right, durations_right)
        play_movement(leftArmDofs, poses_left, durations_left)    
        increase_stroke_count()
    # At end of drawing, move left arm back to parking and right arm through steady & ready
    # back to parking

    move_to_position_through_time_ext(leftArmDofs, parking_position[:-1], parking_time)  
    poses_right_arm = [
        steady_position[:-1],
        ready_position[:-1],
        parking_position[:-1]
    ]
    durations_right_arm = [
        (steady_position[-1]-ready_position[-1])/1000.0,
        (ready_position[-1]-parking_position[-1])/1000.0,
        parking_time
    ]   

    play_movement(rightArmDofs, poses_right_arm, durations_right_arm)   

    time.sleep(5)
    # When drawing robot thread is finished, we can close canvas
    close_canvas()    
    
#This returns the poses & durations for the right arm.
#If the right arm has any angles, it also moves left arm back to parking position.
def get_poses_and_durations_right(rescaled_angles_right : list[list[float]]):
    poses_right = []
    durations_right = []
    if len(rescaled_angles_right) != 0:
        #If right arm will draw, put left arm away
        # TODO: Check, if left arm is already in parking position, to save time if it is
        move_to_position_through_time_ext(leftArmDofs, parking_position[:-1], parking_time)            
        rescaled_angles_right = np.array(rescaled_angles_right)
        rescaled_angles_right[:, 1] -= 0.7
        #poses_right.append([(angle if index != 5 else -180.0) for index, angle in enumerate(rescaled_angles_right[0])])
        poses_right += list(rescaled_angles_right)
        poses_right.append(rescaled_angles_right[-1])
        poses_right.append([(angle if index != 5 else -180.0) for index, angle in enumerate(rescaled_angles_right[-1])])
        durations_right += [
            0.25
        ]
        
        # TODO: Test if shoulder joint is most sensible predictor of needed time or 
        # what would be better time calculation
        durations_right += [ duration_movement(angles, rescaled_angles_right[index-1]) for index, angles in enumerate(rescaled_angles_right[1:])]
        durations_right += [
            0.75,
            0.25
        ]

    return (poses_right, durations_right)

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
        poses_left.append([(angle if index != 5 else -180.0) for index, angle in enumerate(rescaled_angles_left[0])])
        poses_left += rescaled_angles_left
        # We rather do it right here, assuming that left arm will rarely be used, to avoid waiting 
        # for arms to move back, when they are already parking all the time when we use the right arm
        poses_left.append(steady_position[:-1])
        poses_left.append(ready_position[:-1])

        touch_timestamp = 450 + rescaled_angles_left[0][0]*250
            
        durations_left += [
            (ready_position[-1]-parking_position[-1])/1000.0,
            (steady_position[-1]-ready_position[-1])/1000.0,
            touch_timestamp/1000.0,
            0.25
        ]

        durations_left += [ duration_movement(angles, rescaled_angles_left[index-1]) for index, angles in enumerate(rescaled_angles_left[1:])]

        durations_left += [
            (steady_position[-1]-ready_position[-1])/1000.0,
            (ready_position[-1]-parking_position[-1])/1000.0
        ]

    return (poses_left, durations_left)    

def get_angles_for_stroke(stroke : list[list[int]]):
    angles_for_points = list(map(get_output_for_point, stroke))
    # Checks, if elbow is over possible value, therefore point out of reach,
    # fall back to left arm
    if any(output[3] > 1.0 for output in angles_for_points):
        angles_for_points_left = list(map(lambda point: get_output_for_point(point, True), stroke))
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
            
def get_output_for_point(point : list[int], left : bool = False):
    inps = np.array([point],np.float32) / np.array([width_side, height_side],np.float32)
    return model(inps).numpy()[0] if not left else model_left(inps).numpy()[0]

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
