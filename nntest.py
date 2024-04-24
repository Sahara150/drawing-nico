import keras
from keras.models import load_model
import numpy as np
from global_static_vars import width_side, height_side

model_old = model = load_model("perceptron.h5", safe_mode=True, custom_objects={
    'mse'.encode('cp1252'): keras.losses.mean_squared_error
})
model_new = load_model("perceptron_clean.h5", safe_mode=True, custom_objects={
    'mse'.encode('cp1252'): keras.losses.mean_squared_error
})

def get_output_for_point(point : list[int], model):
    inps = np.array([point],np.float32) / np.array([width_side, height_side],np.float32)
    return model(inps).numpy()[0]

def compare_old_to_new(point : list[int]):
    old = get_output_for_point(point, model_old)
    new = get_output_for_point(point, model_new)
    print(f"Old: {np.array(old)*180.0}, new: {np.array(new)*180.0}")