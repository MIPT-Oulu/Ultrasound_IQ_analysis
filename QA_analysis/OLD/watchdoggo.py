# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 14:38:01 2020

@author: sinkinen
"""

import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import os
import pickle
import UA_QA_analysis as QA

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import time
path = "C:/Users/sinkinen/US_analysis/data"



#%%
def sent_email(device_name, transducer_name):
    
    #import pdb; pdb.set_trace()
    #message:
    sent_from = 'quality.control.notes@gmail.com'
    to = ['quality.control.notes@gmail.com']
    
    subject = 'Analysis on device: ' +device_name + ' Transducer: '+transducer_name 
    body = 'Analyysi on tehty.'
    email_text = """\
    From: %s
    To: %s
    Subject: %s
    %s
    """ % (sent_from, ", ".join(to), subject, body)
     
    time.sleep(1)
    #tietoturva!
    gmail_user = 'quality.control.notes@gmail.com'
    gmail_password = '1BQA10N0tes'
    
    msg = MIMEMultipart()
    msg['From'] = 'quality.control.notes@gmail.com'
    msg['To'] = 'quality.control.notes@gmail.com'
    msg['Subject'] = 'Analysoitu laite:' +device_name + 'anturi: ' +   transducer_name
    text =  'Analysoitu laite: ' +device_name + ' anturi: ' +   transducer_name
    part1 = MIMEText(text, 'plain')
    msg.attach(part1)
    

    try:
        time.sleep(1)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, msg.as_string())
        time.sleep(5)
        server.close()
        print('Email sent!')
        
    except:
        print("Something went wrong")
        
def us_data_to_dict(data):
    dct = {'S_depth': data.S_depth,
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
        }
    
    return dct

def save_object(obj, filename):
    with open(filename,'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    patterns= "*"
    ignore_patters = ""
    ignore_directories = True
    case_sensitive = True
    my_event_handler =  PatternMatchingEventHandler(patterns, ignore_patters, ignore_directories, case_sensitive)
   #“ignore_directories” is just a boolean that we can set to True if we want to be notified just for regular files (not for directories) and the “case_sensitive” variable is just another boolean that, if set to “True”, made the patterns we previously introduced “case sensitive”
   
   
def on_created(event):
    print(f"hey, {event.src_path} has been created!")
    print("analyzing...")
    
    res = QA.MAIN_US_analysis(event.src_path)
    save_path = 'C:/Users/sinkinen/US_analysis/results/'
    #import pdb; pdb.set_trace()
    
    #make directories:
    directory_device = str(res.get_name()) #+'_'+str(res.get_transducer_name())
    path = os.path.join(save_path, directory_device) 
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)
        
    #make directories:
    directory_transducer = str(res.get_transducer_name())
    path = os.path.join(path, directory_transducer)
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)
    
    
    path_old = path
    uniq = 1
    while os.path.exists(path):
        path = path_old+'/%d' % (uniq)
        uniq += 1
    
    #sent email:
    sent_email(str(res.get_name()), str(res.get_transducer_name()))
    
    res = us_data_to_dict(res)
    save_object(res, path)

    print('done!')

def on_deleted(event):
    print(f"Someone deleted {event.src_path}!")

def on_modified(event):
    print(f"hey buddy, {event.src_path} has been modified")

def on_moved(event):
    print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")
    
    
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved



go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    

my_observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
    
    

    