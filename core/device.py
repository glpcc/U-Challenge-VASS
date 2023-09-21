import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Device():
    def __init__(self,power:int, name: str | None = None) -> None:
        self.name = name if name is not None else "Unknown"
        # Create table with the analytics for each minute of the day
        # Each row of the dataframe will have the sum of the points at that minute for that feature (starting time, etc...)
        self.analytics = pd.DataFrame(np.zeros((1440,3)),columns=["On_time","Off_time","Operating_time"])
        self.num_points = 0
        self.weight_sum = 0
        self.power = power

    def add_point(self,weight, data: pd.Series) -> None:
        self.analytics.loc[data["On"], "On_time"] += weight
        self.analytics.loc[data["Off"], "Off_time"] += weight
        self.analytics.loc[data["Off"]-data["On"], "Operating_time"] += weight
        self.num_points += 1
        self.weight_sum += weight