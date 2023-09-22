
import matplotlib

import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd


devices = pd.read_csv("data_generator/data/devices.csv")


def generate_data(**kwargs):
    day_rnd_times = pd.DataFrame()
    day_rnd_times["Power"] = devices["Power"]
    day_rnd_times["ON"] = devices.apply(lambda row: np.random.normal(row['Usual_On_time'], row['On_variance']), axis=1).round().astype(int)
    day_rnd_times["OFF"] = devices.apply(lambda row: np.random.normal(row['Usual_Off_time'], row['Off_variance']), axis=1).round().astype(int)
    all_minutes = pd.DataFrame(np.zeros(1440), columns=["Power"])
    p_forget = 0.2
    for i in range(len(day_rnd_times)):
        # Ignore the device a certain percentage of the time
        if random.random() < p_forget:
            continue

        on_time = day_rnd_times.iloc[i]["ON"]
        off_time = day_rnd_times.iloc[i]["OFF"]
        all_minutes.iloc[on_time:off_time] += day_rnd_times.iloc[i]["Power"]

    all_minutes["Minute"] = all_minutes.index
    return all_minutes