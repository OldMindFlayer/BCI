# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 18:13:30 2018

@author: Александр
"""

import sys
from pylsl import StreamInlet, resolve_stream
import time
import numpy as np
import socket
import struct



class Decode():
    def __init__(self, config, inlet_amp, inlet_pn):
        self.config = config
        sys.path.append(self.config['paths']['root_path'] + '/myo/NEOREC')
        from EMGdecode import EMGDecoder
        from EMGfilter import envelopeFilter        
        
        self.inlet_amp = inlet_amp #myoInlet
        self.inlet_pn = inlet_pn #pnInlet
        self.exp_time = self.config['general'].getint('experiment_time_realtime')
        
        # for emulation of stream recieve
        #debug = False
        self.fps = 30
        self.tpf = 1/self.fps
        self.numCh = self.config['general'].getint('n_channels_amp')
        self.offCh = self.config['general'].getint('channels_pn_offset')
        self.srate = self.config['general'].getint('fs_amp')
        self.pos = 0
        
        self.coordbuff = []
        
        #PN channels for finger joints
        self.fingersrange = np.array([59,77,101,125])
        #avatar channels for finger joints
        self.fsendrange = np.array([14,23,32,41])
        
        #technical variables
        self.avatarBuffer = np.zeros(96)
        self.pnbuff = np.zeros((len(self.fingersrange)))
        
        
        #initializing Avatar connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('127.0.0.1', 12001)
        self.client_address = ('127.0.0.1', 9001)
        print('starting up on {} port {}'.format(*self.server_address))
        
        self.sock.bind(self.server_address)

        self.emgdecoder = EMGDecoder()
        self.emgdecoder.fit(X=None,Y=None,
                            file=self.config['paths']['experiment_data_path'],
                            numCh=self.numCh, offCh=64, 
                            Pn=[59,77,101,125], 
                            lag=2,forward=0,
                            downsample=0)
        self.emgfilter=envelopeFilter()
        
    
    def decode(self):
        start_time = time.time()
        while (time.time() - start_time < self.exp_time):
        
            start = time.time()
        
            chunk, timestamp = self.inlet_amp.pull_chunk()
            chunk = np.asarray(chunk)
            chunk_size = chunk.shape[0]
        
            pnchunk, timestamp = self.inlet_pn.pull_chunk()
            pnchunk = np.asarray(pnchunk)
            pnchunk_size = pnchunk.shape[0]
            
            if pnchunk_size > 0:
                pnchunk = pnchunk[:, self.fingersrange]
                for i in range(pnchunk.shape[1]):
                    t = pnchunk[:, i]
                    nans = np.isnan(t)
                    if sum(~nans) == 0:
                        t = self.pnbuff[i]
                    else:
                        t = np.median(t[~nans])
                    self.pnbuff[i] = t
            else:
                print('empty pn chunk encountered')
        
            if chunk_size > 0:
                
                chunk = chunk[:, :self.numCh]
                chunk = self.emgfilter.filterEMG(chunk)
                WienerCoords, KalmanCoords = self.emgdecoder.transform(chunk)
                
                #getting the last samples
                prediction = KalmanCoords[-1,:len(self.fingersrange)]   
                fact = np.copy(self.pnbuff)
        
        
                # self.fsendrange = np.array([14,23,32,41])
                self.avatarBuffer[self.fsendrange] = prediction
                self.avatarBuffer[self.fsendrange+3] = prediction
                self.avatarBuffer[self.fsendrange+6] = prediction/2
        
                self.avatarBuffer[self.fsendrange+48] = fact
                self.avatarBuffer[self.fsendrange+3+48] = fact
                self.avatarBuffer[self.fsendrange+6+48] = fact/2
                
                self.coordbuff.append((prediction,fact))
                
                #sending to the Avatar
                data2 = struct.pack('%df' % len(self.avatarBuffer), *list(map(float, self.avatarBuffer)))
                self.sock.sendto(data2, self.client_address)
                
            else:
                print('empty chunk encountered')
        
            dif = self.tpf - time.time() + start
            if dif > 0:
                time.sleep(dif)
            else:
                print("not enough time for chunk processing, latency is ", dif, ' s')
        
    def get_coordbuff(self):
        return self.coordbuff
    

