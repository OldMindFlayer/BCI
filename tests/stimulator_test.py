# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 03:16:25 2020

@author: AlexVosk
"""
from pathlib import Path
import sys
stimulator_path = str(Path('stimulator_test.py').resolve().parents[1]/'bci/')
sys.path.append(stimulator_path)

import time
import configparser
from stimulator import Stimulator

# test Stimulator class based on config

def test(config):
    stimulator = Stimulator(config)
    stimulator.connect()
    
    # stimulate from electrode 1 to electrode 2
    
    stimulator.configurate(2, 3)
    time.sleep(1)
    #stimulator.recieve_feedbeak()
    #stimulator.stimulate(2500, 1)
    #for i in range(20):
    #    stimulator.stimulate(i*10, 1)
    #    time.sleep(0.2)
    #t = 10000
    #sleep = 150
    #for i in range(t//sleep):
    #    stimulator.stimulate(i, 1)
        #time.sleep((sleep - i)/1000)
        #print('stimulation length {}'.format(i))

    # stimulate from electrode 2 to electrode 1
    #stimulator.configurate(1, 0)
    #t = 10000
    #sleep = 150
    #for i in range(t//sleep):
    #    stimulator.stimulate(100 - i, 1)
    #    time.sleep((sleep - i + 100)/1000)
    #    print('stimulation length {}'.format(100 - i))

    stimulator.close_connection()

if __name__ == '__main__':

    # parse configuration file and determine which tests to run
    config = configparser.ConfigParser()
    config.read('stimulator_config.ini')
    test_stimulation_disable = config['test'].getboolean('test_stimulation_disable')
    test_stimulation_imaginary = config['test'].getboolean('test_stimulation_imaginary')
    test_stimulation_real = config['test'].getboolean('test_stimulation_real')
    
    # test how Stimulation class react if stimulation is disabled
    if test_stimulation_disable:
        config['general']['stimulation_enable'] = 'false'
        test(config)
        print()
        
    # test how Stimulation class react if stimulation is imaginary
    # does not require stimulator, each stimulation just prints message
    if test_stimulation_imaginary:
        config['general']['stimulation_enable'] = 'true'
        config['stimulation']['stimulation_idle'] = 'true'
        test(config)
        print()
    
    # test how Stimulation class react if stimulation is real
    # require stimulator, preferably use oscillograph / amplifier to check correctness
    if test_stimulation_real :
        config['general']['stimulation_enable'] = 'true'
        config['stimulation']['imaginary'] = 'false'
        test(config)
    

    