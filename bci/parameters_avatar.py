# -*- coding: utf-8 -*-
"""
Created on Mon May  4 10:30:44 2020

@author: AlexVosk
"""


import winreg

var_names = {'CubeRotationAngle': 'CubeRotationAngle_h624454337',
             'CubeWidth': 'CubeWidth_h1024759154',
             'CubeXCoord': 'CubeXCoord_h3978394169',
             'CubeYCoord': 'CubeYCoord_h4015161880',
             'ExplosionAngle': 'ExplosionAngle_h1193650737',
             'MaxIndexAngleMale': 'MaxIndexAngleMale_h3863063659'}

def refresh_avatar_parameters():
    var_values = {}
    handle = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, 'Software\\Neuro\\VirtualArm')
    for key, name in var_names.items():
        var_values[key] = float(winreg.QueryValueEx(handle, name)[0].decode()[:-1])
    return var_values




if __name__ == '__main__':    
    refresh_avatar_parameters()