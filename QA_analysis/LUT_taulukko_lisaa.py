# -*- coding: utf-8 -*-
"""Taman koodin ajamalla saa lisattua LUT taulukkoon antureita"""
import os
import time
import argparse
import yaml
import pydicom
from LUT_table_codes import extract_parameters
import pandas as pd


def dir_path(string):
     if os.path.isdir(string):
         return string
     else:
         raise NotADirectoryError(string)


#Parser:    
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Lisataan LUT taulukkoon antureita')
parser.add_argument('--data_path', type = dir_path, default = 'C:/ultra/Codes/Codes/QA_analysis/US_samsun/dcms2',
                    help='hakemisto joka sisaltaa listattavat dicom tiedostot') 
parser.add_argument('--excel_writer_path', type = str, default = 'C:/ultra/Codes/Codes/QA_analysis/LUT.xls',
                    help='Hakemistopolku excel tiedostoon johon tiedot lisataan automaattisesti') 
 
args = parser.parse_args()
data_path  = args.data_path
excel_writer = args.excel_writer_path

filenames = os.listdir(data_path)
#import pdb; pdb.set_trace()

for filename in filenames: #Tama looppi kay dcm tiedostot lapi ja lisaa metatiedot taulukkoon
    
    data = pydicom.dcmread(os.path.join(data_path, filename))
    dct_params = extract_parameters(data, get_name = True)
    
    df1 = pd.DataFrame(data = dct_params)
    try: 
        df = pd.read_excel(excel_writer)
    except:
        df = pd.DataFrame({})
    try:
        df.drop(['Unnamed: 0'], axis = 1, inplace=True)
    except:
        None
        
    frames = [df, df1]
    df_total = pd.concat(frames)        
    df_total.to_excel(excel_writer)   