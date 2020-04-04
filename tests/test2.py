# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:27:11 2020

@author: AlexVosk
"""
import h5py
import numpy as np



with h5py.File('C:/MyoDecodeProject/MyoDecodeData/20_04_04_120538_Test34/experiment_data.h5', "r") as file:
    data = file['protocol1']['raw_data'][()]
    timestemp = file['protocol1']['timestamp_data'][()]
    print(data.shape)
    print(data[:, 130])
    print(np.sum(np.isnan(data[:, 130])))
    print(timestemp.shape)
    print(timestemp)

