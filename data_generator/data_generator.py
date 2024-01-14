import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd


devices = pd.read_csv("data_generator/data/devices.csv")


def generate_data(**kwargs):
    random_on_off_times = pd.DataFrame()
    random_on_off_times["Power"] = devices["Power"]
    # Generate random on and off times for each device
    random_on_off_times["ON"] = devices.apply(lambda row: np.random.normal(row['Usual_On_time'], row['On_variance']), axis=1).round().astype(int)
    random_on_off_times["OFF"] = devices.apply(lambda row: np.random.normal(row['Usual_Off_time'], row['Off_variance']), axis=1).round().astype(int)
    # Calulate the power at each minute
    power_over_time = np.zeros(1440)
    p_forget = 0.2
    for i,(power,on_time,off_time) in random_on_off_times.iterrows():
        # Ignore the device a certain percentage of the time
        if random.random() < p_forget:
            continue
        power_over_time[on_time:off_time] += power
    # Transform to dataframe
    power_dataframe = pd.DataFrame(power_over_time, columns=["Power"])
    power_dataframe["Minute"] = power_dataframe.index
    return power_dataframe