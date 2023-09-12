import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class DataProcessor():
    def __init__(self,maximum_noise_level: int) -> None:
        self.maximum_noise_level = maximum_noise_level
    
    def process_data(self,df: pd.DataFrame):
        diffs = pd.DataFrame()
        diffs['Power_Diff'] = df['Power'].diff()
        diffs['Minute'] = df['Minute']
        # leave only elements above 5 in the diffs dataframe
        diffs = diffs[abs(diffs['Power_Diff']) > self.maximum_noise_level]

        # Connect Posible On/Off moments for Same power devices
        df_connections = pd.DataFrame

        

        # Plot the diff dataframe if needed
        # plt.scatter(diffs['Minute'],diffs['Power_Diff'])
        # plt.plot(df['Minute'],df['Power'])
        # plt.show()