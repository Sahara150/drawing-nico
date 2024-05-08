import numpy
from rdp import rdp
from global_static_vars import lower_edge_canvas, width_side
from global_static_vars import max_rescale, drawing_area_x, drawing_area_y, center_y, center_x
from shapely.geometry import LineString, Point
from nicocameras import NicoCameras
import cv2 as cv
import time

cameras_running = True

cameras = NicoCameras()
### Coordinate manipulations ###    
def flatten_data(data: list[list[list[int]]]):
    flattened_strokes = []
    for stroke in data:
        #This is a 3D-array of x, y and t arrays 
        #Skip all empty strokes
        if len(stroke[0])!=0:
            #We drop the time as it is irrelevant for flattening the data 
            shortened_stroke = [stroke[0], stroke[1]]      
            transformed_stroke = numpy.transpose(shortened_stroke)
            #It may be discussed, how much we wanna reduce the point-clouds, 
            #but that for sure is a start
            flattened = rdp(transformed_stroke, epsilon=3)
            flattened_strokes.append(flattened)
    return flattened_strokes

# This function takes the flattened data and mirrors the y values by calculating "lower edge of canvas"-y as new y
# x stays untouched if transform_x is false
def transform_coordinates(data: list[list[list[int]]], transform_x : bool = False):
    # Converting to list, so it can be used multiple times in rescale_and_shift function
    return list(map(lambda stroke: list(map(lambda coordinate: transform_coordinate(coordinate, transform_x), stroke)), data))

def transform_coordinate(coordinate: list[int], transform_x : bool):
    if transform_x:
        return [width_side-coordinate[0], lower_edge_canvas-coordinate[1]]
    else:
        return [coordinate[0], lower_edge_canvas-coordinate[1]]

# The data is a list of strokes, each stroke being represented by a list of their coordinates    
def rescale_and_shift_image(data: list[list[list[int]]]):
    maxX = max(get_max_for_stroke(item, False) for item in data)
    minX = min(get_min_for_stroke(item, False) for item in data)
    maxY = max(get_max_for_stroke(item, True) for item in data)
    minY = min(get_min_for_stroke(item, True) for item in data)
    
    #Determine how much it can be rescaled maximum on each axis
    rescale_x = drawing_area_x/(maxX-minX)
    rescale_y = drawing_area_y/(maxY-minY)
    
    #Get the "weakest" rescale factor: We only rescale so that x & y stay within bounds 
    #and the rescaling is not too exaggerated
    rescale_factor = min(rescale_x, rescale_y, max_rescale)
    rescaled_data = map(lambda stroke: rescale_coordinates(stroke, rescale_factor), data)

    # Get current center value for x and y
    curr_center_x = ((maxX + minX)/2)*rescale_factor
    curr_center_y = ((maxY + minY)/2)*rescale_factor

    #We're shifting the image to the center, because it's generally easier for the robot to 
    #draw there
    shift_y = center_y - curr_center_y
    shift_x = center_x - curr_center_x

    return (map(lambda stroke: shift_data(stroke, shift_x, shift_y), rescaled_data), rescale_factor, shift_x, shift_y)

#If getY is set to true, it returns y, otherwise x
def get_max_for_stroke(item: list[list[int]], getY : bool):
    return max(coordinate[1] if getY else coordinate[0] for coordinate in item)

def get_min_for_stroke(item: list[list[int]], getY: bool):
    return min(coordinate[1] if getY else coordinate[0] for coordinate in item)

def rescale_coordinates(item: list[list[int]], rescale_factor: float):
    return map(lambda coordinate: [coordinate[0]*rescale_factor, coordinate[1]*rescale_factor], item)

def shift_data(item: list[list[int]], shift_x: float, shift_y: float):
    return list(map(lambda coordinate: [coordinate[0] + shift_x, coordinate[1] + shift_y], item))
    
def calculate_error(strokes_should : list[list[list[int]]], strokes_act):
    distance_sums = numpy.zeros(len(strokes_should))
    amount_of_points = numpy.zeros(len(strokes_should))    
    for stroke in strokes_act:
        if len(stroke[0])!=0:
            # Stroke at index 2 contains stroke count
            stroke_should = strokes_should[stroke[2]]
            line = LineString(stroke_should)
            distance_sum = 0
            for index, x in enumerate(stroke[0]):
                p = Point(x, stroke[1][index])
                distance = p.distance(line)
                distance_sum += abs(distance)

            distance_sums[stroke[2]] += distance_sum
            amount_of_points[stroke[2]] += len(stroke[0])

    print(f"Distance sums: {distance_sums}, Amount of points: {amount_of_points}")
    distances = numpy.divide(distance_sums, amount_of_points, where=amount_of_points!=0)
    print(f"Distances: {distances}")
    return distances.sum()/len(distances)

# TODO: Test if it works
def display_camera_image():
    while cameras_running:
        left_frame, right_frame = cameras.read()
        cv.imshow(left_frame, right_frame)
        cv.waitKey(10)

def close_cameras():
    global cameras_running
    cameras_running = False
    time.sleep(1)
    cameras.close()