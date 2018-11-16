import numpy as np
from .database import *
from .track import *

class Tracker():
    '''This is the tracker class'''
    
    def __init__(self,db_path):
        self._i, self.frame, self.tracks, self.db = 1, 1, [], SQLiteDB(db_path)
        self.max_distance=45
        print("Tracker online, let's do this!")
        
    def __del__(self):
        for track in self.tracks:
            if track.is_real(): self.save_track(track)
            del track
        del self.db
        print("Tracker is off, night night.")
        

    def _calculate_distance(self, row, track):
        x, y = row, track.predict_position(track.lost + 1)
        return np.linalg.norm(x-y)

    def _calculate_angle(self, row, track):
        a = np.degrees(np.arctan2(row[1], row[0]))
        angle = abs(float(track.dataframe['avg_angle']) - a)
        return angle


    def create_track(self, position):
        self.tracks.append(Track(self._i, position, self.frame))
        self._i += 1
        
    def save_track(self, track): self.db.insert('track', track.get_data())


    def update(self, centroids):
        '''The core function \m/(-_-)\m/'''
        h = 0
        for track in self.tracks:
            if len(centroids) > 0:
                distances = np.empty((0),dtype=np.float32)
                for centroid in centroids:
                    distance = self._calculate_distance(centroid, track)
                    angle = self._calculate_angle(centroid, track)
                    if distance < self.max_distance: # and angle < 40:
                        distances = np.append(distances, distance)
                    else: distances = np.append(distances, np.Inf)
                index = np.argmin(distances)
                if distances[index] != np.Inf:                
                    track.append_position(centroids[index], self.frame)
                    centroids = np.delete(centroids, index, 0)
                else: track.lost += 1
            else: track.lost += 1

            if track.lost > 30:
                if track.is_real(): self.save_track(track)
                del self.tracks[h]
            h +=1
        
        for row in centroids:
            if len(row) > 0 : self.create_track(row)
        
        self.frame +=1
