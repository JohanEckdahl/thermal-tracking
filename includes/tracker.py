import numpy as np
from collections import OrderedDict
from .database import *
from .track import *

class Tracker():
    
    def __init__(self,db_path):
        self.i = 1
        self.tracks = OrderedDict()
        self.db = SQLiteDB(db_path)
        print("Tracker online, let's do this!")
        
    def __del__(self):
        for track_id, track_object in self.tracks.items():
            del track_object
        print("Tracker is off, night night.")
        del self.db

    def create_track(self, position):
        self.tracks[self.i] = Track(self.i, position)
        self.i += 1
        
    def save_delete_track(self, track):
        dataframe = track.get_data()
        self.db.insert('track', dataframe)
        del self.tracks[track.id]
        
    def update(self, centroidsXY):
        for track_id, track_object in self.tracks.items():
            if len(centroidsXY) > 0:
                distances = np.empty((0),int)
                for row in centroidsXY:
                    d = np.linalg.norm(row-track_object.current_position())
                    distances = np.append(distances, d)
                index = np.argmin(distances)
                track_object.append_position(centroidsXY[index])
                centroidsXY = np.delete(centroidsXY, index, 0)
                #print("Track {} Position: {}".format(track_id, track_object.current_position()))
            else: self.save_delete_track(track_object)
                
        for row in centroidsXY:
            self.create_track(row)
