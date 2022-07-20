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
import numpy as np
import base64
import multiprocessing

import cv2

production = False

configPath = "/Configurations"
dataPath = "/Data"

configDoc = configPath if production else '.' + '/configs/config.json'
settingDoc = configPath if production else '.' + '/configs/setting/accon.json'
statusDoc = configPath if production else '.' + '/configs/status/accon.json'

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

    if not doesConfigContainsValidInfo(configData):
        updateStatus(-6)
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
    f = open(settingDoc)
    data = json.load(f)
    f.close()
    if data['kill']:
        updateStatus(999)
        os.kill(pid, signal.SIGTERM)
    #endif

    if data['forceHalt']: time.sleep(1); return;

    cams = fetchCameras(camIds)
    if len(cams) != len(camIds): 
        updateStatus(-1)
        time.sleep(1)
        return
    #endif
    updateStatus(2)
    print(cams)

    converter = bgrConv()
    cam = cams[0]
    # print(cam)
    cameraToPlay = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cam))
    cameraToPlay.Open()
    cameraToPlay.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    # print(f"{cam.GetSerialNumber()}: [Cameras opened]")
    updateStatus(3)

    dataCollection = dataPath if production else '.' + f"/data/{configData['proid']}/orig_low_res"
    dataCollectionJson = dataPath if production else '.' + f"/data/{configData['proid']}/orig_json"
    metaDoc = dataPath if production else '.' + f"/data/{configData['proid']}/meta.txt"

    if not os.path.exists(dataCollection):
        os.makedirs(dataCollection)
    #endif
    if not os.path.exists(dataCollectionJson):
        os.makedirs(dataCollectionJson)
    #endif

    grabbingCount = numberOfFiles(dataCollectionJson)
    while cameraToPlay.IsGrabbing():
        startTime = time.time()

        f = open(configDoc)
        configData = json.load(f)
        f.close()
        if not doesConfigContainsValidInfo(configData):
            time.sleep(1)
            return
        #endif

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
            
            camExposure, camGain, camLogs, camPid, camRetrievalTime, camShowImage, camSaveImage, camSaveImagesFromScratch, camFps, camKill, camForceHalt = itemgetter('exposure', 'gain', 'showLogs', 'showPid', 'retrievalTime', 'showImage','saveImage', 'saveImagesFromScratch','fps', 'kill', 'forceHalt')(data)
            
            if camForceHalt: time.sleep(1); return;

            cameraToPlay.AcquisitionFrameRate.SetValue(camFps)
            cameraToPlay.ExposureTime.SetValue(camExposure)
            if (camGain <= 24.014275) and (camGain >= 0):
                cameraToPlay.Gain.SetValue(camGain)
            else:
                cameraToPlay.Gain.SetValue(0)
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

        grabResult = cameraToPlay.RetrieveResult(camRetrievalTime, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            img = image.GetArray()
            timeOfGrab = currentServertime();

            if grabbingCount%camFps == 0: writeMeta(grabbingCount, metaDoc);

            if camSaveImage:
                multiprocessing.Process(target=imageWriter, args=(img, grabbingCount,dataCollection, dataCollectionJson,timeOfGrab,)).start()
                # imageWriter(img, grabbingCou"appended text"nt,dataCollection, dataCollectionJson);
            #enddef

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
            grabbingCount += 1
        #endif

        grabResult.Release()
        endTime = time.time()
        print(f"Total time taken this loop: {(endTime - startTime)*1000} ms")
    #endwhile

    # Releasing the resource    
    cameraToPlay.StopGrabbing()
    cv2.destroyAllWindows()
#enddef

def imageWriter(img, grabbingCount,dataCollection,dataCollectionJson, timeOfGrab):
    totalImages = grabbingCount

    resizedImg = cv2.resize(img, (200*2,150*2))
    rotatedResizedImg = cv2.rotate(resizedImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    imageB64 = convertToB64(img)
    lowResB64 = convertToB64(resizedImg, '.jpg')
    # lowResRotB64 = convertToB64(rotatedResizedImg, '.jpg')
    
    imageBoxHtml = f"<!DOCTYPE html><html><img src='data:image/jpg;base64,{lowResB64}' width='100%' alt='{configData['proid']} image'/></html>"
    imageObject = {
        "_id": totalImages,
        "servertime": f'{timeOfGrab}',
        "isCorrect": True,
        "data": [
            {
                "pair": "single",
                "base64": imageB64, #original image
                "lowResImage": f"{dataCollection}/{totalImages}.png" # path to low res image
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
    cv2.imwrite(f"{dataCollection}/{totalImages}.jpg", rotatedResizedImg)
    # print(f"Image {totalImages} written")
#enddef

def saveImage(img, path):
    cv2.imwrite(path, img)
#enddef

def writeMeta(count: int, path: str) -> bool:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(str(count))
        f.close()
    #endwith
#enddef

def buglog(data):
    if showLogs:
        print(f'[CAM LOGS]: {data}')
    #endif
#enddef

def doesConfigContainsValidInfo(data):
    validOperations = ["1"]
    if "proid" in data and "operationStatus" in data:
        if len(data['proid']) != 0 and data['operationStatus'] in validOperations:
            # print(data)
            return True
        #endif
    #endif

    # print(data)
    return False
#enddef

def readStatus() -> dict:
    if not os.path.exists(statusDoc): return None;
    f = open(statusDoc)
    data = json.load(f)
    f.close()
    return data;
#enddef

def updateStatus(status):
    allStatuses = {
        999: "Ended",
        8: "Image file saved",
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
        -6: "Config not valid",
        -999: "Unexpected error"
    }

    prevStatusData = readStatus()
    prevMd5Hash = hashlib.md5(json.dumps(prevStatusData).encode('utf-8')).hexdigest()

    statusData = {
        'status': status,
        'message': allStatuses[status],
    }

    md5Hash = hashlib.md5(json.dumps(statusData).encode('utf-8')).hexdigest()

    # print(prevMd5Hash != md5Hash)
    if prevMd5Hash != md5Hash:
        with open(statusDoc, 'w', encoding='utf-8') as f:
            json.dump(statusData, f, ensure_ascii=False, indent=4)
        #endwith
    #endif

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

def convertToB64(img, ext='.png'):
    _, imArr = cv2.imencode(ext, img)  # imArr: image in Numpy one-dim array format.
    imBytes = imArr.tobytes()
    imB64 = base64.b64encode(imBytes)
    return imB64.decode("ascii")
#enddef

def currentServertime() -> int:
    return round(time.time() * 1000)
#enddef

def numberOfFiles(dir: str) -> int:
    list = os.listdir(dir)
    numberFiles = len(list)
    return numberFiles
#enddef

def defaultSetting():
    settingData = {
        "exposure": 100000,
        "gain": 0,
        "retrievalTime": 5000,
        "showPid": False,
        "showLogs": False,
        "showImage": False,
        "saveImage": True,
        "saveImagesFromScratch": False,
        "fps": 1,
        "kill": False,
        "forceHalt": False,
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
        except KeyboardInterrupt:
            updateStatus(4)
        #endtry

        counter += 1
    #endwhile
#endif

