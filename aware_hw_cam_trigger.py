import hashlib
from operator import itemgetter
import os
import signal
import Jetson.GPIO as GPIO
import time

from itsdangerous import json 

production = False

configPath = "../Configurations"
dataPath = "../Data"

configDoc = configPath if production else '.' + '/configs/config.json'
settingDoc = configPath if production else '.' + '/configs/setting/ahcat.json'
statusDoc = configPath if production else '.' + '/configs/status/ahcat.json'

showLogs = True
pid = None
counter = 0
prevSetting = None
configData = None

print("AHCAT - AWARE HW CAM TRIGGER")

def main():
    # read config
    configData = readConfig()
    if not doesConfigContainsValidInfo(configData):
        updateStatus(-1)
        time.sleep(1)
        return
    #endif

    # read setting
    settingData = readSetting()
    camPinNumber, camShowLogs, camFps, camKill, camForceHalt = itemgetter('pinNumber', 'showLogs','fps', 'kill', 'forceHalt')(settingData)
    if camKill: updateStatus(999); killMe()
    if camForceHalt: updateStatus(3); time.sleep(1); return

    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(camPinNumber, GPIO.OUT, initial=GPIO.HIGH)

    # run capture loop until break condition
    updateStatus(1)
    while (camKill == False) or (camForceHalt == False):
        startTime = time.time()
        global showLogs; showLogs = camShowLogs;

        if camForceHalt: updateStatus(3); return

        if camFps == 0: defaultSetting(force=True); updateStatus(7); return
        timeOn = (1/camFps)*0.9
        timeOff = (1/camFps)-timeOn

        time.sleep(timeOn) 
        GPIO.output(camPinNumber, GPIO.HIGH) 
        buglog("LED is ON")
        time.sleep(timeOff) 
        GPIO.output(camPinNumber, GPIO.LOW)
        buglog("LED is OFF")

        settingData = readSetting()
        camShowLogs, camPinNumber, camFps, camKill, camForceHalt = itemgetter('showLogs','pinNumber', 'fps','kill', 'forceHalt')(settingData)
        if camKill: updateStatus(999); killMe()
        configData = readConfig()
        if not doesConfigContainsValidInfo(configData): return;
        endTime = time.time()
        print(f"Total time taken this loop: {(endTime - startTime)*1000} ms")
    #endwhile
#enddef

def readConfig() -> dict:
    if not os.path.exists(configDoc): return None;
    f = open(configDoc)
    data = json.load(f)
    f.close()
    return data;
#enddef

def readStatus() -> dict:
    if not os.path.exists(statusDoc): return None;
    f = open(statusDoc)
    data = json.load(f)
    f.close()
    return data;
#enddef

def readSetting() -> dict:
    if not os.path.exists(settingDoc): return None;
    f = open(settingDoc)
    data = json.load(f)
    f.close()
    return data;
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

def updateStatus(status: int):
    allStatuses = {
        999: "Ended",
        6: "Frequency cannot be zero. Settings defaulted!",
        5: "Reviving...",
        4: "Setting defaulted",
        3: "Halting",
        2: "Setting applied",
        1: "Trigger started",
        0: "Script started",
        -1: "Config not valid",
        -2: "Config not found",
        -998: "Unexpected error but reviving...",
        -999: "Unexpected error"
    }

    prevStatusData = "{}"
    try:
        prevStatusData = readStatus()
    except:
        prevStatusData = "{}"
    #endtry
    
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

    buglog(statusData)
#enddef

def currentServertime() -> int:
    return round(time.time() * 1000)
#enddef

def killMe() -> bool:
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)
#enddef

def defaultSetting(force=False):
    existingSettingData = None
    if not force:
        try:
            existingSettingData = readSetting()
            if existingSettingData['kill'] == True: existingSettingData = None
        except:
            existingSettingData = None
        #endif
    #endif

    if existingSettingData is None:
        settingData = {
            "fps": 1,
            "kill": False,
            "forceHalt": False,
            "showLogs": True,
            "pinNumber": 7
        }

        with open(settingDoc, 'w', encoding='utf-8') as f:
            json.dump(settingData, f, ensure_ascii=False, indent=4)
        #endwith

        updateStatus(4)
    #endif
#enddef

def buglog(data):
    if showLogs:
        print(f'[CAM TRIG LOGS]: {data}')
    #endif
#enddef

if __name__ == "__main__":
    defaultSetting()
    updateStatus(0)
    count = 0
    while True:
        try:
            main()
        except KeyboardInterrupt:
            updateStatus(5)
            time.sleep(1)
        except Exception as e:
            print(e)
            if count >= 5: 
                defaultSetting()
                updateStatus(4)
            else:
                updateStatus(-998)
            #endif
            time.sleep(1)
        #endtry

        count += 1
    #endwhile
#endif