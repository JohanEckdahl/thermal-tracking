import numpy as np
import cv2
import time
from .tracker import *
from datetime import datetime


class Camera():
  
    def __init__(self, sources):
        self.thresh_px = 100
        self.erode_kernel = (5,5)
        self.open_kernel = (5,5)
        self.close_kernel = (5,5)
        self.min_contour_area = 2
        self.rec_fps = 30
        self.save_video = False
        self.stitch = False
        self.fps = 30
        self.image_size = (640,480)
        self.triggered = False
        self.names, urls = zip(*sources.items())
        self.caps = [cv2.VideoCapture(url) for url in urls]
            
    #--- GUI ---#
    
    def _create_trackbars(self, name): pass

    def _read_trackbars(self, name): pass

    def _create_window(self, name):
        cv2.namedWindow(name)
        self._create_trackbars(name)

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
        img = img[20:480, 0:640] #Ignore Axis Timestamp
        return cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]

    def _save_video(self, video_writer, frame): video_writer.write(frame)

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
    
    def _get_corrections(self, name): return 0, 0 #mtx, dist

    def _correct_distortion(self,img, mtx, dist):
        if mtx == 0: return img #if mtx, dist say no correction
        h, w = img.shape[:2]
        newmtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
        dst = cv2.undistort(img, mtx, dist, None, newmtx)
        x,y,w,h = roi
        img = dst[y:y+h, x:x+w]
        return img

    def _stitch(self, images): return img

    #--- Image Display ---#

    def _display(self, name, image):
        cv2.imshow(name, image)
        return image

    def _draw_track(self, img, coordinates, color):
        for xy in coordinates:
            img = cv2.circle(img, tuple(map(int,xy)), 1, color, -1)
        return cv2.polylines(img, np.int32([coordinates]), 0, color)


    def _mark_centroids(self, img, centroids):
        for X,Y in centroids:
            img = cv2.circle(img, (X, Y), 5, (100, 100, 255), -1)
            img = cv2.putText(img, "centroid", (X - 25, Y - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 2)
        return img


    #--- Public Method ---#
    def record(self, timeout=0):
        corrections = [self._get_corrections(name) for name in self.names]
        
        if self.stitch: self.names = ["combined"]
        if self.save_video:
            def path(i): return "./media/"+start+"_"+ str(i+1) +".avi"
            start = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            fourcc = cv2.VideoWriter_fourcc(*'XVID')            
            video_writers = [cv2.VideoWriter(path(i), fourcc,
                             self.fps, self.image_size)
                             for i, _ in enumerate(self.names)]

        for name in self.names: self._create_window(name)
 
        starttime = time.time()
        while True if timeout == 0 else time.time() < starttime + timeout:
            frames= [self._get_frame(cap) for cap in self.caps]
            c = [(a,*b) for a,b in zip(frames,corrections)]
            frames= [self._correct_distortion(*d) for d in c]
            if self.stitch: frames = [self._stitch(frames)]
            b = 0    
            for i, frame in enumerate(frames):
                if frame is not None:
                    self._read_trackbars(self.names[i])
                    img = self._process(frame)
                    self._display(self.names[i], img)
                    if self.save_video:
                        b += 1
                        self._save_video(video_writers[i], frame)
                else: break
            if b == 0: break
            if cv2.waitKey(1) & 0xFF == ord('q'): break
                
        if self.save_video:
            for writer in video_writers: writer.release()
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

    def _create_trackbars(self, name):
        def n(o): pass
        cv2.createTrackbar('Threshold', name, 0, 255, n)
        cv2.setTrackbarPos('Threshold', name, self.thresh_px)
        cv2.createTrackbar('Open', name, 0, 50, n)
        cv2.setTrackbarPos('Open', name, self.open_kernel[0])
        cv2.createTrackbar('Close', name, 0, 50, n)
        cv2.setTrackbarPos('Close', name, self.close_kernel[0])
        cv2.createTrackbar('Erode', name, 0, 50, n)
        cv2.setTrackbarPos('Erode', name, self.erode_kernel[0])

    def _read_trackbars(self, name):
        self.thresh_px = cv2.getTrackbarPos('Threshold', name)
        self.open_kernel = (cv2.getTrackbarPos('Open', name),)*2
        self.close_kernel = (cv2.getTrackbarPos('Close', name),)*2
        self.erode_kernel = (cv2.getTrackbarPos('Erode', name),)*2


    def _display(self, name, img):
        #img = self._mark_centroids(img, self.centroids)
        super()._display(name, img)
        return img

    def _save_video(self, video_writer, frame):
        if self.triggered and len(self.centroids): super()._save_video(video_writer, frame)
        else: pass
#______________________________________________________________________________#

class CentroidTracking(Centroid):
    db_path = "db.sqlite3"

    def _process(self, frame):
        img = super()._process(frame)
        self.tracker.update(self.centroids)
        return img

    def _display(self, name, img):
        for track in self.tracker.tracks:
            if track.is_real():
                white, red, gray = (255,255,255), (0,0,255), (100, 100, 255)
                img = self._draw_track(img, track.position,(white))
                img = self._draw_track(img, track.predicted_position,(red))
                predicted =  tuple(map(int,track.predict_position(1)))
                current   =  tuple(map(int,track.current_position()))
                img = cv2.circle(img, predicted, 3, (red), -1)
                img = cv2.circle(img, current, 3, gray, -1)
                img = cv2.putText(img, str(track.id), current,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        Camera._display(self, name, img)
        return img

    def record(self, timeout=0):
        self.tracker = Tracker(self.db_path)
        super().record(timeout)
        del self.tracker

