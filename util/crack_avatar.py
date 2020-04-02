

import numpy as np
import time
import struct
import socket
import pylsl

#initializing Avatar connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 12001)
client_address = ('127.0.0.1', 9001)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

mode = 1


if mode == 1:
    n = 96
    for i in range(96):
        avatarBuffer = np.zeros(n) #[0 for _ in range(96)]
        print('\nchannel {}'.format(i))
        for j in range(100):
            avatarBuffer[i] = - 50 + j/2
            
            #sending to the Avatar
            data = struct.pack('%df' % len(avatarBuffer), *list(map(float, avatarBuffer)))
    
            sock.sendto(data, client_address)
            time.sleep(0.033)
    print(data)
    print(len(data))

    
    
    
    
    
    
    
    