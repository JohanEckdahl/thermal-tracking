import numpy as np
import cv2
from .tracker import *

class Camera():
        
    def __init__(self, url, source = ""):
        self.cap = cv2.VideoCapture(url)
        self.thresh_px = 100
        self.erode_kernel = (5,5)
        self.open_kernel = (5,5)
        self.close_kernel = (5,5)
        self.min_contour_area = 2000
        self.rec_fps = 30


    #--- Image Processing ---#

    def _get_frame(self):
        ret, frame = self.cap.read()
        return frame

    def _process(self, frame): return frame

    def _grayscale(self, img): return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def _threshold(self, img):
        retval, img = cv2.threshold(img, self.thresh_px, 255,cv2.THRESH_BINARY)
        return img

    def _erode(self, img):
        kernel = np.ones(self.erode_kernel, np.uint8)
        return cv2.erode(img, kernel, iterations = 1)

    def _opening(self,img):
        kernel = np.ones(self.open_kernel, np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    def _closing(self, img):
        kernel = np.ones(self.close_kernel, np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    def _find_contours(self, img):
        return cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]

    #--- Image Display ---#

    def _display(self,img): cv2.imshow('hi',img)
   
    def _draw_track(self, img, coordinates):
        for xy in coordinates:
            img = cv2.circle(img, tuple(map(int,xy)), 2, (100, 100, 255), -1)
        return cv2.polylines(img, np.int32([coordinates]), 0, (180,180,180))

    def _find_centroids(self, img, min_area):
        contours = self._find_contours(img)
        centroidsXY = np.empty((0,2),int)
        for c in contours:
            if cv2.contourArea(c) > min_area:
               # calculate moments for each contour
                M = cv2.moments(c)
                # calculate x,y coordinate of center
                try: cX, cY= int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                except: pass
                centroidsXY = np.append(centroidsXY, [[cX, cY]], axis=0)
        return centroidsXY
  
    def _mark_centroids(self, img, centroidsXY):
        for X,Y in centroidsXY:
            img = cv2.circle(img, (X, Y), 5, (100, 100, 255), -1)
            img = cv2.putText(img, "centroid", (X - 25, Y - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 2)
        return img


    #--- Public Method ---#

    def record(self):
        while self.cap.isOpened():
            frame = self._get_frame()
            if frame is not None:
                self._process(frame)
                self._display(frame)
                if cv2.waitKey(self.rec_fps) & 0xFF == ord('q'): break
            else: break
        self.cap.release()
        cv2.destroyAllWindows()
#______________________________________________________________________________#

class Centroid(Camera):
    def _process(self, img):
        img = gray = self._grayscale(img)
        img = self._threshold(img)
        img = self._erode(img)
        img = self._opening(img)
        img = self._closing(img)
        self.centroidsXY = self._find_centroids(img, self.min_contour_area)

    def _display(self, img):
        img = self._mark_centroids(img, self.centroidsXY)
        super()._display(img)
#______________________________________________________________________________#

class CentroidTracking(Centroid):
    db_path = "db.sqlite3"

    def _process(self, frame):
        super()._process(frame)
        self.tracker.update(self.centroidsXY)

    def _display(self, img):
        for track_object in self.tracker.tracks:
            if True: #track_object.is_real():
                img = self._draw_track(img, track_object.position)
                predicted =  tuple(map(int,track_object.predict_position(1)))
                current   =  tuple(map(int,track_object.current_position()))
                img = cv2.circle(img, predicted, 5, (250, 250, 255), -1)
                img = cv2.circle(img, current, 3, (100, 100, 255), -1)
                img = cv2.putText(img, str(track_object.id), current,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 2)
        Camera._display(self, img)

    def record(self):
        self.tracker = Tracker(self.db_path)
        super().record()
        del self.tracker

