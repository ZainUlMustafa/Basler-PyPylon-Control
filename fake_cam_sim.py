import json
from operator import itemgetter
import os
import signal
import cv2
import numpy as np
import time

inputPath = ['./data/62d690207384085634ff9848/orig_json','./data/62d690207384085634ff9848/orig_low_res']
outputPath = ['./data/200/orig_json','./data/200/orig_low_res']
def main():
    if not os.path.exists(outputPath[0]):
        os.makedirs(outputPath[0])
    #endif
    if not os.path.exists(outputPath[1]):
        os.makedirs(outputPath[1])
    #endif
    numOfFiles = numberOfFiles(inputPath[0])
    for i in range(0, numOfFiles):
       inputImageJsonPath =  f'{inputPath[0]}/{i}.json'
       inputImageLowResPath =  f'{inputPath[1]}/{i}.jpg'
       f = open(inputImageJsonPath);inputImageJsonData = json.load(f); f.close()
       inputImageLowResData = cv2.imread(inputImageLowResPath)

       outputImageJsonPath =  f'{outputPath[0]}/{i}.json'
       outputImageLowResPath =  f'{outputPath[1]}/{i}.jpg'
       cv2.imwrite(outputImageLowResPath, inputImageLowResData)
       with open(outputImageJsonPath, 'w', encoding='utf-8') as f: json.dump(inputImageJsonData, f, ensure_ascii=False, indent=4);f.close()
       print(f'image{i} saved!')
       time.sleep(0.2)
    

def currentServertime() -> int:
    return round(time.time() * 1000)
#enddef

def numberOfFiles(dir: str) -> int:
    list = os.listdir(dir)
    numberFiles = len(list)
    return numberFiles
#enddef

if __name__ == '__main__':
    main()