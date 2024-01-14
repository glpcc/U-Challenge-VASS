import pandas as pd
import numpy as np
from core.data_loader import DataLoader
from core.data_processor import DataProcessor
from core.device import Device
from core.knowledge_base import KnowledgeBase
from core.recomendation_engine import RecomendationEngine
from matplotlib import pyplot as plt
# Profiling
import cProfile
import pstats


# Generate the classes instances
data_load = DataLoader()
data_processor = DataProcessor(maximum_noise_level=2,max_power_spike_variance=5)
kb = KnowledgeBase()

# list_devices = data_load.load_devices_data("data/")
# kb.set_devices_by_list(list_devices)
# kb.plot_device_analytics()

# Profiling
with cProfile.Profile() as pr:
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
plt.show()
# Profiling
stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.CUMULATIVE)
stats.print_stats(30)