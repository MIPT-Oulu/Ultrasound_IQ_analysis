import pydicom
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import os
mpl.rcParams["figure.dpi"] = 150


def extract_parameters(data, get_name = False):
    '''This function extract metadata information on the dicom and outputs to dictionary'''
    
    dct_params_1 = {'Model_name': 0x00081090,
                  'Manufacturer':0x00080070}
    dct_params_2 = {'RCX0': 0x00186018,
                  'RCY0': 0x0018601a,
                  'RCX1': 0x0018601c,
                  'RCY1': 0x0018601e,
                  'Phys_units_X': 0x00186024,
                  'Phys_units_Y': 0x00186026,
                  'Phys_delta_X': 0x0018602c,
                  'Phys_delta_Y': 0x0018602e}
    
    
    seq = data[0x0018, 0x6011]
    data_sub = seq[0]
    
    dct_params={}            
    for key in dct_params_1.keys():    
        try: # tämä sen takia että välttämättä aina ei löydy kaikkia dicom headeri kenttiä
            dct_params[key] = [data[dct_params_1[key]].value]
        except:
            dct_params[key] = ['None']
            
    for key in dct_params_2.keys():    
        try: # tämä sen takia että välttämättä aina ei löydy kaikkia dicom headeri kenttiä
            dct_params[key] = [data_sub[dct_params_2[key]].value]
        except:
            dct_params[key] = ['None']
    
    if get_name:
        plt.imshow(data.pixel_array), plt.show()
        cond = 'N'
        while cond == 'N':
            answer = input('Give the name of the transducer: ')
            print(answer)
            cond = input('Is the name okay [Y/N]?' )
        
            dct_params['Transducer_name'] =  [answer]
    #print(dct_params)
    
    return dct_params

def get_name_from_df(df, df1):
    '''This function fetches the name from df based on information in df1 '''
    #Compare:
    res = df.loc[(df['Model_name']==df1['Model_name'][0])
        & (df['RCX0'] == df1['RCX0'][0])
        & (df['RCY0'] == df1['RCY0'][0])
        & (df['RCX1'] == df1['RCX1'][0])
        & (df['RCY1'] == df1['RCY1'][0])
        & (df['Phys_units_X'] == df1['Phys_units_X'][0])
        & (df['Phys_units_Y'] == df1['Phys_units_Y'][0])
        & (df['Phys_delta_X'] == df1['Phys_delta_X'][0]) 
        & (df['Phys_delta_Y'] == df1['Phys_delta_Y'][0])]

    if res.empty:
        name = 'Not_found_from_LUT' #if no name then return this
    else:
        name = res.iloc[0]['Transducer_name']#get name
    
    return name

#%%
if __name__ == "__main__":

    data_path = 'D:/AI_laatu/US_analysis/data_old/samsungmammo/'
    filenames = os.listdir(data_path)

    excel_writer = 'D:/AI_laatu/US_analysis/LUT2.xls'

    
    for filename in filenames:
        
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
#%%
    #% testaa toimiiko LUT:
    
    df = pd.read_excel(excel_writer)
    try:
        df.drop(['Unnamed: 0'], axis = 1, inplace=True)
    except:
        None
    excel_writer = 'D:/AI_laatu/US_analysis/LUT.xls'
    
    data_path = 'D:/AI_laatu/US_analysis/data_old/samsungmammo/'
    filenames = os.listdir(data_path)
    name_list = []
    for filename in filenames:
        
        data = pydicom.dcmread(os.path.join(data_path, filename))
        dct_params = extract_parameters(data)
        df1 = pd.DataFrame(data = dct_params)
        
        name = get_name_from_df(df, df1)
        name_list.append(name)
        
        #%%
    print(name_list == df['Transducer_name']) 
     
    print(name_list)
    print(df['Transducer_name'])    
    
        
