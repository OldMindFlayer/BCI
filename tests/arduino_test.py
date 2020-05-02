# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 08:31:52 2020

@author: AlexVosk
"""
import time
import math
import configparser
import serial
import serial.tools.list_ports
from serial import SerialException

# connect to comport
def connect(comport, baudrate):
    while 1:
        try:
            ser = serial.Serial(port = comport,
                                baudrate = baudrate,
                                bytesize = serial.EIGHTBITS,
                                parity = serial.PARITY_NONE, 
                                stopbits = serial.STOPBITS_ONE)
            break
        except SerialException:
            print('comport {} is alrady open, please close it, reconnection in 10 sec...'.format(comport))
            time.sleep(10)
    time.sleep(1.7) # need to wait at least 1.5s before sending any data
    print('connection to comport {} established'.format(comport))
    return ser
    
# close connection to comport, used in finally
def close_connection(ser):
    if ser is not None:
        ser.close()
        print('connection to comport closed')
    else:
        print('connection to comport is not established, can\'t close')
    
    
def configurate(stim_plus, stim_minus):
    message = bytes([254, stim_plus, stim_minus])
    send_data_to_comport(message)

def stimulate(stim_time, stim_fs):
    message = bytes([255, stim_time//10, stim_fs])
    send_data_to_comport(message)

    
def send_data_to_comport(message):
    bytes_send = ser.write(message)
    if bytes_send != 3:
        print('wrong number of bytes ({}) send'.format(bytes_send)) 

def recieve_feedbeak(ser):
    ser.read()
    return time.time()
                    



def test(config, stim_plus, stim_minus, number_stimuli, overall_time):
    try:
        comport = config['arduino']['comport']
        baudrate = config['arduino'].getint('baudrate')
        # connect to arduino
        ser = None
        ser = connect(comport, baudrate)
        # choose stimulation cells of matrix
        configurate(stim_plus, stim_minus)
        # stimulate in cycle
        sleep = 100
        s = overall_time*1000 - sleep*number_stimuli
        stim_time = (math.sqrt(1 + 8*s) - 1)//2
        for i in range(number_stimuli):
            stimulate(stim_time*i, 1)
            time.sleep(sleep/1000)
            print('stimulation length {}'.format(stim_time*i))
    finally:
        close_connection(ser)
    



if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('arduino_config.ini')
    comport = config['arduino']['comport']
    baudrate = config['arduino'].getint('baudrate')
    
    # from cell 0 to cell 1, 50 stimuli in 10 sec 
    test(config, 0, 1, 50, 10)
    