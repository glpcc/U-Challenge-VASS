import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from core.device import Device
from core.utils import calculate_weighted_mean,calculate_weighted_std

class RecomendationEngine():
    def __init__(self) -> None:
        pass

    def recommend_cheaper_on_times(self,devices: list[Device],electricity_price: pd.DataFrame,std_considerated_not_regular_use: float = 4,min_std_usage_time_consider_regular: float = 220,out_of_boundaries_usage_time: tuple[int,int] = (0,1441)):
        # 0 index is the on time, 1 index is the off time, 2 index is the operating time
        mean_usage_times = {device: calculate_weighted_mean(device,2) for device in devices}
        std_usage_times = {device: calculate_weighted_std(device,2) for device in devices}
        mean_on_times = {device: calculate_weighted_mean(device,0) for device in devices}
        std_on_times = {device: calculate_weighted_std(device,0) for device in devices}

        cost_reduction_per_device = []
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
            most_efficcient_minute = int(min_index)
            cost_reduction = convolution[round(mean_on_times[device])] - convolution[most_efficcient_minute]
            cost_reduction_per_device.append((device,cost_reduction))
        num_recommendations = min(3,len(cost_reduction_per_device))
        cost_reduction_per_device.sort(key=lambda x: x[1],reverse=True)
        for device,cost_reduction in cost_reduction_per_device[:num_recommendations]:
            # Print the recomendation
            print(f"Se podrian ahorrar {cost_reduction:.2f}€ si el dispositivo llamado {device.name} que consume {device.power}W se usara a las {round(most_efficcient_minute/60)}:{round(most_efficcient_minute%60)}h \
                    \nen vez de a las {round(mean_on_times[device]/60)}:{round(mean_on_times[device]%60)}h lo que equivale a {cost_reduction*365:.2f}€ al año\n" 
            )
            




    def recommend_sorter_usage_time(self,devices: list[Device]):
        kg_C02_per_kWh = 0.273 # Average in spain in 2022
        # 0 index is the on time, 1 index is the off time, 2 index is the operating time
        # Sort devices by the time they are used
        mean_usage_times = list(map(lambda x: (x,calculate_weighted_mean(x,2)),devices))
        mean_usage_times.sort(key=lambda x: x[0].power*x[1],reverse=True)
        # Recommend to reduce the use time of the most used and consuming devices
        max_num_devices = min(3,len(mean_usage_times))
        for device,mean_usage_time in mean_usage_times[:max_num_devices]:
            print(f"El dispositivo llamado {device.name} consume {device.power}W y se usa en promedio {round(mean_usage_time/60,2)} horas al día")
            print(f"este dispositivo es uno de los que más consume y se usa, se recomienda reducir su uso si es posible")
            if mean_usage_time > 60:
                print(f"Si se reduce el uso de este dispositivo en 1 hora al día se ahorrarían {(device.power/1000)*kg_C02_per_kWh*365:.2f}kg de CO2 al año\n")
        return devices
    

    