import numpy as np
import pandas as pd
from datetime import datetime


class Track():

    def __init__(self, id, position, frame):
        self.id, self.lost, self.frames = id, 0, [frame]
        self.position = self.__reshape2by1(position)
        self.predicted_position = self.__reshape2by1(position)
        df = {'start_time'     :  [datetime.now().strftime('%Y-%m-%d %H:%M:%S')], 
              'end_time'       :  [""],
              'avg_angle'      :  [0.0],
              'std_angle'      :  [0.0],
              'frame_count'    :  1,
        }
        self.dataframe = pd.DataFrame.from_dict(df)

    def __del__(self):
        if self.is_real():        
            print(self.dataframe)
            print("Track {} deleted".format(self.id))
        else: pass
        print(len(self.position), len(self.predicted_position))

    def __avg_angle(self, frame_count):
        if self.__frame_count() < 2 or frame_count < 2: return 0
        azimuth = []
        b = self.position[::-1][:frame_count]
        for i in range(len(b)-1):
            array = b[i]-b[i+1]
            azimuth.append(np.degrees(np.arctan2(array[1], array[0])))
        mean = np.mean(np.array(azimuth))
        return mean


    def __avg_speed(self, frame_count):
        if self.__frame_count() < 2 or frame_count < 2: return 0
        b = self.position[::-1][:frame_count]
        c = self.frames[::-1][:frame_count]
        speeds = []
        for i in range(len(b)-1):
            array  = b[i]-b[i+1]
            array2 = c[i]-c[i+1]
            distance = np.linalg.norm(array)
            speed = distance/(array2)
            speeds.append(speed)
        mean = np.mean(np.array(speeds))
        return mean


    def __frame_count(self): return len(self.position)
    
    def __reshape2by1(self, position): return np.reshape(position, (1, 2))

    def get_data(self): return self.dataframe
       
    def is_real(self): return self.__frame_count() > 15

    def current_position(self): return self.position[-1]

    def predict_position(self, frame_count):
        # arg is frames away from last seen
        angle = self.__avg_angle(2)
        speed = self.__avg_speed(2)
        distance = frame_count*speed
        angle = np.radians(angle)
        x = distance * np.cos(angle)
        y = distance * np.sin(angle)
        return self.current_position() + [x,y]

    def append_position(self, position,frame):
        self.frames.append(frame)
        self.dataframe['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.position = np.append(self.position, self.__reshape2by1(position), axis=0)
        self.predicted_position = np.append(self.predicted_position, self.__reshape2by1(self.predict_position(self.lost+1)), axis=0)
        self.dataframe['avg_angle'] = self.__avg_angle(self.__frame_count())
        self.dataframe['frame_count'] = self.__frame_count()
        self.lost = 0
        

    

