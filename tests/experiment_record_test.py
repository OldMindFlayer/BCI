# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 12:29:53 2020

@author: AlexVosk
"""

import time
import configparser
from pathlib import Path
import sys
from os import makedirs
experiment_record_path = str(Path('pnhandler_test.py').resolve().parents[1]/'bci/')
sys.path.append(experiment_record_path)
from threading import Thread

from pnhandler import PNHandler
from amp_inlet import get_inlet_amp
from experiment_record import ExperimentRecord

# function that create directories for the recording data 
# and add paths to the data and to the lsl generator
def mod_config(config):
    root_path = Path('pnhandler_test.py').resolve().parents[2]
    config['paths']['root_path'] = str(root_path)
    patient_date = time.strftime('%y_%m_%d')
    patient_time = time.strftime('%H%M%S')
    patient_path = root_path/'BCIData'/(patient_date + '_' + patient_time + '_' + 'Test')
    experiment_data_path = patient_path/'experiment_data.h5'
    results_path = patient_path/'results'
    makedirs(results_path, exist_ok=True)
    config['paths']['experiment_data_path'] = str(experiment_data_path)
    config['paths']['lsl_stream_generator_path'] = str(root_path/'nfb/')
    return config

# start generate lsl like it is from amplifier
def start_debug_amp(config):
    sys.path.append(config['paths']['lsl_stream_generator_path'])
    sys.path.append(config['paths']['lsl_stream_generator_path'] + '/pynfb')
    from generators import run_eeg_sim
    freq = config['amp_config'].getint('fs_amp')
    name = config['amp_config']['lsl_stream_name_amp']
    labels = ['channel{}'.format(i) for i in range(config['amp_config'].getint('n_channels_amp'))]
    lsl_stream_debug = lambda: run_eeg_sim(freq, name=name, labels=labels)
    lsl_stream_debug_tread = Thread(target=lsl_stream_debug, args=())
    lsl_stream_debug_tread.daemon = True
    lsl_stream_debug_tread.start()
    print("generators.run_eeg_sim start DEBUG LSL \"{}\"".format(config['amp_config']['lsl_stream_name_amp']))



def test(config):
    # emulate amplifire lsl
    mod_config(config)
    if config['general'].getboolean('debug_mgde'):
        start_debug_amp(config)
    time.sleep(1.5)
    
    # start pnhandler, active Axis Neuron is needed
    pnhandler = PNHandler(config)
    pnhandler.start()
    inlet_amp = get_inlet_amp(config)
    time.sleep(1.5)
    
    # test ExperimentRecord class and it's record_data method
    experiment_record = ExperimentRecord(config, pnhandler, inlet_amp)
    experiment_record.record_data()
    
    
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('experiment_record_config.ini')
    
    test(config)