
import matplotlib

import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd


devices = pd.read_csv("data-generator/data/devices.csv")
print(devices)

num_days = 10
day_rnd_times = pd.DataFrame()
day_rnd_times["Power"] = devices["Power"]
for i in range(num_days):
    day_rnd_times["ON"] = devices.apply(lambda row: np.random.normal(row['Usual_On_time'], row['On_variance']), axis=1).round()
    day_rnd_times["OFF"] = devices.apply(lambda row: np.random.normal(row['Usual_Off_time'], row['Off_variance']), axis=1).round()
    print(day_rnd_times)
    current_power = 0
    days_power_series = []
    for j in range(1440):
        current_power += day_rnd_times[day_rnd_times["ON"] == j]["Power"].sum()
        current_power -= day_rnd_times[day_rnd_times["OFF"] == j]["Power"].sum()
        days_power_series.append(current_power)
    # plt.plot(days_power_series)
    # plt.show()
    temp_df = pd.DataFrame(days_power_series)
    temp_df["Minute"] = temp_df.index
    temp_df.to_csv(f"data-generator/data/example_day{i}.csv",header=['Power','Minute'],index=False)