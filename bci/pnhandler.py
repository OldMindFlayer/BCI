# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 10:56:57 2020

@author: AlexVosk
"""

import socket
import threading
import time
from collections import deque

import numpy as np



class PNHandler:
    def __init__(self, config):
        
        self.config = config
        self.dtype = 'float64'
        
        # connection parameters
        self.TCP_IP = config['pn_config']['TCP_IP']
        self.TCP_PORT = config['pn_config'].getint('TCP_PORT')
        
        # init TCP socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # PN channels in order (fror dictionary-like representation check config.ini)
        self.channels = ['LeftShoulder posX','LeftShoulder posY','LeftShoulder posZ',
                         'LeftShoulder rotY','LeftShoulder rotX','LeftShoulder rotZ',
                         'LeftArm posX','LeftArm posY','LeftArm posZ',
                         'LeftArm rotY','LeftArm rotX','LeftArm rotZ',
                         'LeftForeArm posX','LeftForeArm posY','LeftForeArm posZ',
                         'LeftForeArm rotY','LeftForeArm rotX','LeftForeArm rotZ',
                         'LeftHand posX','LeftHand posY','LeftHand posZ',
                         'LeftHand rotY','LeftHand rotX','LeftHand rotZ',
                         'LeftHandThumb1 posX','LeftHandThumb1 posY','LeftHandThumb1 posZ',
                         'LeftHandThumb1 rotY','LeftHandThumb1 rotX','LeftHandThumb1 rotZ',
                         'LeftHandThumb2 posX','LeftHandThumb2 posY','LeftHandThumb2 posZ',
                         'LeftHandThumb2 rotY','LeftHandThumb2 rotX','LeftHandThumb2 rotZ',
                         'LeftHandThumb3 posX','LeftHandThumb3 posY','LeftHandThumb3 posZ',
                         'LeftHandThumb3 rotY','LeftHandThumb3 rotX','LeftHandThumb3 rotZ',
                         'LeftInHandIndex posX','LeftInHandIndex posY','LeftInHandIndex posZ',
                         'LeftInHandIndex rotY','LeftInHandIndex rotX','LeftInHandIndex rotZ',
                         'LeftHandIndex1 posX','LeftHandIndex1 posY','LeftHandIndex1 posZ',
                         'LeftHandIndex1 rotY','LeftHandIndex1 rotX','LeftHandIndex1 rotZ',
                         'LeftHandIndex2 posX','LeftHandIndex2 posY','LeftHandIndex2 posZ',
                         'LeftHandIndex2 rotY','LeftHandIndex2 rotX','LeftHandIndex2 rotZ',
                         'LeftHandIndex3 posX','LeftHandIndex3 posY','LeftHandIndex3 posZ',
                         'LeftHandIndex3 rotY','LeftHandIndex3 rotX','LeftHandIndex3 rotZ',
                         'LeftInHandMiddle posX','LeftInHandMiddle posY','LeftInHandMiddle posZ',
                         'LeftInHandMiddle rotY','LeftInHandMiddle rotX','LeftInHandMiddle rotZ',
                         'LeftHandMiddle1 posX','LeftHandMiddle1 posY','LeftHandMiddle1 posZ',
                         'LeftHandMiddle1 rotY','LeftHandMiddle1 rotX','LeftHandMiddle1 rotZ',
                         'LeftHandMiddle2 posX','LeftHandMiddle2 posY','LeftHandMiddle2 posZ',
                         'LeftHandMiddle2 rotY','LeftHandMiddle2 rotX','LeftHandMiddle2 rotZ',
                         'LeftHandMiddle3 posX','LeftHandMiddle3 posY','LeftHandMiddle3 posZ',
                         'LeftHandMiddle3 rotY','LeftHandMiddle3 rotX','LeftHandMiddle3 rotZ',
                         'LeftInHandRing posX','LeftInHandRing posY','LeftInHandRing posZ',
                         'LeftInHandRing rotY','LeftInHandRing rotX','LeftInHandRing rotZ',
                         'LeftHandRing1 posX','LeftHandRing1 posY','LeftHandRing1 posZ',
                         'LeftHandRing1 rotY','LeftHandRing1 rotX','LeftHandRing1 rotZ',
                         'LeftHandRing2 posX','LeftHandRing2 posY','LeftHandRing2 posZ',
                         'LeftHandRing2 rotY','LeftHandRing2 rotX','LeftHandRing2 rotZ',
                         'LeftHandRing3 posX','LeftHandRing3 posY','LeftHandRing3 posZ',
                         'LeftHandRing3 rotY','LeftHandRing3 rotX','LeftHandRing3 rotZ',
                         'LeftInHandPinky posX','LeftInHandPinky posY','LeftInHandPinky posZ',
                         'LeftInHandPinky rotY','LeftInHandPinky rotX','LeftInHandPinky rotZ',
                         'LeftHandPinky1 posX','LeftHandPinky1 posY','LeftHandPinky1 posZ',
                         'LeftHandPinky1 rotY','LeftHandPinky1 rotX','LeftHandPinky1 rotZ',
                         'LeftHandPinky2 posX','LeftHandPinky2 posY','LeftHandPinky2 posZ',
                         'LeftHandPinky2 rotY','LeftHandPinky2 rotX','LeftHandPinky2 rotZ',
                         'LeftHandPinky3 posX','LeftHandPinky3 posY','LeftHandPinky3 posZ',
                         'LeftHandPinky3 rotY','LeftHandPinky3 rotX','LeftHandPinky3 rotZ']

        # circular buffer to store pn data
        self.buffer_pn = deque(maxlen = config['pn_config'].getint('buffer_pn_size'))
        
        self.thread = threading.Thread(target=self._get_data, args=())
        self.thread.daemon = True


    def start(self):
        if self._connect_to_PN():
            self.thread.start()
        
    def get_next_chunk_pn(self):
        if len(self.buffer_pn) == 0:
            return (None, None)
        else:
            pn_chunk = []
            pn_timestamp = []
            while len(self.buffer_pn) > 0:
                sample = self.buffer_pn.popleft()
                pn_chunk.append(sample[0])
                pn_timestamp.append(sample[1])
            chunk_pn = np.asarray(pn_chunk, dtype = self.dtype )
            timestamp_pn = np.asarray(pn_timestamp, dtype = self.dtype )
            return chunk_pn, timestamp_pn 

    def clear_buffer_pn(self):
        self.buffer_pn.clear()

    def get_buffer_pn(self):
        return self.buffer_pn

    
    def _connect_to_PN(self):
        try:
            self.s.connect((self.TCP_IP, self.TCP_PORT))
            return True
        except ConnectionError:
            self._printm('ConnectionError, check:\nAxis Neuron -> File -> Settings -> Broadcasting ->\nchecked BVH, Port: {}, Format: String'.format(self.TCP_PORT))
            return False


    def _get_data(self):
        self._printm('Start receiving data from PN and put it into buffer_pn')
        start_time = time.time()
        string_buffer = ''
        while True:
            data_received = self.s.recv(1800) #Recieve a string of data from Axis Neuron
            try:
                data_received = data_received.decode("utf-8")
            except UnicodeDecodeError:
                self._printm('UnicodeDecodeError, check:\nBVH format: String, Axes Neuron version: 3.6.xxx')
                return
                        
            string_buffer += data_received
            index_start = string_buffer.find("C")
            index_stop = string_buffer.find("|", index_start)
            while index_start >= 0 and index_start < index_stop:
                chunk = string_buffer[index_start + 7: index_stop - 1]
                chunk_split = chunk.split(' ')
                sample = [float(chunk_split[i]) for i in range(216, len(chunk_split))]
                self.buffer_pn.append((sample, time.time() - start_time))
                string_buffer = string_buffer[index_stop:]
                index_start = string_buffer.find("C")
                index_stop = string_buffer.find("|", index_start)


    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)
     


if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    pnh = PNHandler(config, TCP_IP='127.0.0.1', TCP_PORT = 7010, BUFFER_SIZE = 1800)
    pnh.start()
    time.sleep(3)
    cb = pnh.get_buffer_pn()
    print(len(cb))