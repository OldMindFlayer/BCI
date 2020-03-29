# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:39:59 2020

@author: dblokv@gmail.com
"""

import configparser
from pathlib import Path


config = configparser.ConfigParser()

config['patient_info'] = {'patient_name': 'Test34',
      'patient_date': 'None',
      'patient_time': 'None'}

config['display'] = {'resting_time': '240',
      'pictures_action_time': '240',
      'pictures_object_time': '240',
      'single_picture_time': '4',
      'time_between_pictures': '0.5',
      'time_other_pictures': '2',
      'number_of_pictures_action': 'None',
      'number_of_pictures_object': 'None',
      'sound_between_pictures': 'false',
      'shuffle_pictures': 'true',
      'rotate_pictures':'true',      
      'WINDOW_X': '800',
      'WINDOW_Y': '1280'}

config['paths'] = {'root_path': 'None',
      'patient_data_path': 'None',
      'experiment_data_path': 'None',
      'results_path': 'None',
      'pictures_actions_path': 'None',
      'pictures_objects_path': 'None',
      'pictures_others_path': 'None',
      'tone_path': 'None',
      'lsl_stream_generator_path': 'None'}

config['general'] = {'debug_mode': 'false',
                     'remove_procedure': 'false',                     
                     'debug_time': '45',
                     'lsl_outlet_random': 'true',
                     'root_path_autogeneration': 'true',
                     'patient_date_time_autogeneration': 'true',
                     'fs': '2048',
                     'lsl_stream_name': 'EBNeuro_BePLusLTM_192.168.171.83'}

config['data_saving'] = {'save_through_buffer': 'true',
      'buffer_size_sec': '3',
      'group_names': 'data_rest data_actions data_objects',
      'dataset_width': '72',
      'save_picture_numbers': 'true'}

      
config['processing'] = {'grid_size_X': '4',
      'grid_size_Y': '8',
      'grid_channel_from': '1',
      'grid_channel_to': '32',
      'use_interval': 'false',
      'plot_grid_base': 'true',
      'interval_start': '0',
      'interval_stop': '1.5'}

      
config['channels'] = {'1': 'None',
      '2': 'None',
      '3': 'None',
      '4': 'None',
      '5': 'None',
      '6': 'None',
      '7': 'None',
      '8': 'None',
      '9': 'None',
      '10': 'None',
      '11': 'None',
      '12': 'None',
      '13': 'None',
      '14': 'None',
      '15': 'None',
      '16': 'None',
      '17': 'None',
      '18': 'None',
      '19': 'None',
      '20': 'None',
      '21': 'None',
      '22': 'None',
      '23': 'None',
      '24': 'None',
      '25': 'None',
      '26': 'None',
      '27': 'None',
      '28': 'None',
      '29': 'None',
      '30': 'None',
      '31': 'None',
      '32': 'None',
      '33': 'None',
      '34': 'None',
      '35': 'None',
      '36': 'None',
      '37': 'None',
      '38': 'None',
      '39': 'None',
      '40': 'None',
      '41': 'None',
      '42': 'None',
      '43': 'None',
      '44': 'None',
      '45': 'None',
      '46': 'None',
      '47': 'None',
      '48': 'None',
      '49': 'None',
      '50': 'None',
      '51': 'None',
      '52': 'None',
      '53': 'None',
      '54': 'None',
      '55': 'None',
      '56': 'None',
      '57': 'None',
      '58': 'None',
      '59': 'None',
      '60': 'None',
      '61': 'None',
      '62': 'None',
      '63': 'None',
      '64': 'None',
      '65': 'Sound',
      '66': 'None',
      '67': 'None',
      '68': 'None',
      '69': 'strange values',
      '70': 'timestap',
      '71': 'picture type',
      '72': 'picture start points'}


path = Path('write_config.py').resolve().parents[1]/'spmap'/'config.ini'
with open(path, 'w') as configfile:
    config.write(configfile)

    