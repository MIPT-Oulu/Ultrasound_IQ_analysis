from flask import Flask, render_template, session
from os.path import join
import json
from utils.util import read_log_file2, get_settings_dct, get_filenames,Convert,read_pickle,get_trend_data
from datetime import datetime

app = Flask(__name__)

# ---- Routes ----
@app.route('/devices')
def devices_page():
    """List the devices in HTML page"""
    dct = get_settings_dct()
    path_data = dct['path_data'] 
    device_names = get_filenames(path_data)
    device_names =  Convert(device_names) 
    return render_template('devices.html', names = device_names)

@app.route('/device/<string:id>/')
def device(id):
    """List the transducers in HTML page"""
    dct = get_settings_dct()
    path_data = dct['path_data'] 

    device_names = get_filenames(path_data)
    device_names =  Convert(device_names) 
    name = device_names[int(id)].get('name') 
    session["device_id"] = int(id)
    session["device_path"] = join( path_data,name)

    transducer_names = get_filenames(join( path_data,name))
    transducer_names =  Convert(transducer_names) 

    return render_template('device.html', names = transducer_names)     
    
@app.route('/transducer/<string:id>/')
def transducer(id):
    """Lists transducer measurements in HTML page"""
    path2device = session["device_path"]
    transducer_names = get_filenames(path2device)
    transducer_names =  Convert(transducer_names)
    name = transducer_names[int(id)].get('name') 

    session["transducer_path"] = join(path2device, name) 

    measurement_names = get_filenames(join( path2device,name))
    measurement_names =  Convert(measurement_names) 

    return render_template('transducer.html', names = measurement_names) 

@app.route('/measurement/<string:id>/')
def measurement(id):
    """Visualizes the dashboard"""
    measurement_names = get_filenames(session["transducer_path"])
    measurement_names =  Convert(measurement_names) 
    name = measurement_names[int(id)].get('name') 
    session["measurement_path"] = join(session["transducer_path"], name) 

    return render_template('dashboard.html', id = id)

@app.route('/trendi/')
def trendi():
    """Makes the trend plots in HTML page""" 
    measurement_names = get_filenames(session["transducer_path"])
    measurement_names =  Convert(measurement_names) 

    return render_template('plot_trends.html')

@app.route("/data")
def data():
    """Transform dictionary to JSON and put to /data"""
    objs = read_pickle(session["measurement_path"])
    dct = objs[0]
    y = json.dumps(dct)
    return y

@app.route("/trend_data")
def trend_data():
    """Transform dictionary to JSON and put to /trend_data"""
    dct = get_settings_dct()
    res_dct = get_trend_data(session["transducer_path"], n_samples=dct['n_samples'])
    
    data = res_dct['dates']
    dt = [datetime.strptime(s, '%Y%m%d') for s in data] 
    dt_str = [s.strftime('%d-%m-%Y') for s in dt]
    res_dct['dates'] = dt_str


    y = json.dumps(res_dct)
    return y

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    """Show about HTML page"""
    return render_template('about.html')     

@app.route('/log')
def log():
    """Show log file"""
    dct = get_settings_dct()
    log_list  =  read_log_file2(dct['path_log'])
    return render_template('log.html', log = log_list)    


if __name__=='__main__':
    app.secret_key = 'super secret key' #this is needed to start the program locally

    app.run(debug = True)