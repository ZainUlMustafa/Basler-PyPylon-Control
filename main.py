from pypylon import pylon
import cv2
import numpy as np

def main():
    camIds = ["22730681"]
    cams = fetchCameras(camIds)
    print(cams)
#enddef

def fetchCameras(camIds):
    cams = []
    for camId in camIds:
        for cam in pylon.TlFactory.GetInstance().EnumerateDevices():
            if cam.GetSerialNumber() == camId:
                cams.append(cam)
            #endif
        #endfor
    #endfor

    return cams
#enddef

if __name__ == "__main__":
    cv2.destroyAllWindows()
    main()
#endif

