import pandas as pd
import numpy as np
from core.data_loader import DataLoader
from core.data_processor import DataProcessor
from core.device import Device
from core.knowledge_base import KnowledgeBase
from core.recomendation_engine import RecomendationEngine

# Generate the classes instances
data_load = DataLoader()
data_processor = DataProcessor(maximum_noise_level=2,max_power_spike_variance=5)
kb = KnowledgeBase()

days = 10

for d in range(days):
    # Get the power data from the required source
    data = data_load.get_data(f'','generate')

    # Proccess the data
    posibles_device_intervals,min_num_devices = data_processor.process_data(data)

    
    # Save the data to the knowledge base
    kb.save_events(posibles_device_intervals,min_num_devices)

    # Print the progress
    print(d)

kb.trim_devices(0.5)
kb.name_devices_from_csv(pd.read_csv("data_generator/data/devices.csv"))

# Recommend to the user
re = RecomendationEngine()
list_devices = list(kb.devices.values())
list_devices = [item for sublist in list_devices for item in sublist]
re.recommend_sorter_usage_time(list_devices)
#kb.plot_device_analytics()