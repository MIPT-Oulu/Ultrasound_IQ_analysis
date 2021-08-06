import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os
import pickle
import utils.UA_QA_analysis as QA
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import argparse
import numpy as np
import pydicom


def check_if_US_data(path_data, id2cmp):
    ''' This function checks is the data is ultrasound air scan image by comparing the patient id '''
    data = pydicom.dcmread(path_data) #load data
    id_value = data[0x00100020].value #patient id
    bool_val = id_value == id2cmp

    return bool_val

def compare_results(res_dct,res_vo_dct,  threshold = 10):
    '''This  function compares the results res_dct and res_vo_dct (reference measurement)  '''
    list_keys_to_cmp = []
    list_keys_to_cmp.append('S_depth')
    list_keys_to_cmp.append('U_cov')
    list_keys_to_cmp.append('U_low')
    list_keys_to_cmp.append('U_skew')
    
    res  = {}
    alert_flag = {}
    for k in list_keys_to_cmp:
        
        if k=='U_low':
            list1 = res_dct[k]
            list2 = res_vo_dct[k]
            err_list = []
            alert_list = []
            for i in range(len(list1)):
                rel_err = np.abs(list2[i]-list1[i])/list2[i]*100
                alr_val = np.abs(rel_err) > threshold #!!!
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
                        
    return(res, alert_flag)    


def save_dct(obj, filename):
    ''' saves dictionary to pickle'''
    with open(filename,'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


#Seuraava kolme funktiota liittyvät logitiedoston kirjaukseen:
def line_prepender1(filename, line):
    '''Kirjoittaa merkkijonon tekstin alkuun ja jättää kaksi tyhjää riviä'''
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n\n' + content)

def line_prepender2(filename, line):
    '''Kirjoittaa merkkijonon tekstin alkuun ja jättää yhden tyhjän rivin'''
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)
        
def line_prepender_list(filename, list_line):
    '''Kirjoittaa merkkijonon listan  tiedoston filename alkuun'''
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        for txt in list_line:
            txt = '\t ' + txt
            f.write(txt.rstrip('\r\n') + '\n')
        f.write('\n')
        f.write(content)   