import pandas as pd
import numpy as np
from core.data_loader import DataLoader
import matplotlib.pyplot as plt

electricity_price = DataLoader().get_electricity_price()
fig = electricity_price.plot()
fig.set_xlabel("Tiempo (minutes)")
fig.set_ylabel("Precio (€/MWh)")
plt.show()