import numpy as np
from .database import *
from .track import *

class Tracker():
    '''This is the tracker class'''
    
    def __init__(self,db_path):
        self.i, self.tracks, self.db = 1, [], SQLiteDB(db_path) 
        self.frame = 1
        print("Tracker online, let's do this!")
        
    def __del__(self):
        for track in self.tracks:
            if track.is_real(): self.save_track(track)
            del track
        print("Tracker is off, night night.")
        del self.db

    def _calculate_distance(self, row, track):
        x = row
        y = track.predict_position(track.lost + 1)
        z=x-y
        d = np.linalg.norm(z)            
        return d

    def _calculate_angle(self, row, track):
        a = np.degrees(np.arctan2(row[1], row[0]))
        angle = abs(float(track.dataframe['avg_angle']) - a)
        return angle


    def create_track(self, position):
        track = Track(self.i, position, self.frame)
        self.tracks.append(track)
        self.i += 1
        
    def save_track(self, track):
        dataframe = track.get_data()
        self.db.insert('track', dataframe)


    def update(self, centroidsXY):
        '''The core function \m/(-_-)\m/'''
        h = 0
        for track in self.tracks:
            if len(centroidsXY) > 0:
                distances = np.empty((0),int)
                for row in centroidsXY:
                    distance = self._calculate_distance(row, track)
                    angle = self._calculate_angle(row, track)
                    if distance < 50: # and angle < 40:
                        distances = np.append(distances, distance)
                    else: distances = np.append(distances, np.Inf)
                index = np.argmin(distances)
                if distances[index] != np.Inf:                
                    track.append_position(centroidsXY[index], self.frame)
                    centroidsXY = np.delete(centroidsXY, index, 0)
                else: track.lost += 1
            else:
                #print("Shit, track {} dissapaeared!".format(track.id))
                track.lost += 1
            if track.lost > 30:
                if track.is_real(): self.save_track(track)
                del self.tracks[h]
            h +=1
        
        
        for row in centroidsXY:
            if len(row) > 0 : self.create_track(row)
        
        self.frame +=1



'''

def update(self, centroidsXY):
        h = 0
        for track in self.tracks: 
            if len(centroidsXY) > 0:
                distances = np.empty((0),int)
                for row in centroidsXY:
                    d = np.linalg.norm(row-track.predict_position(track.lost + 1))
                    d = np.linalg.norm(row-track.current_position())
                    distances = np.append(distances, d)
                index = np.argmin(distances)
                if distances[index] < 60:
                    track.append_position(centroidsXY[index])
                    track.frames.append(self.frame)
                    centroidsXY = np.delete(centroidsXY, index, 0)
                else: track.lost += 1
            else:
                #print("Shit, track {} dissapaeared!".format(track.id))
                track.lost += 1
            if track.lost > 30:
                if track.is_real(): self.save_track(track)
                del self.tracks[h]
            h +=1
        
        self.frame +=1
        for row in centroidsXY:
            if len(row) > 0 : self.create_track(row)   

    def update(self, centroidsXY):
        indices = [i for i in range(len(self.tracks))]
        for row in centroidsXY:
            if not any(indices): self.create_track(row)
            else:
                distances = np.empty((0),int)
                for i in indices:
                    if i:
                        track = self.tracks[i]                
                        d = np.linalg.norm(row-track.current_position())
                        distances = np.append(distances, d)
                        
                    else: distances = np.append(distances, np.Inf)
                index = np.argmin(distances)
                self.tracks[index].append_position(row)
                self.tracks[index].frames.append(self.frame)
                indices[index] = False
        for i in indices:
            if i:
                track = self.tracks[i] 
                #track.append_position(track.predict_position(track.lost))
                track.lost += 1
                if track.lost > 30:
                    del self.tracks[i]        
        self.frame +=1
'''


