import matplotlib.pyplot as plt
import pydicom
import numpy as np
from os import listdir
from os.path import isfile, join
from skimage.measure import label   
import cv2 as cv
from scipy.signal import argrelextrema
from scipy import ndimage
import cv2
import matplotlib as mpl

path_data = 'C:/ultra/Codes/Codes/QA_analysis/testi1/IMG00000.dcm'
data = pydicom.dcmread(path_data)

id_value = data[0x00100020]
id_value.value = '123-US'
data[0x00100020]=id_value

print(id_value)

data.save_as('C:/ultra/Codes/Codes/QA_analysis/testi1/out.dcm')

path_data = 'C:/ultra/Codes/Codes/QA_analysis/testi1/out.dcm'

data = pydicom.dcmread(path_data)
id_value = data[0x00100020]
print(id_value)
