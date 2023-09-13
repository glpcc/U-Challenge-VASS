import pandas as pd
import numpy as np
from core.data_loader import DataLoader
from core.data_processor import DataProcessor
from core.device import Device


# Get the power data from the required source
data_load = DataLoader('data-generator/data/example_01.csv','csv')
data = data_load.get_data()

# Proccess the data
data_processor = DataProcessor(maximum_noise_level=2,max_power_spike_variance=3)
posibles_device_intervals = data_processor.process_data(data)
print(posibles_device_intervals)

# Create a test device
test_device = Device("Test Device")