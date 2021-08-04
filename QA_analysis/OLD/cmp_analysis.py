# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 11:44:30 2020

@author: sinkinen
"""

import numpy as np


threshold = 10

list_keys_to_cmp = []
list_keys_to_cmp.append('S_depth')
list_keys_to_cmp.append('U_cov')
list_keys_to_cmp.append('U_low')
list_keys_to_cmp.append('U_skew')


res  = {}
alert_flag = {}
for k in list_keys_to_cmp:
    print(k)
    print (res_dct[k])
    print(res_vo_dct[k])
    
    if k=='U_low':
        list1 = res_dct[k]
        list2 = res_vo_dct[k]
        err_list = []
        alert_list = []
        for i in range(len(list1)):
            print(i)
            rel_err = np.abs(list2[i]-list1[i])/list2[i]*100
            alr_val = np.abs(rel_err) > threshold
            err_list.append(rel_err)
            alert_list.append(alr_val)
            
      
        res[k] = err_list
        alert_flag[k] = alert_list 

        
    else:
        #compare:
        rel_err = np.abs(res_vo_dct[k]-res_dct[k])/res_vo_dct[k]*100
        alr_val = np.abs(rel_err) > threshold
        res[k] = rel_err
        alert_flag[k] = alr_val
    
            
    
print(res)
print(alert_flag)      
    

#%%
    
    
res_dct['S_depth']

# res_vo_dct

    dct = {'S_depth': data.S_depth,
 = {'S_depth': data.S_depth,
           'U_cov': data.U_cov,
           'U_low': data.U_low,
           'U_skew': data.U_skew,
           'horiz_profile': data.horiz_profile.tolist(),
           'vert_profiles': data.vert_profile.tolist(),
           'im': data.im.tolist(),
           'name': data.name,
           'transducer_name': data.transducer_name,
           'reverb_lines': data.reverb_lines,
           'unit': data.unit
           