#!/usr/bin/env python3

import settings
from includes.camera import CentroidTracking as camera

#url  = 'http://root:pass@192.168.0.90/mjpg/video.mjpg'
url = settings.project_path + '/media/lawn.mov'


a = camera(url)

a.erode_kernel      =   (2,2)
a.open_kernel       =   (2,2)
a.close_kernel      =   (2,2)
a.thresh_px         =   200
a.min_contour_area  =   2
a.rec_fps           =  33

a.record()
