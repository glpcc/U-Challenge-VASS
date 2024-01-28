import pandas as pd
import numpy as np
from core.data_loader import DataLoader
from core.data_processor import DataProcessor
from core.device import Device
from core.knowledge_base import KnowledgeBase
from core.recomendation_engine import RecomendationEngine
from matplotlib import pyplot as plt
import random

# Generate the classes instances
data_load = DataLoader()
data_processor = DataProcessor(maximum_noise_level=2,max_power_spike_variance=5)
kb = KnowledgeBase()

# list_devices = data_load.load_devices_data("data/")
# kb.set_devices_by_list(list_devices)
# kb.plot_device_analytics()
# Seed the random generator and numpy random generator
random.seed(0)
np.random.seed(0)

days = 200
#Create a plot with the power data of the 20 first days
fig, axs = plt.subplots(4, 5,figsize=(20, 10))
data_days = []
for d in range(days):
    # Get the power data from the required source
    data = data_load.get_power_data()

    #Plot the data
    if d < 20:
        axs[d//5,d%5].plot(data['Power'])
        axs[d//5,d%5].set_title("Dia "+str(d))
        axs[d//5,d%5].set_xlabel("Tiempo (Minutes)")
        axs[d//5,d%5].set_ylabel("Potencia (Watts)")
        data_days.append(data)
    # Proccess the data
    posibles_device_intervals,min_num_devices = data_processor.process_data(data)

    # Save the data to the knowledge base
    kb.save_events(posibles_device_intervals,min_num_devices)
plt.show()
kb.trim_devices(0.5)
kb.name_devices_from_stats(pd.read_csv("data_generator/data/devices.csv"))
kb.plot_device_analytics([1000,1500])

# Create the recomendation engine
re = RecomendationEngine()
# Get the electricity price data
electricity_price = data_load.get_electricity_price()
# Recommend the cheaper on times
list_devices = kb.get_list_devices()
re.recommend_cheaper_on_times(list_devices,electricity_price)
# Recommend to reduce the usage time of the most used and consuming devices
re.recommend_sorter_usage_time(list_devices)
