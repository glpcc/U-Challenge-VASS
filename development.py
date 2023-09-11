import pandas as pd
import numpy as np
from core.data_loader import DataLoader

data_load = DataLoader()

data = data_load.get_data(filename='hola')