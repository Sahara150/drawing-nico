from nicomotion.Motion import Motion

motorConfig = './nico_humanoid_upper_rh7d_ukba.json'
robot = Motion(motorConfig=motorConfig)

safe = { # position that should be achieved
                'r_shoulder_z':-2.1,
                'r_shoulder_y':-10.3,
                'r_arm_x':2.1,
                'r_elbow_y':86.9,
                'r_wrist_z':-8.7,
                'r_wrist_x':19.2,
                'r_thumb_z':-57.0,
                'r_indexfinger_x':-180.0,
                'r_middlefingers_x':180.0,
                'head_z':0.0,
                'head_y':0.0
            }

for dof in safe:
    robot.enableTorque(dof)
    robot.setAngle(dof, safe[dof], 0.08)
    print(f"Setting ${dof}")
