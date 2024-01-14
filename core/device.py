import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Device():
    def __init__(self,power:int, name: str | None = None) -> None:
        self.name = name if name is not None else "Unknown"
        # Create table with the analytics for each minute of the day
        # Each row of the dataframe will have the sum of the points at that minute for that feature (starting time, etc...)
        self.analytics = np.zeros((3,1440))
        self.num_points = 0
        self.weight_sum = 0
        self.power = power

    def add_point(self,weight, on_time , off_time) -> None:
        self.analytics[0,on_time] += weight
        self.analytics[1,off_time] += weight
        self.analytics[2,off_time-on_time] += weight
        self.num_points += 1
        self.weight_sum += weight
    
    def get_as_dataframe(self):
        return pd.DataFrame(self.analytics.T,columns=["On_time","Off_time","Operating_time"])
    
    @property
    def on_time_analytics(self):
        return self.analytics[0]
    
    @property
    def off_time_analytics(self):
        return self.analytics[1]
    
    @property
    def operating_time_analytics(self):
        return self.analytics[2]