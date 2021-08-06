import numpy as np
import os
from os import listdir
from os.path import join
import pickle
import yaml

def read_log_file2(filename):
    """read log text file lines to list"""
    count = 0
    c = -1
    param_dct = {'param1':'', 'param2':'', 'param3':'','param4':'','param5':'','param6':'','param7':'','param8':'', 'param9':''}
    log_list_dct = { 'name':'', 'params':param_dct}
    
    log_list = []
    with open(filename) as fp:
        while True:
            count+=1
            c += 1
            line = fp.readline()
            if not line:
                break

            if c==0:
                log_list_dct['name'] = line
            else:
                keys =  list(param_dct.keys())
                param_dct[keys[c-1]] =  line
            if line == '\n':
                keys =  list(param_dct.keys())
                for k in keys:
                    txt = param_dct[k]
                    if txt=='':
                        del param_dct[k]
                log_list.append(log_list_dct)
                param_dct = {'param1':'', 'param2':'', 'param3':'','param4':'','param5':'','param6':'','param7':'','param8':'', 'param9':''}
                log_list_dct = { 'name':'', 'params':param_dct}
                c = -1

    return log_list

def read_log_file(filename):
    """read log text file lines to list"""
    count = 0
    c = 0
    log_list_names = []
    log_list_params = []
    txt = ''
    with open(filename) as fp:
        while True:
            count+=1
            c += 1
            line = fp.readline()
            if not line:
                break

            if c==1:
                log_list_names.append(line)
            else:
                txt = txt + line + ' \n'

            if line == '\n':
                log_list_params.append(txt)
                txt = ''
                c = 0

    return log_list_names, log_list_params

def get_settings_dct():
    ''' Get setting data as dictionary '''
    path = os.getcwd()
    name = 'Settings.yaml'
    path_name = os.path.join(path, name)
    a_yaml_file = open(path_name)
    dct = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    return dct

def get_filenames(path_data):
    ''' list filenames from path_data'''
    names =  [f for f in listdir(path_data)]
    return names

def Convert(lst):
    ''' convert list to dictionary'''
    res_dct_list = []
    id=0
    for file in lst:
        dct = {'id': id, 'name': file}
        res_dct_list.append(dct)
        id += 1
    return res_dct_list

def read_pickle(file):
    ''' Read pickle data'''
    objects = []
    with (open(file, "rb")) as openfile:
        while True:
            try:
                objects.append(pickle.load(openfile))
            except EOFError:
                break
    return objects

def get_trend_data(path_data, n_samples=4):
    ''' Gathers trend data from path_data to dct '''
    files =  listdir(path_data)
    # re-order:
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    
    #init lists:
    dates = []
    U_cov_list = []
    U_skew_list = []
    S_depth_list = []
    U_low_list = []
    name = []
        
    for file in files:
       objects = read_pickle(join(path_data, file))
       dct = objects[0]  
       
       # Assign data:
       dates.append(dct['date'])
       U_cov_list.append(dct['U_cov'])
       U_skew_list.append(dct['U_skew'])    
       S_depth_list.append(dct['S_depth'])     
       U_low_list.append(dct['U_low'])
    
    name = dct['name']
    
    #error limits:
    # statistical params:
    if len(U_cov_list) >= n_samples + 1: #check if there is enough previous data
        lb = len(U_cov_list)-n_samples-1
        ub = len(U_cov_list)-1
        
        U_cov_mean = np.mean(U_cov_list[lb:ub])
        U_skew_mean = np.mean(U_skew_list[lb:ub])
        S_depth_mean = np.mean(S_depth_list[lb:ub])
        U_low_mean = np.mean(U_low_list[lb:ub], 0)
        U_low_mean =U_low_mean.tolist()
      
        U_cov_sd = np.std(U_cov_list[lb:ub])
        U_skew_sd = np.std(U_skew_list[lb:ub])
        S_depth_sd = np.std(S_depth_list[lb:ub])
        U_low_sd = np.std(U_low_list[lb:ub], 0)
        U_low_sd = U_low_sd.tolist()
        
    else:   

        U_cov_mean =  np.mean(U_cov_list[0:len(U_cov_list)-1])
        U_skew_mean = np.mean(U_skew_list[0:len(U_cov_list)-1])
        S_depth_mean = np.mean(S_depth_list[0:len(U_cov_list)-1])
        U_low_mean =  np.mean(U_low_list[0:len(U_cov_list)-1], 0)
        U_low_mean = U_low_mean.tolist()
    
        U_cov_sd = np.std(U_cov_list[0:len(U_cov_list)-1])
        U_skew_sd = np.std(U_skew_list[0:len(U_cov_list)-1])
        S_depth_sd = np.std(S_depth_list[0:len(U_cov_list)-1])
        U_low_sd = np.std(U_low_list[0:len(U_cov_list)-1], 0)
        U_low_sd = U_low_sd.tolist()
  
    dct_res = {'name':name,'dates':dates,
               'U_cov_list':U_cov_list, 'U_skew_list':U_skew_list,
               'S_depth_list':S_depth_list,'U_low_list':U_low_list,
               'U_cov_mean':U_cov_mean, 'U_skew_mean':U_skew_mean, 
               'S_depth_mean':S_depth_mean, 'U_low_mean':U_low_mean,
               'U_cov_sd':U_cov_sd, 'U_skew_sd':U_skew_sd,
               'S_depth_sd':S_depth_sd, 'U_low_sd':U_low_sd}
    
    return dct_res