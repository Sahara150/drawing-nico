from nicomotion.Motion import Motion
from global_static_vars import default_speed

def setup_robot() -> Motion :
    motorConfig = "./nico_humanoid_upper_rh7d_ukba.json"
    return Motion(motorConfig=motorConfig)

def look_down(robot : Motion):
    print("Setting head now")
    robot.setAngle("head_y", -40.0, default_speed)