# -*- coding: utf-8 -*-
"""
Created on Sun May 17 16:35:42 2020

@author: AlexVosk
"""



import time

import h5py
import numpy as np
from scipy.interpolate import interp1d


class Recorder():
    def __init__(self, config, prediction):
        self.config = config
        self.dtype = 'float64'
        self.prediction = prediction
        self.interpolate = True
        
        self.stacked_timestamps = []
        self.stacked_chunks_amp = []
        self.stacked_chunks_pn = []
        self.data_timestamps = None
        self.data_amp = None
        self.data_pn = None
        
        if not self.prediction:
            self.data_save_path = self.config['paths']['train_data_path']
        else:
            self.data_save_path = self.config['paths']['realtime_data_path']
            self.stacked_predictions = []    
            self.data_predictions  = None
        



    def record_data(self, chunk_amp, timestamp_amp, chunk_pn, timestamp_pn, prediction = None):
        # record only of there is nonzero chunk from amplifier
        chunk_length = chunk_amp.shape[0]
        if chunk_length == 0:
            chunk_amp, timestamp_amp = (None, None)
        if chunk_amp is not None:
            # get chunks from pn and transform it into the same number of samples as in chunk_amp
            chunk_pn_to_stack = np.zeros((chunk_length, self.config['pn_config'].getint('n_channels_pn'))) * np.nan
            if chunk_pn is not None:
                timestamp_pn = timestamp_pn - timestamp_pn[0] + timestamp_amp[0]
                chunk_pn_to_stack[np.searchsorted(timestamp_amp[:-1], timestamp_pn), :] = chunk_pn
            # append lists of chunks
            self.stacked_timestamps.append(timestamp_amp)
            self.stacked_chunks_pn.append(chunk_pn_to_stack)
            self.stacked_chunks_amp.append(chunk_amp)
            
            # if we want to record predictions, record them into the middle of nan chunk
            if self.prediction and prediction is not None:
                prediction_to_stack = np.zeros((chunk_length, len(prediction))) * np.nan
                prediction_to_stack[chunk_length//2,:] = prediction 
                self.stacked_predictions.append(prediction_to_stack)


    def save_data(self):
        self.data_timestamps = np.concatenate(self.stacked_timestamps)
        self.data_amp = np.vstack(self.stacked_chunks_amp)
        self.data_pn = np.vstack(self.stacked_chunks_pn)
        if self.interpolate:
            self.data_pn = self._intrapolate(self.data_pn)
        if self.prediction:
            self.data_predictions = np.vstack(self.stacked_predictions)
            self.data_predictions = self._intrapolate(self.data_predictions)
        
        # save into file
        with h5py.File(self.data_save_path, 'w') as file:
            file.create_dataset('data_timestamps', dtype=self.dtype, data=self.data_timestamps)  
            file.create_dataset('data_amp', dtype=self.dtype, data=self.data_amp)  
            file.create_dataset('data_pn', dtype=self.dtype, data=self.data_pn)
            if self.prediction:
                file.create_dataset('data_predictions', dtype=self.dtype, data=self.data_predictions)
        self._printm('data saved:\n{}'.format(self.data_save_path))
    
        with h5py.File(self.data_save_path,'r+') as file:
            for dataset in file.keys():
                print(dataset)
                print(file[dataset])
    
    
    
    
    def _intrapolate(self, data):
        nans = np.isnan(data[:,0])
        nan_indices = nans.nonzero()[0]
        not_nan_indices = (~nans).nonzero()[0]
        if len(not_nan_indices) == 0:
            data = np.zeros(data.shape)
        elif len(not_nan_indices) == 1:
            data[:,:] = data[not_nan_indices,:]
        elif len(not_nan_indices) >= 2:
            interpolator = interp1d(not_nan_indices, data[not_nan_indices], 
                                    kind='linear', axis=0, 
                                    bounds_error=False, fill_value='extrapolate')
            data[nan_indices, :] = interpolator(nan_indices)
        return data
        
    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)




if __name__ == '__main__':
    pass
    
    
    
    
    
    
    
    
    
    
    
    
    