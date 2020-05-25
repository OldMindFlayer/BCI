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
experiment_record_path = str(Path('recorder_test.py').resolve().parents[1]/'bci/')
sys.path.append(experiment_record_path)
import numpy as np
import h5py

from recorder import Recorder

# function that create directories for the recording data 
# and add paths to the data and to the lsl generator
def mod_config(config):
    root_path = Path('recorder_test.py').resolve().parents[2]
    config['paths']['root_path'] = str(root_path)
    patient_date = time.strftime('%y_%m_%d')
    patient_time = time.strftime('%H%M%S')
    patient_path = root_path/'BCIData'/(patient_date + '_' + patient_time + '_' + 'Test')
    train_data_path = patient_path/'train_data.h5'
    results_path = patient_path/'results'
    realtime_data_path = results_path/'realtime_data.h5'
    makedirs(results_path, exist_ok=True)
    config['paths']['train_data_path'] = str(train_data_path)
    config['paths']['realtime_data_path'] = str(realtime_data_path)
    return config


def test_record(config):
    chank_amp = np.random.normal(0,1,16).reshape(8,2)
    timestemp_amp = np.arange(8)

    def get_pn(n):
        if n == 0:
            return None, None
        chunk_pn = np.random.normal(0,1,n*3).reshape(n,3)
        timestemp_pn = np.random.choice(np.arange(8), n) + 0.5
        return chunk_pn, timestemp_pn
    
    rec = Recorder(config, prediction= False)
    for i in range(3):
        chunk_pn, timestemp_pn = get_pn(i*3)
        rec.record_data(chank_amp, timestemp_amp, chunk_pn, timestemp_pn)
    rec.save_data()
    print_file(config['paths']['train_data_path'])
    
def test_record_predictions(config):
    chank_amp = np.random.normal(0,1,16).reshape(8,2)
    timestemp_amp = np.arange(8)

    def get_pn(n):
        if n == 0:
            return None, None
        chunk_pn = np.random.normal(0,1,n*3).reshape(n,3)
        timestemp_pn = np.random.choice(np.arange(8), n) + 0.5
        return chunk_pn, timestemp_pn
    
    rec = Recorder(config, prediction = True)
    for i in range(3):
        chunk_pn, timestemp_pn = get_pn(i*3)
        pred = [i, i, i, i, i]
        rec.record_data(chank_amp, timestemp_amp, chunk_pn, timestemp_pn, pred)
        
    rec.save_data()
    print_file(config['paths']['realtime_data_path'])
    
    
    
def print_file(path):
    with h5py.File(path,'r+') as file:
        for dataset in file.keys():
            pass
            #print(dataset)
            #print(file[dataset].shape)
    
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('recorder_config.ini')
    
    test_record(config)
    print()
    test_record_predictions(config)