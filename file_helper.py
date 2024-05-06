import os
import ndjson
import pandas as pd
from global_static_vars import experiment_dir



### File helpers ###
def read_newest_results(category : set):
    path_results = experiment_dir + f"raw_{category}.ndjson"
    file = pd.read_json(path_results, lines=True)
    # This gets the detailed strokes for each iteration of category
    strokes = file["strokes"]
    data = strokes[len(strokes)-1]
    return data

def read_results(category : str, iteration : int):
    path_results = experiment_dir + f"raw_{category}.ndjson"
    file = pd.read_json(path_results, lines=True)
    # This gets the detailed strokes for each iteration of category
    strokes = file["strokes"]
    data = strokes[iteration]
    return data

def append_to_ndjson(file_path, new_data):
    # Read existing data if file exists, otherwise start with an empty list
    data = []
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            data = ndjson.load(file)

    # Append the new data
    data.append(new_data)

    # Write all data back to the file
    with open(file_path, 'w') as file:
        ndjson.dump(data, file)

### End of file helpers ###
