#!/usr/bin/env python3

import sys
sys.path.append('.')
from includes.camera import CentroidTracking as camera


url  = 'http://root:pass@192.168.0.90/mjpg/video.mjpg'
url = './media/lawn.mov'



a = camera(url)
a.erode_kernel = (2,2)
a.open_kernel = (2,2)
a.close_kernel = (2,2)
a.thresh_px = 200
a.centroid_markers = False
a.min_contour_area = 2
a.record()
