# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 18:13:30 2018

@author: Александр/AlexVosk
"""

import sys
import time
import numpy as np
import socket
import struct



class ExperimentRealtime():
    def __init__(self, config, inlet_amp, inlet_pn):
        self.config = config
        
        # lsl inlets
        self.inlet_amp = inlet_amp #myoInlet
        self.inlet_pn = inlet_pn #pnInlet
        
        # time of realtime experiment (inf if it set to -1)
        experiment_time = self.config['general'].getint('experiment_time_realtime')
        self.experiment_time = float('inf') if experiment_time < 0 else experiment_time
        
        # params of amp data stream
        self.numCh = self.config['general'].getint('n_channels_amp')
        self.offCh = self.numCh
        self.srate = self.config['general'].getint('fs_amp')

        avatar_freq = self.config['general'].getint('avatar_freq')
        self.avatar_period = 1 / avatar_freq
        self.avatar_buffer_size = self.config['general'].getint('avatar_buffer_size')
        
        # buffer for plotting
        self.coordbuff = []
        
        
        # PN channels for finger joints
        self.pn_fingers_range = np.asarray(list(map(int, self.config['general']['pn_fingers_range'].split())))
        # avatar channels for finger joints
        self.avatar_fingers_range = np.asarray(list(map(int, self.config['general']['avatar_fingers_range'].split())))
        
        # buffer
        self.avatar_buffer = np.zeros(self.avatar_buffer_size)
        
        
        # initializing Avatar connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('127.0.0.1', 12001)
        self.client_address = ('127.0.0.1', 9001)
        self.sock.bind(self.server_address)
        print('{} {}: UDP from {} {} established'.format(time.strftime('%H:%M:%S'), type(self).__name__, *self.server_address))

        # fit the model and initialize filter
        print('{} {}: fitting...'.format(time.strftime('%H:%M:%S'), type(self).__name__))
        self.decoder, self.filter = self._fit()
        print('{} {}: decoding...'.format(time.strftime('%H:%M:%S'), type(self).__name__))
        self.decode()
        
        
    # fit data from file
    def _fit(self):
        # load Decoder and Filter from NEOREC
        sys.path.append(self.config['paths']['root_path'] + '/MyoDecode/NEOREC')
        from EMGdecode import EMGDecoder
        from EMGfilter import envelopeFilter
        
        # fit the model from file and initialize filter
        emgdecoder = EMGDecoder()
        emgdecoder.fit(X = None, Y = None, 
                       file=self.config['paths']['experiment_data_path'], 
                       numCh = self.numCh, offCh = self.offCh, 
                       Pn = self.pn_fingers_range, 
                       lag = 2, forward = 0, downsample = 0)
        emgfilter = envelopeFilter()
        return emgdecoder, emgfilter
        
    
    # decode realtime data
    def decode(self):
        # initialize pn_buffer and KalmanCoords
        pn_buffer = np.zeros(len(self.pn_fingers_range))
        KalmanCoords = np.zeros((1, self.numCh))
        
        # get chunks, decode and sent to avatar
        start_time = time.time()
        while (time.time() - start_time < self.experiment_time):
            cycle_start_time = time.time()
        
            # get chunks of data from inlets
            pnchunk, _ = self.inlet_pn.pull_chunk()
            chunk_pn = np.asarray(pnchunk)
            chunk, _ = self.inlet_amp.pull_chunk()
            chunk_amp = np.asarray(chunk)
        
            # process chunks, if no chunks - previous data will be used
            if chunk_pn.shape[0] > 0:
                pn_buffer = self._process_chunk_pn(chunk_pn, pn_buffer)
            else:
                print('{} {}: empty pn chunk encountered'.format(time.strftime('%H:%M:%S'), type(self).__name__))
            if chunk_amp.shape[0] > 0:
                WienerCoords, KalmanCoords = self._process_chunk_amp(chunk_amp)            
            else:
                print('{} {}: empty chunk encountered'.format(time.strftime('%H:%M:%S'), type(self).__name__))
            
            # get predictions and factual result and send them to avatar
            prediction = KalmanCoords[-1,:len(self.pn_fingers_range)]   
            fact = np.copy(pn_buffer)
            self.coordbuff.append((prediction, fact))
            self._send_data_to_avatar(prediction, fact)
        
            # control time of each cycle of the loop 
            difference_time = self.avatar_period - (time.time() - cycle_start_time)
            if difference_time > 0:
                time.sleep(difference_time)
            else:
                print('{} {}: not enough time for chunk processing, latency is {} s'.format(time.strftime('%H:%M:%S'), type(self).__name__, difference_time))
        
    
    def _process_chunk_pn(self, chunk_pn, pn_buffer):
        chunk_pn = chunk_pn[:, self.pn_fingers_range]
        medians = np.nanmedian(chunk_pn, axis=0)
        pn_buffer[~np.isnan(medians)] = medians[~np.isnan(medians)]
        return pn_buffer
    
    def _process_chunk_amp(self, chunk_amp):
        chunk_amp = chunk_amp[:, :self.numCh]
        chunk_amp = self.filter.filterEMG(chunk_amp)
        WienerCoords, KalmanCoords = self.decoder.transform(chunk_amp)
        return WienerCoords, KalmanCoords
        
    def _send_data_to_avatar(self, prediction, fact):
        self.avatar_buffer[self.avatar_fingers_range] = fact
        #self.avatar_buffer[self.avatar_fingers_range + self.avatar_buffer_size//2 + 3] = fact
        #self.avatar_buffer[self.avatar_fingers_range + self.avatar_buffer_size//2 + 6] = fact/2
            
        self.avatar_buffer[self.avatar_fingers_range + self.avatar_buffer_size//2] = prediction
        #self.avatar_buffer[self.avatar_fingers_range + 3] = prediction
        #self.avatar_buffer[self.avatar_fingers_range + 6] = prediction/2
    
        data = struct.pack('%df' % len(self.avatar_buffer), *list(map(float, self.avatar_buffer)))
        self.sock.sendto(data, self.client_address)
        
        
    def get_coordbuff(self):
        return self.coordbuff
    

