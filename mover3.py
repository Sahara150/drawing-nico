from nicomotion.Motion import Motion
import time
import numpy as np
from global_static_vars import default_speed

motorConfig = './nico_humanoid_upper_rh7d_ukba.json'
robot = Motion(motorConfig=motorConfig)

def close():
    global robot #?
    rightArmDofs = ['r_shoulder_z','r_shoulder_y','r_arm_x','r_elbow_y','r_wrist_z','r_wrist_x','r_thumb_z','r_thumb_x','r_indexfinger_x','r_middlefingers_x']
    parking_position = [-8.0, -15.0, 16.0, 74.0, -24.0, 35.0, -71.0, -104.0, -180.0, -180.0, 3.0, 13.0]
    for dof, position in zip(rightArmDofs,parking_position):
        robot.setAngle(dof,position,0.04)
    time.sleep(1.5)
    try:
        print('closing line')
        del robot
        print('line closed')
    except:
        pass

def enableTorque(dofs):
    for dof in dofs:
        robot.enableTorque(dof)

def disableTorque(dofs):
    for dof in dofs:
        robot.disableTorque(dof)

def stopAllMotors(dofs):
    for motor in robot._robot.motors:
        motor.goal_position = motor.present_position

def loadAnimation(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        concerned_dofs = eval(lines[0])
        recorded_poses = []
        for line in lines[1:]:
            recorded_pose = eval(line[:-1])
            recorded_poses.append(recorded_pose)
        return (concerned_dofs,recorded_poses)
    raise(BaseException(filename+" does not exist"))

def move_to_position_through_time(target_positions, duration):
    global robot
    # calculate current angular speed
    import copy
    # get the current positions of all joints to move
    current_positions = copy.deepcopy(target_positions)
    for joint in current_positions:
        current_positions[joint] = robot.getAngle(joint)
    speed_to_reach = {
        k: abs(
            (float(current_positions[k]) - float(target_positions[k])) / float(1260*duration)
        ) if duration != 0 else default_speed
        for k in current_positions
    }
    for joi in target_positions:
        robot.setAngle(
            joi,
            float(target_positions[joi]),
            speed_to_reach[joi],
        )
    print(f"Load Shoulder: {robot._robot.r_shoulder_y.present_load}")
    print(f"Load elbow: {robot._robot.r_elbow_y.present_load}" )

# Instead of a dictionary, this function requires only a list of positions and the corresponding 
# dofs
def move_to_position_through_time_ext(dofs, target_positions : list[float], duration):
    if duration == 0:
        return
    global robot
    # calculate current angular speed
    import copy
    # get the current positions of all joints to move
    current_positions = copy.deepcopy(target_positions)
    for index in range(len(current_positions)):
        current_positions[index] = robot.getAngle(dofs[index])
    speed_to_reach = [
        abs(
            (float(current_positions[k]) - float(target_positions[k])) / float(1260*duration)
        )
        for k in range(len(current_positions))
    ]
    for ind in range(len(target_positions)):
        robot.setAngle(
            dofs[ind],
            target_positions[ind],
            speed_to_reach[ind],
        )

def play_movement(dofs,poses,durations):
    for pose,duration in zip(poses,durations):
        # Move all joints in the subset to the postion
        command = {dof : angle for dof, angle in zip(dofs, pose) if dof != 'timestamp' }
        move_to_position_through_time(command, duration)
        time.sleep(duration)

if __name__ == "__main__":
 
    dofs, poses = loadAnimation('movement.txt')
        
    # enable torque
    for dof in dofs:
        if dof != 'timestamp':
            robot.enableTorque(dof)

    timeindex = np.where(np.array(dofs) == 'timestamp')[0][0]
    timestamps = []
    for pose in poses:
        timestamps.append(pose[timeindex])

    timestamps = np.array(timestamps,np.float64)/1000.0 #[s]
    durations = [timestamps[0]] + list(timestamps[1:]-timestamps[:-1])

    command0 = {dof : angle for dof, angle in zip(dofs, poses[0]) if dof != 'timestamp' }
    move_to_position_through_time(command0,2)

    for _ in range(4):
        play_movement(dofs,poses,durations)
        durations = [ duration * 2 for duration in durations ]
        time.sleep(1)

