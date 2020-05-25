# -*- coding: utf-8 -*-
"""
Created on Sun May  3 02:18:01 2020

@author: AlexVosk
"""
import time
import configparser
from pathlib import Path
import sys
experiment_realtime_path = str(Path('experiment_realtime_test.py').resolve().parents[1]/'bci/')
sys.path.append(experiment_realtime_path)
from threading import Thread

from pnhandler import PNHandler
from amp_inlet import get_inlet_amp
from experiment_realtime import ExperimentRealtime
from stimulator import Stimulator


def mod_config(config):
    root_path = Path('experiment_realtime_test.py').resolve().parents[2]
    train_data_path = Path('experiment_realtime_test.py').resolve().parents[0]/'test_data/train_data.h5'
    realtime_data_path = Path('experiment_realtime_test.py').resolve().parents[0]/'test_data/results/realtime_data.h5'
    config['paths']['realtime_data_path'] = str(realtime_data_path)
    config['paths']['train_data_to_fit_path'] = str(train_data_path)
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
    if config['general'].getboolean('debug_mode'):
        start_debug_amp(config)
    time.sleep(1.5)
    
    # start pnhandler, active Axis Neuron is needed
    pnhandler = PNHandler(config)
    pnhandler.start()
    inlet_amp = get_inlet_amp(config)
    time.sleep(1.5)
    
    # init idle stimulator
    stimulator = Stimulator(config)
    stimulator.connect()

    
    # test ExperimentRealtime class and it's methods
    experiment_realtime = ExperimentRealtime(config, pnhandler, inlet_amp, stimulator)
    experiment_realtime.fit()
    experiment_realtime.decode()    
    
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('experiment_realtime_config.ini')
    
    test(config)

