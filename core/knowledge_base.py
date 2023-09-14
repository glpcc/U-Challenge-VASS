import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from core.device import Device
import math

class KnowledgeBase():
    def __init__(self) -> None:
        # Dictionary with the devices connected to the power in the form of 
        # Power: [Device1,Device2,...]
        self.devices: dict[int,list[Device]] = dict()
        self.num_days = 0

    def distance_to_kpoints(self,point_distribution,k,starting_point):
        total_points = point_distribution[starting_point]
        distance = 1
        # While there are points to collect
        while total_points < k :
            if starting_point+distance < len(point_distribution):
                total_points += point_distribution[starting_point+distance]

            if starting_point-distance > 0:
                total_points += point_distribution[starting_point-distance]
            
            if starting_point+distance > len(point_distribution) and starting_point-distance < 0:
                distance = 0
                break
            else:
                distance += 1
        return distance - 1
    
    def save_events(self,events : pd.DataFrame):
        # Events is a dataframe with the following columns:
        # Power: int
        # On: int
        # Off: int
        # Complete?: bool
        self.num_days += 1
        for indx,event in events.iterrows():
            # Check if power in devices
            if event["Power"] in self.devices:
                # Check if the device is already in the list
                # TODO Add the posibility of adding more devices to the same power category
                for device in self.devices[event["Power"]]:
                    weight = 0
                    # The 0.1 number is an arbitrary number to be changed depending on the tendency to strong time patterns
                    k = device.weight_sum*0.1
                    # a,b selected from function desing to be near 1 around 20-40 minutes of distance
                    a = 1
                    b = -0.003
                    # Get the distance from the 3 features
                    distance = self.distance_to_kpoints(device.analitics["On_time"],k,event["On"])
                    weight += a*math.exp(distance*b)
                    distance = self.distance_to_kpoints(device.analitics["Off_time"],k,event["Off"])
                    weight += a*math.exp(distance*b)
                    distance = self.distance_to_kpoints(device.analitics["Operating_time"],k,event["Off"]-event["On"])
                    weight += a*math.exp(distance*b)
                    if weight > 3:
                        print("ERROR")
                    weight /= 3
                    # Remove 0.3 to the weight if the event was not the same power in the positive spike and the negative spike.
                    weight = max(weight-0.5,0) if event['Complete?'] else weight
                    # Add point to the device analitics
                    device.add_point(weight,event)

            else:
                # Create new device
                new_device = Device()
                new_device.add_point(1,event)
                self.devices[event["Power"]] = [new_device]
    
    def save_data(self):
        ...
    
    def read_data(self):
        ...

    # TODO TEMP
    def plot_device_analytics(self):
        for power in self.devices:
            for device in self.devices[power]:
                # Calculate the weighted average
                val = device.analitics.index
                wt = device.analitics["On_time"]
                print((val * wt).sum() / wt.sum())
                print(device.num_points)
                device.analitics.plot(title=str(power)+ "W",style='.')
                plt.show()

    def trim_devices(self,percentage_of_points):
        minimum_points = percentage_of_points*self.num_days
        print(minimum_points)
        for power in self.devices:
            for i in range(len(self.devices[power])):
                if self.devices[power][i].num_points < minimum_points:
                    del self.devices[power][i]