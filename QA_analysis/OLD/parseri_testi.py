# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 10:25:23 2020

@author: sinkinen
"""

import argparse
import os
import time

def dir_path(string):
     if os.path.isdir(string):
         return string
     else:
         raise NotADirectoryError(string)
        
    
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Process US air scan images automatically')
parser.add_argument('--data_path', type = dir_path, default = 'C:/Users/sinkinen/US_analysis/data',
                    help='directory location to monitor data') 

parser.add_argument('--save_path', type = dir_path, default = 'C:/Users/sinkinen/US_analysis/results',
                    help='directory location to store the results') 


args = parser.parse_args()

data_path = args.data_path
save_path = args.save_path



#%%
print(args)
time.sleep(1)
print("tulostuuko tämä")
#dir_path(args)
print(data_path)
print(save_path)

print("tulostuuko tämä2")



time.sleep(2)
       