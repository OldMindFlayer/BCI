# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 20:48:25 2020

@author: AlexVosk
"""

import sys
import time
import socket
import struct

import h5py
import numpy as np

name = 'finger_index.h5'


finger_pn = [0, 1, 2, 3, 4]
finger_avatar = [0, 1, 2, 3, 4]
avatar_buffer = np.zeros(10)
assert len(finger_pn) == len(finger_avatar)


with h5py.File(name, 'r+') as file:
    raw_data = np.array(file['raw_data'])


# initializing Avatar connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 12001)
client_address = ('127.0.0.1', 9001)
sock.bind(server_address)


while 1:
    for i in range(raw_data.shape[0]):
        time_start = time.time()
        
        avatar_buffer[finger_avatar] = raw_data[i, finger_pn]
        print(avatar_buffer)
        data = struct.pack('%df' % len(avatar_buffer), *list(map(float, avatar_buffer)))
        sock.sendto(data, client_address)
        
        t = 1/30 - (time.time() - time_start)
        if t > 0:
            time.sleep(t)
    