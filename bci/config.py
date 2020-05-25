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
    
    # parse arguments of main.py
    parse_argv(config, argv)
    
    # create base root path for path autogeneration or in case of path errors
    # variable root_path will have Path object to the root
    if len(Path('main.py').resolve().parents) >= 3:
        root_path_base = Path('main.py').resolve().parents[2]
    else:
        root_path_base = Path('main.py').resolve().parents[2]
    
    if config['paths'].getboolean('path_autogeneration'):
        config['paths']['root_path'] = str(root_path_base)
        root_path = root_path_base
    else:
        try:
            root_path = Path(config['paths']['root_path'])
        except:
            printm('can\'t parse root path from config, base root path:\n{}'.format(str(root_path_base)))
            config['paths']['root_path'] = str(root_path_base)
            root_path = root_path_base
        
    # Date and time autogeneration ignores values in config and generate them based on current date and time
    if  config['paths'].getboolean('experiment_date_and_time_autogeneration'):
        config['patient_info']['patient_date'] = time.strftime('%y%m%d')
        config['patient_info']['patient_time'] = time.strftime('%H%M%S')
    
    # create Path objects for 'experiment_data' and 'results' directories
    patient_path = root_path/'BCIData'/(config['patient_info']['patient_date'] + '_' + \
                                        config['patient_info']['patient_time'] + '_' + \
                                        config['patient_info']['patient_name'])
    train_data_path = patient_path/'train_data.h5'
    results_path = patient_path/'results'
    realtime_data_path = results_path/'realtime_data.h5'
    # create directories
    makedirs(results_path, exist_ok=True)
    
    # Create directory stucture for experiment and update config with 'patient_data_path'
    config['paths']['patient_path'] = str(patient_path)
    config['paths']['results_path'] = str(results_path)
    config['paths']['realtime_data_path'] = str(realtime_data_path)
    if config['general'].getboolean('debug_mode'):
        # add path to the debug lsl generator
        config['paths']['lsl_stream_generator_path'] = str(root_path/'nfb/')
    
    
    if config['general'].getboolean('record_enable'):
        config['paths']['train_data_path'] = str(train_data_path)
        config['paths']['train_data_to_fit_path'] = config['paths']['train_data_path']
    else:
        config['paths']['train_data_path'] = 'None'

    # save result into global config file and local config file    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    with open(patient_path/'experiment_config.ini', 'w') as configfile:
        config.write(configfile)
        
    return config

def parse_argv(config, argv):
    # debug mode, uses lsl generator instead if amplifier data
    if '-debug' in argv:
        config['general']['debug_mode'] = 'true'
    else:
        config['general']['debug_mode'] = 'false'
        
    # record mode, only records data and saves it
    # realtime mode, only fits existing data from 'experiment_data_to_fit_path' and runs realtime experiment
    # default mode, records data, fits it and runs realtime experiment
    # without arguments - tries to use parameters from config.ini, if can't - default mode
    if '-record' in argv:
        config['general']['record_enable'] = 'true'
        config['general']['realtime_enable'] = 'false'
    elif '-realtime' in argv:
        config['general']['record_enable'] = 'false'
        config['general']['realtime_enable'] = 'true'
    elif '-default' in argv:
        config['general']['record_enable'] = 'true'
        config['general']['realtime_enable'] = 'true'
    else:
        if type(config['general'].getboolean('record_enable')) is not bool or \
            type(config['general'].getboolean('realtime_enable')) is not bool:
            config['general']['record_enable'] = 'true'
            config['general']['realtime_enable'] = 'true'
            
    
        
        

def printm(m):
    print('{} {}: {}'.format(time.strftime('%H:%M:%S'), 'Config', m))
    


if __name__ == '__main__':
    config_init([])