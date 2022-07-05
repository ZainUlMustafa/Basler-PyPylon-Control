'''
AWARE CAM CONTROL [ACCON]
This is a specially designed camera booter that runs and auto tries to run camera
and fetch the required info. It is crash-safe which enables it to revive again and
again.

ACCON uses settingDoc.json as strategy definer within which camera control properties can
be defined.
'''

import json
from operator import itemgetter
import os
import signal
import time
from pypylon import pylon
import cv2
import numpy as np
import base64

configDoc = './configs/config.json'
settingDoc = './configs/setting/accon.json'
statusDoc = './configs/status/accon.json'

showLogs = False
pid = None
counter = 0
prevSetting = None

def main():
    global pid; pid = os.getpid()

    if not os.path.exists(configDoc):
        updateStatus(-4)
        time.sleep(1)
        return
    #endif

    if not os.path.exists(settingDoc):
        updateStatus(-3)
        defaultSetting()
        updateStatus(5);
        time.sleep(1)
        return
    #endif

    camIds = ["22730681"]
    cams = []

    updateStatus(1)
    while len(cams) != len(camIds): 
        f = open(settingDoc)
        data = json.load(f)
        f.close()
        if data['kill']:
            updateStatus(999)
            os.kill(pid, signal.SIGTERM)
        #endif

        cams = fetchCameras(camIds)
        if len(cams) != len(camIds): 
            updateStatus(-1)
            time.sleep(1)
        else:
            updateStatus(2)
        #endif
        print(cams)
    #endwhile

    converter = bgrConv()
    cam = cams[0]
    # print(cam)
    cameraToPlay = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cam))
    cameraToPlay.Open()
    cameraToPlay.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    # print(f"{cam.GetSerialNumber()}: [Cameras opened]")
    updateStatus(3)

    grabbingCount = 0
    while cameraToPlay.IsGrabbing():
        try:
            if not os.path.exists(configDoc):
                updateStatus(-4)
                time.sleep(1)
                return
            #endif

            if not os.path.exists(settingDoc):
                updateStatus(-3)
                defaultSetting()
                updateStatus(5);
                time.sleep(1)
                return
            #endif

            f = open(settingDoc)
            data = json.load(f)
            f.close()
            
            camExposure, camGain, camLogs, camPid, camRetrievalTime, camShowImage, camKill = itemgetter('exposure', 'gain', 'showLogs', 'showPid', 'retrievalTime', 'showImage', 'kill')(data)
                
            if camPid:
                print(pid)
            #endif
                
            if camKill:
                updateStatus(999)
                os.kill(pid, signal.SIGTERM)
            #endif
                
            global showLogs; showLogs = camLogs
            buglog(data)

            # print(camExposure)
            cameraToPlay.ExposureTime.SetValue(camExposure)

            if (camGain <= 24.014275) and (camGain >= 0):
                cameraToPlay.Gain.SetValue(camGain)
            else:
                cameraToPlay.Gain.SetValue(0)
            #endif

            global prevSetting
            if prevSetting != data: updateStatus(6)
            prevSetting = data
            #endif
        except Exception as e:
            print(e)
            updateStatus(-2)
            defaultSetting()
            updateStatus(5)
            buglog("Defaulted. Maybe incorrect setting data?")
            return
        #endtry

        grabResult = cameraToPlay.RetrieveResult(camRetrievalTime, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            img = image.GetArray()

            if camShowImage:
                cv2.imshow('right', cv2.resize(img, (640*1,480*1)))

                if cv2.waitKey(1) & 0xff == ord('q'):
                    updateStatus(999)
                    os.kill(pid, signal.SIGTERM)
                    break
                #endif
            else:
                cv2.destroyAllWindows()
            #endif

            if grabbingCount == 0: updateStatus(7);
        #endif

        grabResult.Release()
        grabbingCount += 1
    #endwhile

    # Releasing the resource    
    cameraToPlay.StopGrabbing()
    cv2.destroyAllWindows()
#enddef

def imageWriter(img):
    ''''''
#enddef

def buglog(data):
    if showLogs:
        print(f'[CAM LOGS]: {data}')
    #endif
#enddef

def updateStatus(status):
    camStatuses = {
        999: "Ended",
        7: "First frame grabbed",
        6: "Setting applied",
        5: "Setting file created automatically",
        4: "Camera reviving",
        3: "Camera initiated",
        2: "Camera found",
        1: "Waiting for camera",
        0: "Script started",
        -1: "Camera not found",
        -2: "Camera exception",
        -3: "Setting not found",
        -4: "Config not found",
        -5: "Frame grabbing failed",
        -999: "Unexpected error"
    }

    statusData = {
        'status': status,
        'message': camStatuses[status],
    }

    with open(statusDoc, 'w', encoding='utf-8') as f:
        json.dump(statusData, f, ensure_ascii=False, indent=4)
    #endwith

    print(statusData)
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

def bgrConv():
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    return converter
#enddef

def convertToB64(img):
    _, imArr = cv2.imencode('.png', img)  # imArr: image in Numpy one-dim array format.
    imBytes = imArr.tobytes()
    imB64 = base64.b64encode(imBytes)
    return imB64.decode("utf-8")
#enddef

def currentServertime():
    return round(time.time() * 1000)
#enddef

def numberOfFiles(dir):
    list = os.listdir(dir)
    numberFiles = len(list)
    return numberFiles
#enddef

def defaultSetting():
    settingData = {
        "exposure": 10900,
        "gain": 0,
        "retrievalTime": 500,
        "showPid": False,
        "showLogs": False,
        "showImage": True,
        "saveImage": True,
        "kill": False
    }

    with open(settingDoc, 'w', encoding='utf-8') as f:
        json.dump(settingData, f, ensure_ascii=False, indent=4)
    #endwith
#enddef

if __name__ == "__main__":
    updateStatus(0)
    # defaultSetting()
    while True:
        try:
            cv2.destroyAllWindows()
            main()
        except Exception as e:
            print(e)
            if counter == 10: defaultSetting(); updateStatus(5)
            # print("Reviving...")
            updateStatus(4)
        #endtry

        counter += 1
    #endwhile
#endif

