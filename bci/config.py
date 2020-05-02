# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:37:29 2020

@author: dblok
"""

import configparser
import time
from os import makedirs
from pathlib import Path

def config_init(argv):
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # parse arguments 
    if '-debug' in argv:
        config['general']['debug_mode'] = 'true'
    else:
        config['general']['debug_mode'] = 'false'

    
    # Path autogeneration ignores path in config and generate path based on location of 'main.py'
    if config['general'].getboolean('path_autogeneration'):
        if len(Path('main.py').resolve().parents) >= 3:
            config['paths']['root_path'] = str(Path('main.py').resolve().parents[2])
        else:
            config['paths']['root_path'] = str(Path('main.py').resolve().parents[1]) 
        
    # Date and time autogeneration ignores values in config and generate them based on current date and time
    if  config['general'].getboolean('experiment_date_and_time_autogeneration'):
        config['patient_info']['patient_date'] = time.strftime('%y%m%d')
        config['patient_info']['patient_time'] = time.strftime('%H%M%S')
    
    
    # get parts of paths from config file
    root_path = Path(config['paths']['root_path'])
    patient_name = config['patient_info']['patient_name']
    patient_date = config['patient_info']['patient_date']
    patient_time = config['patient_info']['patient_time']
    
    # create Path objects for 'experiment_data' and 'results' directories
    patient_path = root_path/'BCIData'/(config['patient_info']['patient_date'] + '_' + \
                                        config['patient_info']['patient_time'] + '_' + \
                                        config['patient_info']['patient_name'])
    experiment_data_path = patient_path/'experiment_data.h5'
    results_path = patient_path/'results'
    # create directories
    makedirs(results_path, exist_ok=True)
    
    # Create directory stucture for experiment and update config with 'patient_data_path'
    config['paths']['patient_path'] = str(patient_path)
    config['paths']['results_path'] = str(results_path)
    if config['general'].getboolean('debug_mode'):
        config['paths']['lsl_stream_generator_path'] = str(root_path/'nfb/')
    
    if config['general'].getboolean('record_enable'):
        config['paths']['experiment_data_path'] = str(experiment_data_path)
        config['paths']['experiment_data_to_fit_path'] = config['paths']['experiment_data_path']
    else:
        config['paths']['experiment_data_path'] = None
    
    #config['record']['record'] = config['general']['record_enable']
    #config['realtime']['realtime'] = config['general']['realtime_enable']
    #config['stimulation']['stimulation'] = config['general']['stimulation_enable']

        
    # save result into global config file and local config file    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    with open(patient_path/'experiment_config.ini', 'w') as configfile:
        config.write(configfile)
        
    return config

if __name__ == '__main__':
    config_init([])