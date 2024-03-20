import cv2 
import depthai as dai

#create a pipeline
pipeline = dai.Pipeline()

#define the source and output
camRgb = pipeline.create(dai.node.ColorCamera)
xoutVideo = pipeline.create(dai.node.XLinkOut)

xoutVideo.setStreamName("video")

#properties

camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setVideoSize(1280, 720)

xoutVideo.input.setBlocking(False)
xoutVideo.input.setQueueSize(1)

#Linking
camRgb.video.link(xoutVideo.input)

with dai.Device(pipeline, usb2Mode=True) as device:

    video = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    count = 0
    while True:
        videoIn = video.get()
        cvFrame = videoIn.getCvFrame()
        cv2.imshow('vid', cvFrame)
        
        if cv2.waitKey(1) == ord('p'):
            cv2.imwrite('picture'+str(count)+'.jpg', cvFrame)
            count = count + 1
        if cv2.waitKey(1) == ord('q'):
            break