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

list_devices = data_load.load_devices_data("data/")
kb.set_devices_by_list(list_devices)
kb.plot_device_analytics()