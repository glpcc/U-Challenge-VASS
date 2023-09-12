import pandas as pd
import numpy as np
from core.data_loader import DataLoader
from core.data_processor import DataProcessor

# Get the power data from the required source
data_load = DataLoader('data-generator/data/example_01.csv','csv')
data = data_load.get_data()

# Proccess the data
data_processor = DataProcessor(maximum_noise_level=2)
data_processor.process_data(data)