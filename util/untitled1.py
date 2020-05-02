# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 08:08:12 2020

@author: AlexVosk
"""

string1 = ['LeftShoulder', 
      'LeftArm', 
      'LeftForeArm', 
      'LeftHand', 
      'LeftHandThumb1', 
      'LeftHandThumb2', 
      'LeftHandThumb3',
      'LeftInHandIndex', 
      'LeftHandIndex1', 
      'LeftHandIndex2', 
      'LeftHandIndex3', 
      'LeftInHandMiddle', 
      'LeftHandMiddle1', 
      'LeftHandMiddle2', 
      'LeftHandMiddle3', 
      'LeftInHandRing', 
      'LeftHandRing1', 
      'LeftHandRing2', 
      'LeftHandRing3',
      'LeftInHandPinky', 
      'LeftHandPinky1', 
      'LeftHandPinky2', 
      'LeftHandPinky3']

string2 = ['posX',
           'posY',
           'posZ',
           'rotY',
           'rotX',
           'rotZ']


s1 = '['
for i in range(354-216):
    string = '\'{} {}\','.format(
                                 string1[i//6],
                                 string2[i%6]) 
    s1 += string
    if i%3 == 2:
        s1 += '\n'
s1 += ']'
print(s1)

s = ''
for i in range(354-216):
    string = '{} = \'{} {}\''.format(i,
                                 string1[i//6],
                                 string2[i%6]) 
    s += string + '\n'
    print(s)
    
    