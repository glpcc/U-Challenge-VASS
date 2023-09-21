import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from core.device import Device


class RecomendationEngine():
    def __init__(self) -> None:
        pass

    def recommend_cheaper_on_times(self,devices: list[Device],electricity_price: pd.DataFrame):
        mean_usage_times = {device: self.calculate_weighted_mean(device,"Operating_time") for device in devices}
        std_usage_times = {device: self.calculate_weighted_std(device,"Operating_time") for device in devices}
        mean_on_times = {device: self.calculate_weighted_mean(device,"On_time") for device in devices}
        std_on_times = {device: self.calculate_weighted_std(device,"On_time") for device in devices}

        # Some parameters to determine the recomendations
        std_considerated_not_regular_use = 4 # minutes of standard deviation to consider that a device is not used at the same time every day
        min_std_usage_time_consider_regular = 220 # minutes of standard deviation to consider that a device is used the same amount of time every day
        out_of_boundaries_usage_time = (0,1441) # tuple with the minimum and maximum time in minutes a recommendation should tell to use the device (to for example exclude the sleeping time)


        for device in devices:
            if std_on_times[device] < std_considerated_not_regular_use:
                continue
            if std_usage_times[device] > min_std_usage_time_consider_regular:
                continue

            power_usage = np.zeros(round(mean_usage_times[device]))
            
            power_usage.fill(device.power)
            # Pass to mega Watts
            power_usage = power_usage/1e6
            # Pass the prices of price per minute
            electricity_price_per_min = electricity_price['value']/60
            limits = out_of_boundaries_usage_time
            convolution = np.convolve(power_usage,electricity_price_per_min[limits[0]:limits[1]],mode='valid')

            # Get the index of the minimum value of the convolution
            min_index = convolution.argmin()
            most_efficcient_minute = min_index
            cost_reduction = convolution[round(mean_on_times[device])] - convolution[most_efficcient_minute]
            # Print the recomendation
            print(f"Se podrian ahorrar {cost_reduction:.2f}€ si el dispositivo llamado {device.name} que consume {device.power}W se usara a las {round(most_efficcient_minute/60)}:{round(most_efficcient_minute%60)}h \
                   \n en vez de a las {round(mean_on_times[device]/60)}:{round(mean_on_times[device]%60)}h\n"
            )
            




    def recommend_sorter_usage_time(self,devices: list[Device]):
        # Sort devices by the time they are used
        mean_usage_times = list(map(lambda x: (x,self.calculate_weighted_mean(x,"Operating_time")),devices))
        mean_usage_times.sort(key=lambda x: x[0].power*x[1],reverse=True)
        # Recommend to reduce the use time of the most used and consuming devices
        max_num_devices = min(5,len(mean_usage_times))
        for device,mean_usage_time in mean_usage_times[:max_num_devices]:
            print(f"El dispositivo llamado {device.name} consume {device.power}W y se usa en promedio {round(mean_usage_time/60,2)} horas al día")
            print(f"este dispositivo es uno de los que más consume y se usa, se recomienda reducir su uso si es posible\n")
        return devices
    
    def calculate_weighted_std(self,device: Device,field)-> float:
        val = device.analytics.index
        wt = device.analytics[field]
        mean = np.average(val, weights=wt)
        variance = np.average((val - mean)**2, weights=wt)
        return np.sqrt(variance)
    
    def calculate_weighted_mean(self,device: Device,field)-> float:
        val = device.analytics.index
        wt = device.analytics[field]
        return np.average(val, weights=wt)

    