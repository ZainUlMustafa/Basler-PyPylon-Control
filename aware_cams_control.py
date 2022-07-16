'''
AWARE CAM CONTROL [ACCON]
This is a specially designed camera booter that runs and auto tries to run camera
and fetch the required info. It is crash-safe which enables it to revive again and
again.

ACCON uses settingDoc.json as strategy definer within which camera control properties can
be defined.
'''

import hashlib
import json
from operator import itemgetter
import os
import shutil
import signal
import time
from pypylon import pylon
import cv2
import numpy as np
import base64
import multiprocessing

configDoc = './configs/config.json'
settingDoc = './configs/setting/accon.json'
statusDoc = './configs/status/accon.json'

showLogs = False
pid = None
counter = 0
prevSetting = None
configData = None

def main():
    global pid; pid = os.getpid()

    if not os.path.exists(configDoc):
        updateStatus(-4)
        time.sleep(1)
        return
    #endif

    global configData
    f = open(configDoc)
    configData = json.load(f)
    f.close()

    if not os.path.exists(settingDoc):
        updateStatus(-3)
        defaultSetting()
        updateStatus(5);
        time.sleep(1)
        return
    #endif

    camIds = ["22730681", "22730679"]
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
    cameraToPlayOne = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cams[0]))
    cameraToPlayOne.Open()
    cameraToPlayOne.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    cameraToPlayTwo = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cams[1]))
    cameraToPlayTwo.Open()
    cameraToPlayTwo.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    # print(f"{cam.GetSerialNumber()}: [Cameras opened]")
    updateStatus(3)

    dataCollection = f"./data/{configData['proid']}/orig_png"
    dataCollectionJson = f"./data/{configData['proid']}/orig_json"
    if not os.path.exists(dataCollection):
        os.makedirs(dataCollection)
    #endif
    if not os.path.exists(dataCollectionJson):
        os.makedirs(dataCollectionJson)
    #endif

    grabbingCount = numberOfFiles(dataCollectionJson)
    while cameraToPlayOne.IsGrabbing() and cameraToPlayTwo.IsGrabbing():
        startTime = time.time()
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
            
            camExposure, camGain, camLogs, camPid, camRetrievalTime, camShowImage, camSaveImage, camSaveImagesFromScratch, camFps, camKill = itemgetter('exposure', 'gain', 'showLogs', 'showPid', 'retrievalTime', 'showImage','saveImage', 'saveImagesFromScratch','fps', 'kill')(data)
            
            cameraToPlayOne.AcquisitionFrameRate.SetValue(camFps)
            cameraToPlayOne.ExposureTime.SetValue(camExposure)
            cameraToPlayTwo.AcquisitionFrameRate.SetValue(camFps)
            cameraToPlayTwo.ExposureTime.SetValue(camExposure)
            if (camGain <= 24.014275) and (camGain >= 0):
                cameraToPlayOne.Gain.SetValue(camGain)
                cameraToPlayTwo.Gain.SetValue(camGain)
            else:
                cameraToPlayOne.Gain.SetValue(0)
                cameraToPlayTwo.Gain.SetValue(0)
            #endif

            if camPid:
                print(pid)
            #endif
                
            if camKill:
                updateStatus(999)
                os.kill(pid, signal.SIGTERM)
            #endif
                
            global showLogs; showLogs = camLogs
            buglog(data)

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

        grabResultOne = cameraToPlayOne.RetrieveResult(camRetrievalTime, pylon.TimeoutHandling_ThrowException)
        grabResultTwo = cameraToPlayTwo.RetrieveResult(camRetrievalTime, pylon.TimeoutHandling_ThrowException)
        if grabResultOne.GrabSucceeded():
            imageOne = converter.Convert(grabResultOne)
            imgOne = imageOne.GetArray()

            imageTwo = converter.Convert(grabResultTwo)
            imgTwo = imageTwo.GetArray()

            # if camSaveImage:
            #     multiprocessing.Process(target=imageWriter, args=(imgOne, imgTwo, grabbingCount,dataCollection, dataCollectionJson,)).start()
            #     # imageWriter(img, grabbingCount,dataCollection, dataCollectionJson);
            # #enddef

            if camShowImage:
                cv2.imshow('one', cv2.resize(imgOne, (640*1,480*1)))
                cv2.imshow('two', cv2.resize(imgTwo, (640*1,480*1)))

                if cv2.waitKey(1) & 0xff == ord('q'):
                    updateStatus(999)
                    os.kill(pid, signal.SIGTERM)
                    break
                #endif
            else:
                cv2.destroyAllWindows()
            #endif

            if grabbingCount == 0: updateStatus(7);
            grabbingCount += 1
        #endif

        grabResultOne.Release()
        grabResultTwo.Release()
        endTime = time.time()
        print(f"Total time taken this loop: {(endTime - startTime)*1000} ms")
    #endwhile

    # Releasing the resource    
    cameraToPlayOne.StopGrabbing()
    cameraToPlayTwo.StopGrabbing()
    cv2.destroyAllWindows()
#enddef

def imageWriter(imgOne, imgTwo, grabbingCount,dataCollection,dataCollectionJson):
    totalImages = grabbingCount

    imageB64 = convertToB64(imgOne)
    resizedB64 = convertToB64(cv2.resize(imgOne, (200*1,150*1)))
    imageBoxHtml = f"<!DOCTYPE html><html><img src='data:image/png;base64,{resizedB64}' width='50%' alt='{configData['proid']} image'/></html>"
    imageObject = {
        "_id": totalImages,
        "servertime": f'{currentServertime()}',
        "isCorrect": True,
        "data": [
            {
                "pair": "single",
                "base64": imageB64, #f"{dataCollection}/single_{totalImages}.png",
            },
        ],
        "imageBoxHtml": imageBoxHtml,
        "proid": configData['proid']
    }

    md5Hash = hashlib.md5(json.dumps(imageObject).encode('utf-8')).hexdigest()
    imageObject['_hash'] = md5Hash

    with open(f"{dataCollectionJson}/{totalImages}.json", 'w', encoding='utf-8') as f:
        json.dump(imageObject, f, ensure_ascii=False, indent=4)
        f.close()
    #endwith

    # multiprocessing.Process(target=saveImage, args=(img, f"{dataCollection}/{totalImages}.png",)).start()
    # cv2.imwrite(f"{dataCollection}/{totalImages}.png", img)
    # print(f"Image {totalImages} written")
#enddef

def saveImage(img, path):
    cv2.imwrite(path, img)
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
    return imB64.decode("ascii")
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
        "retrievalTime": 5000,
        "showPid": False,
        "showLogs": False,
        "showImage": True,
        "saveImage": True,
        "saveImagesFromScratch": False,
        "fps": 1,
        "kill": False
    }

    with open(settingDoc, 'w', encoding='utf-8') as f:
        json.dump(settingData, f, ensure_ascii=False, indent=4)
    #endwith
#enddef

if __name__ == "__main__":
    updateStatus(0)
    defaultSetting()
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

