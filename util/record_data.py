# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 17:59:02 2020

@author: AlexVosk
"""

import sys
import time
import copy
import socket
import struct


import h5py
import numpy as np

from config import config_init
from pnhandler import PNHandler
from experiment_record import ExperimentRecord

channels = np.asarray([243, 269, 293, 317, 341]) - 216 + 1
#finger_coord = np.asarray([1,2,3,4])

filepath = 'C:/MyoDecodeProject/MyoDecodeData/20_04_23_232334_Test34/experiment_data.h5'
name = 'finger_index.h5'

with h5py.File(filepath, 'r+') as file:
    raw_data = np.array(file['protocol1/raw_data'])[:, channels]
    timestamp_data = np.array(file['protocol1/timestamp_data'])

frame = np.zeros(len(channels))
data30fps = []
start_timestamp = timestamp_data[0]
i_start = 0
for i, timestamp in enumerate(timestamp_data):
    time_pass = timestamp - start_timestamp
    if time_pass > 1/30:
        data_slice = raw_data[i_start:i,:]
        medians = np.nanmedian(data_slice, axis=0)
        frame[~np.isnan(medians)] = medians[~np.isnan(medians)]
        new_frame = copy.deepcopy(frame)
        data30fps.append(new_frame)
        start_timestamp = timestamp
        i_start = i
        

stacked_data = np.vstack(data30fps)
print(stacked_data.shape)
with h5py.File(name, 'w') as file:
    file.create_dataset('raw_data', dtype='float64', data=stacked_data)  

    
