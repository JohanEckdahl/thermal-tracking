#!/usr/bin/env python3

import time
import settings
from includes.camera import CentroidTracking as camera


#url  = 'http://root:pass@192.168.0.90/mjpg/video.mjpg'
#url = settings.project_path + '/media/2018-11-07_07:13:51.avi'
url = settings.project_path + '/media/bird1.mp4'

a = camera(url)
a.erode_kernel      =   (4,4)
a.open_kernel       =   (4,4)
a.close_kernel      =   (4,4)
a.thresh_px         =  200
a.min_contour_area  =   5
a.rec_fps           =  33
a.save_video        =  False
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



