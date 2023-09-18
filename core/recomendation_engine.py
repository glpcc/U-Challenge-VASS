import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from core.device import Device


class RecomendationEngine():
    def __init__(self) -> None:
        pass

    def recommend_cheaper_on_times(self,devices,electricity_price: pd.DataFrame):
        ...

    def recommend_sorter_usage_time(self,devices: list[Device]):
        # Sort devices by the time they are used
        mean_usage_times = list(map(lambda x: (x,self.calculate_weighted_mean(x,"Operating_time")),devices))
        mean_usage_times.sort(key=lambda x: x[0].power*x[1],reverse=True)
        # Recommend to reduce the use time of the most used and consuming devices
        max_num_devices = min(5,len(mean_usage_times))
        for device,mean_usage_time in mean_usage_times[:max_num_devices]:
            print(f"El dispositivo llamado {device.name} consume {device.power}W y se usa en promedio {round(mean_usage_time/60,2)} horas al día")
            print(f"este dispositivo es uno de los que más consume y se usa, se recomienda reducir su uso si es posible")
        return devices
    
    def calculate_weighted_std(self,device: Device,field)-> float:
        val = device.analitics.index
        wt = device.analitics[field]
        mean = np.average(val, weights=wt)
        variance = np.average((val - mean)**2, weights=wt)
        return np.sqrt(variance)
    
    def calculate_weighted_mean(self,device: Device,field)-> float:
        val = device.analitics.index
        wt = device.analitics[field]
        return np.average(val, weights=wt)
