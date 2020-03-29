# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:27:11 2020

@author: AlexVosk
"""
import h5py
import numpy as np



with h5py.File('C:/PNAvatarProject/PNAvatarData/25_03_20_Test34/14_31_39_experiment/experiment_data.h5', "r") as file:
    data = file['protocol1']['raw_data'][()]
    timestemp = file['protocol1']['timestamp_data'][()]
    print(data.shape)
    print(data[:, 200])
    print(np.sum(np.isnan(data[:, 200])))
    print(timestemp.shape)
    print(timestemp)

