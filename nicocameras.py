# THIS CODE GOT COPIED FROM ANDY REPO AND MODIFIED
# DO NOT GRADE, I DID NOT PRODUCE THIS CODE

import threading
import time
import cv2

class NicoCameras:

    def __init__(self):
        self.ids = [0,3]
        self.frames = {}
        self.fpss = {}
        for id in self.ids:
            self.frames[id] = None
            self.fpss[id] = 0
        print('starting camera threads')
        self.threads = []
        for i in range(len(self.ids)):
            thread = threading.Thread(name="camera"+str(i), target=self.grabbing, args=(self.ids[i],))
            thread.start()
            self.threads.append(thread)
        self.stopped = False

    def grabbing(self,id):
        print(f'grabbing thread {id} started')
        camera = cv2.VideoCapture(id,cv2.CAP_DSHOW)
        fps = 30 
        camera.set(cv2.CAP_PROP_FPS,fps)
        fps = 0
        t0 = time.time()
        while True:
            hasFrame, self.frames[id] = camera.read()
            if not hasFrame or self.stopped:
                break
            t1 = time.time()
            if int(t1) != int(t0):
                self.fpss[id] = fps
                fps = 0
                t0 = t1
            fps += 1
            cv2.waitKey(1)

    def read(self):
        return ( self.frames[id] for id in self.ids )

    def fps(self):
        return ( self.fpss[id] for id in self.ids )
        
    def close(self):
        self.stopped = True
        