import pandas as pd
import numpy as np
from core.data_loader import DataLoader
from core.data_processor import DataProcessor
from core.device import Device
from core.knowledge_base import KnowledgeBase


# Generate the classes instances
data_load = DataLoader()
data_processor = DataProcessor(maximum_noise_level=2,max_power_spike_variance=5)
kb = KnowledgeBase()

days = 100

for d in range(days):
    # Get the power data from the required source
    data = data_load.get_data(f'','generate')

    # Proccess the data
    posibles_device_intervals,min_num_devices = data_processor.process_data(data)

    
    # for p,group in posibles_device_intervals.groupby("Power"):
    #     print(p)
    #     print(group)

    kb.save_events(posibles_device_intervals,min_num_devices)
    print(d)

kb.trim_devices(0.5)
kb.name_devices_from_csv(pd.read_csv("data_generator/data/devices.csv"))
kb.plot_device_analytics()