# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 12:29:53 2020

@author: AlexVosk
"""

import h5py
import pylsl
import numpy as np
import time

class Experiment():
    def __init__(self, config, dtype = 'float64'):
        self.config = config
        self.dtype = dtype
        
        self.inlet_amp = self._connent_LSL_strams(config['general']['lsl_stream_name_amp'], 3)
        self.inlet_amp_info = self._stream_info(self.inlet_amp)

        self.inlet_pn = self._connent_LSL_strams(config['general']['lsl_stream_name_pn'], 3)
        self.inlet_pn_info = self._stream_info(self.inlet_pn)

        assert self.inlet_amp_info['n_channels'] == self.config['general'].getint('n_channels_amp'), 'wrong n_channels_amp'
        assert self.inlet_amp_info['fs'] == self.config['general'].getint('fs_amp'), 'wrong fs_amp'
        assert self.inlet_pn_info['n_channels'] == self.config['general'].getint('n_channels_pn'), 'wrong n_channels_pn'
        assert self.inlet_pn_info['fs'] == self.config['general'].getint('fs_pn'), 'wrong fs_pn'
        
        self.stacked_data = None
        self.stacked_timestamps = None

        
        
    def _connent_LSL_strams(self, name, maxbuffer_size):
        streams = pylsl.resolve_byprop('name', name)
        inlet = pylsl.StreamInlet(streams[0], maxbuffer_size)
        print('{} {}: LSL stream \"{}\" resolved'.format(time.strftime('%H:%M:%S'), type(self).__name__, name))
        return inlet
        
    def _stream_info(self, inlet):
        stream_info = {'name': inlet.info().name(), 
                       'n_channels': inlet.info().channel_count(),
                       'fs': inlet.info().nominal_srate()}
        return stream_info

    def record_data(self, size):
        counter = 0
        curr_count = 0
        stacked_chunks = []
        timestamps = []
        
        while counter < size:
            chunk_amp, timestamp_amp = self._get_next_chunk(self.inlet_amp)
            if chunk_amp is not None:
                #print(chunk_amp.shape)
                chunk_pn, timestamp_pn = self._get_next_chunk(self.inlet_pn)
                chunk_pn_to_stack = np.zeros((chunk_amp.shape[0], self.inlet_pn_info['n_channels'])) * np.nan
                if chunk_pn is not None:
                    chunk_pn_to_stack[np.searchsorted(timestamp_amp[:-1], timestamp_pn), :] = chunk_pn
                stacked_chunk = np.hstack((chunk_amp, chunk_pn_to_stack))
                stacked_chunks.append(stacked_chunk)
                timestamps.append(timestamp_amp)
                counter += stacked_chunk.shape[0]
                if counter // 1000 > curr_count:
                    print('{}: {} samples collected'.format(type(self).__name__, counter))
                    curr_count += 1
                    
        self.stacked_data = np.vstack(stacked_chunks)
        self.stacked_timestamps = np.concatenate(timestamps)
        self._save_data()
        print('{} {}: data saved:\n{}'.format(time.strftime('%H:%M:%S'), type(self).__name__, self.config['paths']['experiment_data_path']))
    
    
    def _save_data(self):
        with h5py.File(self.config['paths']['experiment_data_path'], 'w') as file:
            file.create_dataset('protocol1/raw_data', dtype=self.dtype, data=self.stacked_data)  
            file.create_dataset('protocol1/timestamp_data', dtype=self.dtype, data=self.stacked_timestamps) 
        
    def _get_next_chunk(self, inlet):
        chunk, timestamp = inlet.pull_chunk(timeout = 0.0)
        chunk, timestamp = np.array(chunk, dtype=self.dtype), np.array(timestamp, dtype=self.dtype)
        return (chunk, timestamp) if chunk.shape[0] > 0 else (None, None)

    def get_inlet_amp(self):
        return self.inlet_amp

    def get_inlet_pn(self):
        return self.inlet_pn
