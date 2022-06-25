from pypylon import pylon
import cv2
import numpy as np

cams= []
for i in pylon.TlFactory.GetInstance().EnumerateDevices():
    cams.append(i)
#endfor

for cam in cams:
    print(cam.GetSerialNumber())
#endfor
