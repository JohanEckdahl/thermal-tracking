import numpy as np
import cv2
from .tracker import *

class Camera():
            
    thresh_px = 100
    erode_kernel = (5,5)
    open_kernel = (5,5)
    close_kernel = (5,5)
    min_contour_area = 2000

    def __init__(self, url, source = ""):
	    self.cap = cv2.VideoCapture(url)

    def _get_frame(self):
        ret, frame = self.cap.read()
        return frame

    def _grayscale(self, img):
	    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

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
        im2, contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def _draw_track(self, img, coordinates, track_id):
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
    
    def _mark_centroids(self, img):
        centroidsXY = self._find_centroids(img, self.min_contour_area)
        for X,Y in centroidsXY:
            cv2.circle(img, (X, Y), 5, (100, 100, 255), -1)
            cv2.putText(img, "centroid", (X - 25, Y - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 2)
        return img
    
    def _process(self, frame): return frame
    
    def record(self):
        while self.cap.isOpened():
            if frame is not None:
                frame = self.get_frame()
                img = self.process(frame)
                cv2.imshow('hi',img)
                if cv2.waitKey(50) & 0xFF == ord('q'):
                    break
                else: break
            self.cap.release()
            cv2.destroyAllWindows()


class Centroid(Camera):
    centroid_markers = True
    def _process(self, img):
        img = gray = self._grayscale(img)
        img = self._threshold(img)
        img = self._erode(img)
        img = self._opening(img)
        img = self._closing(img)
        if self.centroid_markers == True:
            img = self._mark_centroids(img)
        return img


class CentroidTracking(Centroid):
    db_path = "../db.sqlite3"
    def record(self):
        tracker = Tracker(self.db_path)
        
        while self.cap.isOpened():
            frame = self._get_frame()
            if frame is not None:
                img = self._process(frame)

                centroids = self._find_centroids(img, self.min_contour_area)
                tracker.update(centroids)
                #img = frame
                for track_id, track_object in tracker.tracks.items():
                    img = self._draw_track(img,track_object.position, track_object.id)


                cv2.imshow('hi',img)
                if cv2.waitKey(50) & 0xFF == ord('q'):
                    break
            else: break    
        self.cap.release()
        cv2.destroyAllWindows()
        del tracker

