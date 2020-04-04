import socket
import threading
import time
from collections import deque

import numpy as np



class PNHandler:
    def __init__(self, config, TCP_IP='127.0.0.1', TCP_PORT = 7010, BUFFER_SIZE = 1800):
        
        self.config = config
        self.dtype = 'float64'
        
        # connection parameters
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        
        # init TCP socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # PN channels in order
        channels = ["J37, X pos", "J37, Y pos", "J37, Z pos", "J37, Yrot", "J37, Xrot", "J37, Zrot",
                    "J38, X pos", "J38, Y pos", "J38, Z pos", "J38, Yrot", "J38, Xrot", "J38, Zrot",
                    "J39, X pos", "J39, Y pos", "J39, Z pos", "J39, Yrot", "J39, Xrot", "J39, Zrot",
                    "J40, X pos", "J40, Y pos", "J40, Z pos", "J40, Yrot", "J40, Xrot", "J40, Zrot",
                    "J41, X pos", "J41, Y pos", "J41, Z pos", "J41, Yrot", "J41, Xrot", "J41, Zrot",
                    "J42, X pos", "J42, Y pos", "J42, Z pos", "J42, Yrot", "J42, Xrot", "J42, Zrot",
                    "J43, X pos", "J43, Y pos", "J43, Z pos", "J43, Yrot", "J43, Xrot", "J43, Zrot",
                    "J44, X pos", "J44, Y pos", "J44, Z pos", "J44, Yrot", "J44, Xrot", "J44, Zrot",
                    "J45, X pos", "J45, Y pos", "J45, Z pos", "J45, Yrot", "J45, Xrot", "J45, Zrot",
                    "J46, X pos", "J46, Y pos", "J46, Z pos", "J46, Yrot", "J46, Xrot", "J46, Zrot",
                    "J47, X pos", "J47, Y pos", "J47, Z pos", "J47, Yrot", "J47, Xrot", "J47, Zrot",
                    "J48, X pos", "J48, Y pos", "J48, Z pos", "J48, Yrot", "J48, Xrot", "J48, Zrot",
                    "J49, X pos", "J49, Y pos", "J49, Z pos", "J49, Yrot", "J49, Xrot", "J49, Zrot",
                    "J50, X pos", "J50, Y pos", "J50, Z pos", "J50, Yrot", "J50, Xrot", "J50, Zrot",
                    "J51, X pos", "J51, Y pos", "J51, Z pos", "J51, Yrot", "J51, Xrot", "J51, Zrot",
                    "J52, X pos", "J52, Y pos", "J52, Z pos", "J52, Yrot", "J52, Xrot", "J52, Zrot",
                    "J53, X pos", "J53, Y pos", "J53, Z pos", "J53, Yrot", "J53, Xrot", "J53, Zrot",
                    "J54, X pos", "J54, Y pos", "J54, Z pos", "J54, Yrot", "J54, Xrot", "J54, Zrot",
                    "J55, X pos", "J55, Y pos", "J55, Z pos", "J55, Yrot", "J55, Xrot", "J55, Zrot",
                    "J56, X pos", "J56, Y pos", "J56, Z pos", "J56, Yrot", "J56, Xrot", "J56, Zrot",
                    "J57, X pos", "J57, Y pos", "J57, Z pos", "J57, Yrot", "J57, Xrot", "J57, Zrot",
                    "J58, X pos", "J58, Y pos", "J58, Z pos", "J58, Yrot", "J58, Xrot", "J58, Zrot",
                    "J59, X pos", "J59, Y pos", "J59, Z pos", "J59, Yrot", "J59, Xrot", "J59, Zrot"]

        # circular buffer to store pn data
        self.buffer_pn = deque(maxlen = config['general'].getint('circular_buffer_size'))
        
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
        self._printm('Start receiving data from PN and put it into circular_buffer')
        start_time = time.time()
        string_buffer = ''
        while True:
            data_received = self.s.recv(self.BUFFER_SIZE) #Recieve a string of data from Axis Neuron
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