import pygame
import numpy as np
import ctypes
import cv2
import time
from mover3 import robot, move_to_position_through_time_ext, play_movement
import threading
from data_grid import get_moves_for_data_grid, create_data_grid

rightArmDofs = ['r_shoulder_z','r_shoulder_y','r_arm_x','r_elbow_y','r_wrist_z','r_wrist_x','r_thumb_z','r_thumb_x','r_indexfinger_x','r_middlefingers_x']
parking_position = [-8.0, -15.0, 16.0, 74.0, -24.0, 35.0, -71.0, -104.0, -180.0, -180.0, 0]
ready_position = [-8.0, 46.0, 13.0, 99.0, 44.0, 99.0, -70.0, 32.0, -180.0, 180.0, 1200]
steady_position = [13.0, 36.0, 25.0, 106.0, 66.0, -180.0, -70.0, 26.0, -180.0, 172.0, 1800]

#initial_data = np.loadtxt('dataset.npy')[:, :-2]
initial_data = get_moves_for_data_grid(create_data_grid())
last_one = None
correct_data = []
position = 0
quit = False
    

def cv_cross(img,point,radius,color,thickness=1):
    x, y = point
    cv2.line(img,(int(x-radius),int(y)),(int(x+radius),int(y)),color,thickness)
    cv2.line(img,(int(x),int(y-radius)),(int(x),int(y+radius)),color,thickness)

def cross(scr,line_color,point,radius,thickness=1):
    x, y = point
    pygame.draw.line(scr,line_color, (x-radius, y), (x+radius, y), width=thickness)
    pygame.draw.line(scr,line_color, (x, y-radius), (x, y+radius), width=thickness)


def store_touch(point : tuple[int, int]):
    global quit, position, last_one
    time.sleep(0.5)
    angles = []
    for dof in rightArmDofs:
        angles.append(robot.getAngle(dof))
    correct_data.append(np.concatenate((np.around(angles, decimals=2), np.array([point[0], point[1]]))))
    print(f"Old data: {last_one}, Correct data: {correct_data[-1]}")
    #position += 1
    #if position < len(initial_data):
    next_one = next(initial_data, None)
    if next_one is not None:
        move = threading.Thread(target=execute_movement, args=(last_one, next_one))
        last_one = next_one
        move.start()
    else:
        #np.savetxt('corrected_dataset.npy', correct_data, fmt='%.2f')
        np.savetxt('datagrid.npy', correct_data, fmt='%.2f')
        quit = True
        touch_timestamp = 1250 + initial_data[-1][0]*250  
        poses = [
            ready_position[:-1],
            steady_position[:-1],
            parking_position[:-1]
        ]
        durations = [
            round(touch_timestamp-steady_position[-1])/1000.0,
            (steady_position[-1]-ready_position[-1])/1000.0,
            (ready_position[-1]-parking_position[-1])/1000.0
        ]
        play_movement(rightArmDofs, poses, durations)


def execute_movement(old_movement : list[float], next_movement : list[float]):
    move_up = [ (angle if index != 5 else -180.0) for index, angle in enumerate(old_movement) ]
    move_over = [ (angle if index != 5 else -180.0) for index, angle in enumerate(next_movement) ]
    while not robot.getAngle('r_wrist_x') <= -177.0:
        # Perform this until robot obeys
        move_to_position_through_time_ext(rightArmDofs, move_up, 0.25)
        print("Move up")
        time.sleep(2)
    move_to_position_through_time_ext(rightArmDofs, move_over, 1)
    print("Move over")
    time.sleep(3)
    print("Move down")
    move_to_position_through_time_ext(rightArmDofs, next_movement, 0.25)

def create_pygame_window():
    global quit
    # create a Pygame window
    pygame.font.init()
    global myfont
    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    global screen
    screen = pygame.display.set_mode((1920, 1080), flags=pygame.NOFRAME, depth=0, display=1)
    global image
    image = np.zeros((1080,1920,3),np.uint8)
    image[:,:] = (80,80,80)
    pygame.display.set_caption('NICOs touchscreen')
    HWND = pygame.display.get_wm_info()['window']
    GWL_EXSTYLE = -20
    styles = ctypes.windll.user32.GetWindowLongA(HWND,GWL_EXSTYLE)
    WS_EX_NOACTIVATE = 0x08000000
    styles |= WS_EX_NOACTIVATE
    ctypes.windll.user32.SetWindowLongA(HWND,GWL_EXSTYLE,styles)
    screen_info = pygame.display.Info()
    width, height = screen_info.current_w, screen_info.current_h # 
    color_index = 0
    colors = [ (255,0,0), (0,255,0), (0,255,255), (80,80,255) ] # Red, Green, Cyan, Light Blue
    print('initialized')
        
    # Run the event loop
    pygame.time.set_timer(pygame.USEREVENT + 1, 500)
    while not quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('quit event')
                quit = True
            elif event.type == pygame.FINGERDOWN:
                # Process the first moment of touch
                circle_color = colors[color_index]
                color_index += 1
                if color_index == len(colors):
                    color_index = 0
                circle_radius = 30
                circle_position = (int(width*event.x), int(height*event.y))
                print("touch detected at",circle_position)
                cross(screen, circle_color, circle_position, circle_radius, 3)
                cv_cross(image,circle_position,circle_radius,(circle_color[2],circle_color[1],circle_color[0]),7)
                store_touch(circle_position)
        pygame.display.flip()
        time.sleep(0.025)
        
    # quit Pygame
    print('quiting pygame')
    pygame.quit()
    
print("Opening screen now.")
pygameW = threading.Thread(target=create_pygame_window)
pygameW.start()

last_one = next(initial_data)
touch_timestamp = 1250 + last_one[0]*250
        
poses = [
    parking_position[:-1],
    ready_position[:-1],
    steady_position[:-1],
    last_one
]    
durations = [
    1.500,
    (ready_position[-1]-parking_position[-1])/1000.0,
    (steady_position[-1]-ready_position[-1])/1000.0,
    touch_timestamp/1000.0
]

play_movement(rightArmDofs, poses, durations)
