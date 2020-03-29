# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 23:08:54 2020

@author: AlexVosk
"""
import h5py
import numpy as np

def rec_traverse(k):
    if isinstance(k, h5py.Dataset):
        print(k)
    else:
        for key in k.keys():
            print(key)
            rec_traverse(k[key])

np.random.seed(0)
data = np.random.randint(0, 100, 50).reshape((5, 10))
print(data)

aux_data = np.random.randint(0, 100, 15).reshape((3, 5))
print(aux_data)

aux_data_nan = np.zeros((5, 5)) * np.nan
aux_data_nan2 = np.zeros((5, 5)) * np.nan
print(aux_data_nan)


timestamp = np.array([1, 2, 3, 4, 5])
aux_timestamp = np.array([0.5, 3.5, 4.5]) +1


print(np.searchsorted(timestamp[:-1], aux_timestamp))
for k in range(aux_data.shape[1]):
    aux_data_nan[np.searchsorted(timestamp[:-1], aux_timestamp), k] = aux_data[:, k]
    
print(aux_data_nan)



aux_data_nan2[np.searchsorted(timestamp[:-1], aux_timestamp), :] = aux_data
print(aux_data_nan2)




#with h5py.File('experiment_data.h5', "r") as file:
    #k = ['channels', 'fs', 'protocol0', 'protocol1']
    #print(list(file['protocol0']['signals_stats']['Signal'].keys()))
    #rec_traverse(file['protocol1'])
    #data = file['protocol1']['raw_data'][()]
    #print(data.shape)
    #print(data[:, 200])
    #print(np.sum(np.isnan(data[:, 200])))