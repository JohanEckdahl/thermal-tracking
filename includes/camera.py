import numpy as np
import cv2
from .tracker import *
from datetime import datetime
import time

class Camera():
        
    def __init__(self, urls):
        self.caps = [cv2.VideoCapture(url) for url in urls]
        self.thresh_px = 100
        self.erode_kernel = (5,5)
        self.open_kernel = (5,5)
        self.close_kernel = (5,5)
        self.min_contour_area = 2000
        self.rec_fps = 30
        self.save_video = False
        self.fps = 30
        self.image_size = (640,480)


    #--- Image Processing ---#

    def _get_frame(self, cap): return cap.read()[1]

    def _process(self, frame): return frame

    def _grayscale(self, img): return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def _threshold(self, img):
        return cv2.threshold(img, self.thresh_px, 255,cv2.THRESH_BINARY)[1]


    def _erode(self, img):
        kernel = np.ones(self.erode_kernel, np.uint8)
        return cv2.erode(img, kernel, iterations = 1)

    def _opening(self, img):
        kernel = np.ones(self.open_kernel, np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    def _closing(self, img):
        kernel = np.ones(self.close_kernel, np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    def _find_contours(self, img):
        return cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]

    #--- Image Display ---#

    def _display(self, name, image):
        cv2.imshow(name, image)
        return image

    def _draw_track(self, img, coordinates, color):
        for xy in coordinates:
            img = cv2.circle(img, tuple(map(int,xy)), 1, color, -1)
        return cv2.polylines(img, np.int32([coordinates]), 0, color)

    def _find_centroids(self, img):
        contours = self._find_contours(img)
        centroids = np.empty((0,2),int)
        for c in contours:
            if cv2.contourArea(c) > self.min_contour_area:
                M = cv2.moments(c)
                try: X, Y= int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                except: pass
                centroids = np.append(centroids, [[X, Y]], axis=0)
        return centroids
  
    def _mark_centroids(self, img, centroids):
        for X,Y in centroids:
            img = cv2.circle(img, (X, Y), 5, (100, 100, 255), -1)
            img = cv2.putText(img, "centroid", (X - 25, Y - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 2)
        return img


    #--- Public Method ---#
    def record(self, timeout=0):
        if self.save_video:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            start = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            video_writers = []
            i=1
            for cap in self.caps:
                video_writers += [cv2.VideoWriter("./media/"+start+"_" + str(i) +".avi", fourcc,
                                            self.fps, self.image_size)]
                i+=1
        
        def condition(start, timeout): 
            if timeout == 0: return True
            else: return time.time() < start + timeout
   
        timeout_start = time.time()
        while self.caps[0].isOpened() and condition(timeout_start, timeout):
            i = 0            
            for cap in self.caps:
                frame = self._get_frame(cap)
                if frame is not None:
                    frame = frame[0:480, 0:640] 
                    img = self._process(frame)
                    self._display('camera{}'.format(i), frame)
                    if self.save_video: video_writers[i].write(frame)
                else: print("Frame not here"); break
                i+=1
            if cv2.waitKey(self.rec_fps) & 0xFF == ord('q'): break
                
        if self.save_video:
            for video_writer in video_writers: video_writer.release()
        for cap in self.caps: cap.release()
        cv2.destroyAllWindows()
#______________________________________________________________________________#

class Centroid(Camera):
    def _process(self, img):
        img = self._grayscale(img)
        img = self._threshold(img)
        img = self._erode(img)
        img = self._opening(img)
        img = self._closing(img)
        self.centroids = self._find_centroids(img)
        return img

    def _display(self, name, img):
        img = self._mark_centroids(img, self.centroids)
        super()._display('Centroids', img)
        return img
#______________________________________________________________________________#

class CentroidTracking(Centroid):
    db_path = "db.sqlite3"

    def _process(self, frame):
        img = super()._process(frame)
        self.tracker.update(self.centroids)
        return img

    def _display(self, name, img):
        for track_object in self.tracker.tracks:
            if True:#track_object.is_real():
                white, red, gray = (255,255,255), (0,0,255), (100, 100, 255)
                img = self._draw_track(img, track_object.position,(white))
                img = self._draw_track(img, track_object.predicted_position,(red))
                predicted =  tuple(map(int,track_object.predict_position(1)))
                current   =  tuple(map(int,track_object.current_position()))
                img = cv2.circle(img, predicted, 3, (red), -1)
                img = cv2.circle(img, current, 3, gray, -1)
                img = cv2.putText(img, str(track_object.id), current,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        Camera._display(self, name, img)
        return img

    def record(self, timeout=0):
        self.tracker = Tracker(self.db_path)
        super().record(timeout)
        del self.tracker

