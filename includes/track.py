import numpy as np
import pandas as pd
from datetime import datetime


class Track():

    def __init__(self, id, position):
        self.id = id
        self.position = self.__reshape2by1(position)
        df = {'start_time'     :  [datetime.now().strftime('%Y-%m-%d %H:%M:%S')], 
              'end_time'       :  [""],
              'avg_angle'      :  [0.0],
              'std_angle'      :  [0.0],
              'frame_count'    :  1,
        }
        self.dataframe = pd.DataFrame.from_dict(df)
        self.lost = 0
        self.frames=[]

        print("Track {} created".format(self.id))

    def __del__(self):
        if self.is_real:        
            print(self.dataframe)
            print("Track {} deleted".format(self.id))
        else: pass

    def __avg_angle(self, frame_count):
        azimuth = np.empty(1)
        try:
            for point in self.positions[:frame_count]:
                a = np.degrees(np.arctan2(point[1], point[0]))
                azimuth = np.append(azimuth, a)
                mean = (np.mean(azimuth))
                return mean
        except: return 0

    def __avg_speed(self, frame_count):
        try: 
            distance = np.linalg.norm(self.position[0] - self.position[frame_count])
            return distance/(self.frames[0] - self.frames[frame_count])
        except: return 0

    def __frame_count(self): return len(self.position)
    
    def __reshape2by1(self, position):
        return np.reshape(position, (1, 2))

    def get_data(self): return self.dataframe
                
        
    def is_real(self):
        if self.__frame_count() > 15: return True
        else: return False


    def current_position(self):
        return self.position[-1]

    def predict_position(self, frame_count):
        angle = self.__avg_angle(30)
        speed = self.__avg_speed(30)
        distance = frame_count*speed
        angle = np.radians(angle)
        x = distance * np.cos(angle)
        y = distance * np.sin(angle)
        return self.current_position() + [x,y]


    def append_position(self, position):
        self.dataframe['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.position = np.append(self.position, self.__reshape2by1(position), axis=0)
        self.dataframe['avg_angle'] = self.__avg_angle(self.position)
        self.dataframe['frame_count'] = self.__frame_count()
        self.lost = 0
        

    

