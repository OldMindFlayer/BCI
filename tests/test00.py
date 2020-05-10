# -*- coding: utf-8 -*-
"""
Created on Thu May  7 09:50:32 2020

@author: AlexVosk
"""

import time
import pynput

class Control():
    def __init__(self):
        self.key = False
        listener = pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        print(listener.isDaemon())
        listener.daemon = True
        listener.start()
        
        while 1:
            print(self.key)
            time.sleep(1)


    def on_press(self, key):
        if key.char == 't':
            self.key = not self.key

    def on_release(self, key):
        pass
    
    
if __name__ == '__main__':
    Control()