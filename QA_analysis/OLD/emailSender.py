# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 15:27:48 2020

@author: sinkinen
"""

import smtplib

def sent_email(device_name, transducer_name):
    
    import pdb; pdb.set_trace()
    #message:
    sent_from = 'quality.control.notes@gmail.com'
    to = ['quality.control.notes@gmail.com']
    
    subject = 'Analysis on device: ' +device_name + ' Transducer: '+transducer_name 
    body = 'Analyysi on tehty. laite: '
    email_text = """\
    From: %s
    To: %s
    Subject: %s
    %s
    """ % (sent_from, ", ".join(to), subject, body)
     
    #tietoturva!
    gmail_user = 'quality.control.notes@gmail.com'
    gmail_password = '1BQA10N0tes'
    
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        print('Email sent!')
        
    except:
        print("Something went wrong")
        
    