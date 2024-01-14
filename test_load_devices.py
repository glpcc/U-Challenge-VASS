import pandas as pd
import numpy as np
from core.data_loader import DataLoader
from core.data_processor import DataProcessor
from core.device import Device
from core.knowledge_base import KnowledgeBase
from core.recomendation_engine import RecomendationEngine
from matplotlib import pyplot as plt

# Generate the classes instances
data_load = DataLoader()
data_processor = DataProcessor(maximum_noise_level=2,max_power_spike_variance=5)
kb = KnowledgeBase()

# list_devices = data_load.load_devices_data("data/")
# kb.set_devices_by_list(list_devices)
# kb.plot_device_analytics()


days = 100
#Create a plot with the power data of the 20 first days
fig, axs = plt.subplots(4, 5,figsize=(20, 10))
data_days = []
for d in range(days):
    # Get the power data from the required source
    data = data_load.get_data(f'','generate')

    #Plot the data
    if d < 20:
        axs[d//5,d%5].plot(data['Power'])
        data_days.append(data)
    # Proccess the data
    posibles_device_intervals,min_num_devices = data_processor.process_data(data)

    # Save the data to the knowledge base
    kb.save_events(posibles_device_intervals,min_num_devices)

kb.trim_devices(0.5)
kb.name_devices_from_csv(pd.read_csv("data_generator/data/devices.csv"))
# kb.plot_device_analytics([50,120,200])

list_devices = kb.get_list_devices()

re = RecomendationEngine()
re.recommend_sorter_usage_time(list_devices)
re.recommend_cheaper_on_times(list_devices,data_load.get_electricity_price(),std_considerated_not_regular_use=4,min_std_usage_time_consider_regular=220,out_of_boundaries_usage_time=(0,1441))