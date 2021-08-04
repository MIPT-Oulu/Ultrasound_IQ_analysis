import matplotlib.pyplot as plt
import pydicom
import numpy as np

path_d = 'C:/KPacs/Imagebox/1.2.840.113619.2.323.550149246864.1622638488.2.dcm'


asd = pydicom.dcmread(path_d)

import pdb; pdb.set_trace()