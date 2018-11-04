import numpy as np
from .database import *
from .track import *

class Tracker():
    '''This is the tracker class'''
    frame = 1
    
    def __init__(self,db_path):
        self.i, self.tracks, self.db = 1, [], SQLiteDB(db_path) 
        print("Tracker online, let's do this!")
        
    def __del__(self):
        for track in self.tracks:
            if track.is_real(): self.save_track(track)
            del track
        print("Tracker is off, night night.")
        del self.db

    def create_track(self, position):
        self.tracks.append(Track(self.i, position))
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
                if track.is_real(): save_track(track)
                del self.tracks[h]
            h +=1
        
        self.frame +=1
        for row in centroidsXY:
            if len(row) > 0 : self.create_track(row)


'''
    def update(self, centroidsXY):
        h = 0
        j = 0
        for row in centroidsXY:
            distances = np.empty((0),int)
            for track in self.tracks:
                d = np.linalg.norm(row-track.current_position())
                distances = np.append(distances, d)
                track.frames.append(self.frame)
            index = np.argmin(distances)
            track[index].append_position(row)
            centroidsXY = np.delete(centroidsXY, j, 0)
            j+=1
                
        for track in self.tracks: 
            if len(centroidsXY) > 0:
                distances = np.empty((0),int)
                for row in centroidsXY:
                    d = np.linalg.norm(row-track.current_position())
                    distances = np.append(distances, d)
                index = np.argmin(distances)
                track.append_position(centroidsXY[index])
                track.frames.append(self.frame)
                centroidsXY = np.delete(centroidsXY, index, 0)
            else:
                print("Shit, track {} dissapaeared!".format(track.id))
                print(track.predict_position(track.lost))
                track.append_position(track.predict_position(track.lost))
                track.lost += 1
            if track.lost > 30:
                del self.tracks[h]
            h +=1
        
        self.frame +=1
        for row in centroidsXY:
            if len(row) > 0 : self.create_track(row)
'''


