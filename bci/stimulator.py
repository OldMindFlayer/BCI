# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 10:01:18 2020

@author: AlexVosk
"""

import time

import serial
import serial.tools.list_ports
from serial import SerialException




class Stimulator():
    def __init__(self, config):
        self.config = config
        # configuration of stimulation
        self.stimulation_enable = self.config['general'].getboolean('stimulation_enable')
        self.stimulation_idle = self.config['stimulation'].getboolean('stimulation_idle')
        
        # number and coordinates of potential matrix cells for stimulation
        self.cell_number = self.config['stimulation'].getint('cell_number')
        self.electrode_coords = list(map(int, self.config['stimulation']['electrode_coords'].split()))
        
        if self.cell_number < 2 or self.cell_number > 64:
            self._printm('cell_number should be a positive integer >= 2 and =< 64') 
            self._printm('setting cell_number = 2') 
            self.cell_number = 2
        
        if self.cell_number != len(self.electrode_coords):
            self._printm('number of cells and number of electrodes are different') 
            self._printm('creating electrode coordinates as list [1, 2, 3, ..., cell_number]')
            self.electrode_coords = [i for i in range(self.cell_number)]
        
        # init serial port variables
        self.comport = None
        self.ser = None
        self.stimuli_counter = 0
        self.connected = False
        
    
    # connect to the arduino
    def connect(self):
        # no connection if stimulation disabled or imaginary
        if not self.stimulation_enable:
            self._printm('stimulation disabled in config.ini -> general -> stimulation_enable')
            return
        if self.stimulation_idle:
            self._printm('stimulation is imaginary')
            return
        
        # choose comports based on config
        if self.config['stimulation'].getboolean('prefer_custom_comport'):
            # use custom comport
            custom_comport = self.config['stimulation']['custom_comport']
            comports = [custom_comport]
        else:
            # get list of all serial ports available and try to connect
            comports = [comport.device for comport in serial.tools.list_ports.comports()]
        
        # if no comports available - return
        if len(comports) == 0:
            self._printm('no comports available for connection')
            return
        
        # try to connect to the available compors
        while 1:
            for comport in comports:
                self.comport = self._connect(comport)
                if self.comport is not None:
                    break
            if self.comport is not None:
                break
            else:
                self._printm('all comports are alrady open, please close desired one, reconnection in 10 sec...')
                time.sleep(10)
        self.connected = True
            
    # close connection to arduino
    def close_connection(self):
        if not self.stimulation_enable:
            self._printm('stimulation disabled in config.ini -> general -> run_stimulation')
            return
        if self.stimulation_idle:
            self._printm('imaginary stimulation connection is closed')
            return
        if self.connected:
            self.ser.close()
            self._printm('connection to comport {} closed'.format(self.comport))
            self.ser = None
            self.connected = False
        else:
            self._printm('connection to comport is not established, can\'t close')
            
            
    # send command to arduino to configurate
    def configurate(self, stim_plus, stim_minus):
        self._push_command('configuration', (stim_plus, stim_minus))
        
    # send command to arduino to stimulate
    def stimulate(self, time, freq):
        self._push_command('stimulation', (time, freq))
    
        
        
    
        
    # used to estimate latency between pc and arduino
    def recieve_feedbeak(self):
        self.ser.read()
        return time.time()
    
    # getters    
    def get_comport(self):
        return self.comport
    def get_stimuli_counter(self):
        return self.stimuli_counter
    
    
    
    # helper funnction that is trying to connect to certain comport 
    def _connect(self, comport):
        baudrate = self.config['stimulation'].getint('baudrate')
        self._printm('establishing connection to comport {}...'.format(comport))
        try:
            self.ser = serial.Serial(port = comport,
                                     baudrate = baudrate,
                                     bytesize = serial.EIGHTBITS,
                                     parity = serial.PARITY_NONE, 
                                     stopbits = serial.STOPBITS_ONE)
        except SerialException:
            self._printm('comport {} is alrady open')
            return None
        # need to wait at least 1.5s before sending any data
        time.sleep(1.7)
        self._printm('connection to comport {} established'.format(comport))
        return comport
        
    
    def _push_command(self, ctype, data):
        command = Command(ctype, data)
        message = command.get_message()
        if not self.stimulation_enable:
            return
        if self.stimulation_idle:
            self._printm('imaginary {} {}'.format(ctype, command))
            return
        if not self.ser.is_open: 
            self._printm('can\'t stimulate, connection is closed')
            return
        self._send_data_to_comport(message)
        self._printm('{} {}'.format(ctype, command))
                
    def _send_data_to_comport(self, message):
        bytes_send = self.ser.write(message)
        if bytes_send != 3:
            self._printm('wrong number of bytes ({}) send'.format(bytes_send))
        self.stimuli_counter += 1
        if self.stimuli_counter % 100 == 0:
            self._printm('{} commands sent'.format(self.stimuli_counter))

    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)
    
    
    
class Command():
    def __init__(self, ctype, data):
        self.ctype = ctype
        self.data = data
        def bound(value, low, high):
            if value >= high: value = high
            elif value <= low: value = low
            return value
        if self.ctype=='configuration':
            stim_plus = bound(data[0], 0, 63)
            stim_minus = bound(data[1], 0, 63)
            self.message = bytes([254, stim_plus, stim_minus])
        elif self.ctype=='stimulation':
            pulse_time = bound(data[0], 10, 2500)
            fs = bound(data[1], 1, 100)
            self.message = bytes([255, pulse_time//10, fs])
        else:
            self.message = None
            self._printm('wrong ctype of command, it should be \'configuration\' or \'stimulation\'')
            
        
    def get_message(self):
        return self.message
        
    def __repr__(self):
        if self.ctype == 'configuration':
            return '(configuration, start={}, stop={})'.format(self.data[0], self.data[1])
        elif self.ctype == 'stimulation':
            return '(stimulation, time={}, fs={})'.format(self.data[0], self.data[1])
        
    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)
    
    
if __name__ == '__main__':
    pass
    
    
    
    
    
    
    
    