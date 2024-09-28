from django.test import TestCase

# Create your tests here.
import os
import json
from tensorflow.keras.models import model_from_json, load_model
from tensorflow.keras.utils import get_file

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

loaded_model = load_model('C:/Users/huawei/Desktop/ปี  4  เทอม  1/Project/price_of_astrophytum_be/env/mysite/api/models/model4.h5')
loaded_model.summary()
