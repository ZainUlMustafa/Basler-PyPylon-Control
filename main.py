from pypylon import pylon
import cv2
import numpy as np

def main():
    camIds = ["22730681"]
    cams = fetchCameras(camIds)

    if len(cams) == 0: print("No cameras found!"); return
    
    # cameras = []
    # for cam in cams:
    #     camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cam))
    #     cameras.append(camera)
    #     print(f"{cam.GetSerialNumber()}: [Cameras opened]")
    # #endfor

    converter = bgrConv()

    cam = cams[0]
    print(cam)
    cameraToPlay = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cam))
    cameraToPlay.Open()
    cameraToPlay.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    print(f"{cam.GetSerialNumber()}: [Cameras opened]")

    while cameraToPlay.IsGrabbing():
        grabResult = cameraToPlay.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            img = image.GetArray()

            cv2.imshow('right', cv2.resize(img, (640*1,480*1)))

            if cv2.waitKey(1) & 0xff == ord('q'):
                break
            #endif
        #endif

        grabResult.Release()
    #endwhile

    # Releasing the resource    
    cameraToPlay.StopGrabbing()
    cv2.destroyAllWindows()
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

if __name__ == "__main__":
    cv2.destroyAllWindows()
    main()
#endif

