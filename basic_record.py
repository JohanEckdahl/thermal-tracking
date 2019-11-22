#!/usr/bin/env python3

import time
import settings
from includes.camera import Camera as camera

sources = {"camera1" : 'http://root:pass@192.168.0.90/mjpg/video.mjpg',
          }

a = camera(sources)
a.record_fps        = 33
a.fps               =  30
a.save_video        =  True
a.record(timeout=0)

