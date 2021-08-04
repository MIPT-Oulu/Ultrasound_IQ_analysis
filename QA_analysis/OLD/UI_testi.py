# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 13:28:43 2020

@author: sinkinen
"""

import os
import pickle
import numpy as np
import UA_QA_analysis as QA

import matplotlib.pyplot as plt


import matplotlib as mpl
mpl.rcParams['figure.dpi']= 150

#%% Read in data:
path_data = 'C:/Users/sinkinen/US_analysis/results/'

#%%

os.chdir(path_data)
all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]


for dirs in all_subdirs:
     dir = os.path.join(path_data, dirs)
     print(dir)



#%%
for file in os.listdir(dir):
    print(file)
    

#%%
infile = open(os.path.join(dir, file),'rb')
data = pickle.load(infile)
infile.close()

#%% extract:

im = data.get_im()
horiz_profile = data.get_horiz_profiles()
vert_profile = data.get_vert_profiles()
S_depth = data.get_S_depth()
U_cov = data.get_U_cov()
U_low = data.get_U_low()
U_skew = data.get_U_skew()


plt.imshow(im)






