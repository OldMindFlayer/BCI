# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 12:29:53 2020

@author: AlexVosk
"""

import time

import h5py
import pylsl
import numpy as np

class ExperimentRecord():
    def __init__(self, config, pnhandler, dtype = 'float64'):
        self.config = config
        self.pnhandler = pnhandler
        self.dtype = dtype
        
        streams = pylsl.resolve_byprop('name', config['general']['lsl_stream_name_amp'])
        self.inlet_amp = pylsl.StreamInlet(streams[0], 3)
        self.inlet_amp_info = self._stream_info(self.inlet_amp)
        self._printm('LSL stream \"{}\" resolved'.format(config['general']['lsl_stream_name_amp']))

        assert self.inlet_amp_info['n_channels'] == self.config['general'].getint('n_channels_amp'), 'wrong n_channels_amp'
        assert self.inlet_amp_info['fs'] == self.config['general'].getint('fs_amp'), 'wrong fs_amp'

        self.stacked_data = None
        self.stacked_timestamps = None


    def record_data(self):
        size = self.config['general'].getint('experiment_time_record')
        counter = 0
        curr_count = 0
        # init lists to store data
        stacked_chunks = []
        timestamps = []
        # clear buffer from PN
        self.pnhandler.clear_buffer_pn()

        self._printm('start recording {}+ samples'.format(size))
        while counter < size:
            # get chunks from amp
            ampchunk, amptimestamp = self.inlet_amp.pull_chunk(timeout = 0.0)
            chunk_amp, timestamp_amp = np.array(ampchunk, dtype=self.dtype), np.array(amptimestamp, dtype=self.dtype)
            if chunk_amp.shape[0] == 0:
                chunk_amp, timestamp_amp = (None, None)
            if chunk_amp is not None:
                # get chunks from pn and transform it into the same number of samples as in chunk_amp
                chunk_pn, timestamp_pn = self.pnhandler.get_next_chunk_pn()
                chunk_pn_to_stack = self._chunk_stack(chunk_amp, timestamp_amp, chunk_pn, timestamp_pn)
                # stack chunks into the same array: left part is amp data, right part is pn data
                stacked_chunk = np.hstack((chunk_amp, chunk_pn_to_stack))
                stacked_chunks.append(stacked_chunk)
                # as a timestamps use timestamps from amp
                timestamps.append(timestamp_amp)
                # print progress
                counter += stacked_chunk.shape[0]
                if counter // 1000 > curr_count:
                    self._printm('{} samples collected'.format(counter))
                    curr_count += 1
                    
        self.stacked_data = np.vstack(stacked_chunks)
        self.stacked_timestamps = np.concatenate(timestamps)
        self._save_data()

        self._printm('data saved:\n{}'.format(self.config['paths']['experiment_data_path']))
    
    
    
    def _chunk_stack(self, chunk_amp, timestamp_amp, chunk_pn, timestamp_pn):
        chunk_pn_to_stack = np.zeros((chunk_amp.shape[0], self.config['general'].getint('n_channels_pn'))) * np.nan
        if chunk_pn is not None:
            timestamp_pn = timestamp_pn - timestamp_pn[0] + timestamp_amp[0]
            chunk_pn_to_stack[np.searchsorted(timestamp_amp[:-1], timestamp_pn), :] = chunk_pn
        return chunk_pn_to_stack

    def _stream_info(self, inlet):
        stream_info = {'name': inlet.info().name(), 
                       'n_channels': inlet.info().channel_count(),
                       'fs': inlet.info().nominal_srate()}
        return stream_info
    
    
    def _save_data(self):
        with h5py.File(self.config['paths']['experiment_data_path'], 'w') as file:
            file.create_dataset('protocol1/raw_data', dtype=self.dtype, data=self.stacked_data)  
            file.create_dataset('protocol1/timestamp_data', dtype=self.dtype, data=self.stacked_timestamps) 
        

    def _get_next_chunk(self, inlet):
        chunk, timestamp = inlet.pull_chunk(timeout = 0.0)
        chunk, timestamp = np.array(chunk, dtype=self.dtype), np.array(timestamp, dtype=self.dtype)
        return (chunk, timestamp) if chunk.shape[0] > 0 else (None, None)

        
    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)
        


    def get_inlet_amp(self):
        return self.inlet_amp
