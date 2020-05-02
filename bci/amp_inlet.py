# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 11:47:32 2020

@author: AlexVosk
"""
import time
import pylsl
    
def get_inlet_amp(config):
    printm('Resolving LSL stream from amplifier...')
    streams = pylsl.resolve_byprop('name', config['amp_config']['lsl_stream_name_amp'])
    inlet_amp = pylsl.StreamInlet(streams[0], 
                                  max_buflen = config['amp_config'].getint('max_buflen'), 
                                  max_chunklen = config['amp_config'].getint('max_chunklen'))
    printm('LSL stream \"{}\" resolved'.format(config['amp_config']['lsl_stream_name_amp']))
    return inlet_amp


def printm(m):
    print('{} {}: {}'.format(time.strftime('%H:%M:%S'), 'AmpInlet', m))