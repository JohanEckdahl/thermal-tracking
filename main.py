#!/usr/bin/env python3

import time
import settings
from includes.camera import Centroid as camera

sources = {"webcam"   : 0,
	   #"webcam2"  : 0,
	   #"camera1" : 'http://root:pass@192.168.0.90/mjpg/video.mjpg',
	   #"camera2" : 'http://root:pass@192.168.0.90/mjpg/video.mjpg',
	   #"bird8"   : settings.project_path + '/media/bird8.mp4',
	   #"bird1"   : settings.project_path + '/media/bird1.mp4',
	  }

a = camera(sources)
a.erode_kernel      =  (1,1)
a.open_kernel       =  (1,1)
a.close_kernel      =  (1,1)
a.thresh_px         =  200
a.min_contour_area  =   1
a.fps               =  30
a.save_video        =  True
a.stitch	    =  True
a.image_size        =  (640,480)
a.record(timeout=0)



'''
time.sleep(23400)

for i in range(24):
    a = camera(url)
    a.erode_kernel      =   (2,2)
    a.open_kernel       =   (2,2)
    a.close_kernel      =   (2,2)
    a.thresh_px         =  230
    a.min_contour_area  =   1
    a.rec_fps           =  1
    a.save_video        =  True
    a.record(timeout=300)
    del a
    time.sleep(600)
'''


'''
videos = [8,]
for x in videos:
    url = settings.project_path + '/media/bird{}.mp4'.format(x)
    a = camera(url)
    a.erode_kernel      =   (1,1)
    a.open_kernel       =   (1,1)
    a.close_kernel      =   (1,1)
    a.thresh_px         =  200
    a.min_contour_area  =   1
    a.rec_fps           =   33
    a.save_video        =   True    
    a.record()
    del a
'''   



