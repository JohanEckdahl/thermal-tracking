import numpy as np
import pandas as pd
from datetime import datetime


class Track():
    def __init__(self, id, position):
        self.id = id
        self.position = self.__reshape2by1(position)
        print("Track {} created".format(self.id))
        df = {'start_time' : [datetime.now().strftime('%Y-%m-%d %H:%M:%S')], 'end_time' : [""] }
        self.dataframe = pd.DataFrame.from_dict(df)
    
    def __reshape2by1(self, position):
        return np.reshape(position, (1, 2))
        
    def current_position(self):
        return self.position[-1]
    
    def append_position(self, position):
        self.position = np.append(self.position, self.__reshape2by1(position), axis=0)
        
    def get_data(self): return self.dataframe
    
    def __del__(self):
        self.dataframe['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')   
        print("Track {} deleted".format(self.id))
