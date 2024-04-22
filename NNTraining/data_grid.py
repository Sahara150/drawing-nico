import numpy as np
from robot_setup import get_output_for_point

def create_data_grid():
    data_grid = []
    for x in range(164, 1756, 4):
        for y in range(0, 860):
            data_grid.append([x, y])
    return data_grid        

def get_moves_for_data_grid(grid : list[list[int]]):
    grid_angles = []
    for point in grid:
        outs = get_output_for_point(point)
        
        if outs[5] > 1.0: # wrist-x
            outs[5] = 1.0

        if outs[3] <= 1.0: # elbow
            grid_angles.append(list(np.round(outs*180)))
    return grid_angles