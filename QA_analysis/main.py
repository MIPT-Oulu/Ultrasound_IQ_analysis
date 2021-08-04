from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os
import pickle
import time
import argparse
import yaml
from datetime import date
from utils.utils import check_if_US_data, save_dct, compare_results, line_prepender1, line_prepender2, line_prepender_list
import utils.UA_QA_analysis as QA
import getpass


def dir_path(string):
     if os.path.isdir(string):
         return string
     else:
         raise NotADirectoryError(string)
        

#---- Initialization: ---- 

#Get the values from the settings.yaml file 
path = os.getcwd()
name = 'Settings.yaml'
path_name = os.path.join(path, name)
a_yaml_file = open(path_name)
dct = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
data_path = dct['data_path']
save_path = dct['save_path']
id2cmp = dct['id_us_analysis']
path_LUT_table = dct['path_LUT_table']
TH = dct['threshold_val']


log_filename = 'log_file.txt'


print('Ohjelma on käynnistynyt')
print('Sen voi sulkea ctrl+c tai sulkemalla tämän ikkunan')
#----------------


#%% --- Watch dog ---
if __name__ == "__main__":

    patterns= "*"
    ignore_patters = ""
    ignore_directories = True
    case_sensitive = True
    my_event_handler =  PatternMatchingEventHandler(patterns, ignore_patters, ignore_directories, case_sensitive)

   
def on_created(event):
    print(f"Tiedosto: {event.src_path} on tullut.")


    print('Tarksita onko dicom tiedosto:')
    if not event.src_path.endswith('.dcm'): #Hox oletus että tiedosto päättyy .dcm näin ei välttämättä aina ole vaikka onkin dicom.
        print('Ei ole dicom tiedosto')
        return None

    print('On Dicom tiedosto')

    print('Tarkista onko ultraääni-ilmakuva:')
    bool_val = check_if_US_data(event.src_path, id2cmp)
    if bool_val: 

        print("Analysoi...")
        res = QA.MAIN_US_analysis(event.src_path,path_LUT_table=path_LUT_table) #Analyysikoodi palauttaa dictionaryn

        
        #Rakenna tiedostosijainnit tuloksia varten:
        directory_device = str(res['name'])
        path = os.path.join(save_path, directory_device) 
        try:
            os.mkdir(path)
        except OSError as error:
            print("Laitteelta on jo analysoitu antureita")
            

        flag_analysoitu_aiemmin = False #init

        directory_transducer = str(res['transducer_name'])
        path = os.path.join(path, directory_transducer)
        try:
            os.mkdir(path)
        except OSError as error:
            print(error)
            print("Anturia on jo analysoitu aikaisemmin")
            flag_analysoitu_aiemmin = True
            path_vo_data = path+'/1' #vastaanottomittaus on eka.
            
        path_old = path
        uniq = 1
        while os.path.exists(path): #etsii ensimmäisen seuraavaksi vapaan luvun 1 lähtien
            path = path_old+'/%d' % (uniq)
            uniq += 1
        
        # --- Vertaa ensimmäiseen mittaukseen ---
        if  flag_analysoitu_aiemmin:
            with open(path_vo_data, 'rb') as handle:
                    res_vo_dct = pickle.load(handle)
            
            res_cmp, alert_flag = compare_results(res,res_vo_dct,  threshold = TH)             
        # ----------------------------------------

        # ---- Make log file ---- :
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        if flag_analysoitu_aiemmin: #eri kirjaukset jos on analysoitu aikaisemmin
            flag = False
            for v in alert_flag.items():
                if v==True:
                    flag = True
                
            if flag == False:
                #import pdb; pdb.set_trace()
                text_list = 'Analysoitu laite:'+res['name']+'Anturi: '+ res['transducer_name']
                text_list = 'OK '+ text_list
                line_prepender1(log_filename, text_list)
            else:            
                text_list = sent_cmp_email(gmail_user, gmail_password,str(res.get_name()), str(res.get_transducer_name()), res_cmp, alert_flag)
                if isinstance(text_list, list):
                    txt = text_list.pop(0)
                    line_prepender_list(log_filename,text_list)
                    line_prepender2(log_filename, d1 +' '+txt)
                else:
                    line_prepender1(log_filename, d1 +' '+text_list)
                    
        else: 
            
            text_list = 'Analysoitu laite:'+res['name']+' Anturi: '+ res['transducer_name']
            text_list = d1 +' OK '+ text_list
            line_prepender1(log_filename, text_list)

        #---------------------------------

        #------------- Tallennus -------- :
        save_dct(res, path)
        print('Valmis!')
        #---------------------------------

    

def on_deleted(event):
    print(f"{event.src_path} on poistettu.")

def on_modified(event):
    print(f"{event.src_path} tiedostoa on muokattu")

def on_moved(event):
    print(f"Siirto  {event.src_path} sijainnista {event.dest_path} sijaintiin.")


my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, data_path, recursive=go_recursively)
    
my_observer.start()
try:
    while True:
        time.sleep(3)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()