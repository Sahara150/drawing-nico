import numpy as np
from robot_setup import get_output_for_point

corrected_data = np.loadtxt("corrected_dataset.npy")

def create_data_grid():
    data_grid = []
    for x in range(164, 1800, 32):
        for y in range(0, 860, 32):
            data_grid.append([x, y])
    return data_grid        

def get_moves_for_data_grid(grid : list[list[int]]):
    grid_angles = []
    for point in grid:
        outs = get_output_for_point(point)
        
        if outs[5] > 1.0: # wrist-x
            outs[5] = 1.0

        if outs[3] <= 1.0: # elbow
            yield list(np.round(outs*180))

rounded_data = np.round(corrected_data, decimals=2)
np.savetxt('corrected_dataset_round', corrected_data, fmt='%.2f')