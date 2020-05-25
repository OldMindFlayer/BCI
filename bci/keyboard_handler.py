# -*- coding: utf-8 -*-
"""
Created on Sun May 17 12:02:36 2020

@author: AlexVosk
"""


from pynput.keyboard import Listener, Key
from queue import Queue
import time

# handle pressing buttons
def keyboard_on_press(q, key):
    # handle escape button
    if key == Key.esc:
        q.put(('realtime_close', True))
    
    # handle other buttons
    else:
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
        if k == 't':
            q.put(('avatar_data_type', True))
        

def keyboard_on_release(q):
    pass










if __name__ == '__main__':
    queue_keyboard = Queue()
    on_press = lambda key: keyboard_on_press(queue_keyboard, key)
    listener = Listener(on_press=on_press, on_release=keyboard_on_release)
    listener.start()
    
    key = 'p'
    for i in range(10):
        print(key)
        while not queue_keyboard.empty():
            print('buy')
            k, v = queue_keyboard.get()
            print(k)
            print(k == 'realtime_close')
            if k == 'realtime_close':
                break
        time.sleep(0.5)
    listener.stop()

    
    
    
    
    
    
    