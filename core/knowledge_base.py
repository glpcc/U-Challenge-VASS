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
        point_distribution = point_distribution.values
        starting_point = int(starting_point)
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
    
    def save_events(self,events : pd.DataFrame, min_num_devices: dict[int,int]):
        # Events is a dataframe with the following columns:
        # Power: int
        # On: int
        # Off: int
        # Complete?: bool
        self.num_days += 1
        for power,group in events.groupby("Power"):
            # Check if there is any device with that power
            if power not in self.devices:
                # Create new device
                new_device = Device(power,name=f"Unknown device {power}W 0")
                self.devices[power] = [new_device]

            # Make a list of the new devices that need to be created
            num_new_devices = max(min_num_devices.get(power,0) - len(self.devices[power]),0)
            new_devices = [Device(power,name=f"Unknown device {power}W {i +1 + len(self.devices[power])}") for i in range(num_new_devices)]
            j = 0
            for i,event in group.iterrows():
                max_w = 0
                weights = []
                for device in self.devices[power]:
                    w = self.calculate_event_weight(device,event)
                    weights.append(w)
                    max_w = max(max_w,w)
                

                for j,device in enumerate(self.devices[power]):
                    w = weights[j]
                    w -= 0.3 if max_w > w else 0
                    w = max(w,0)
                    device.add_point(w,event)

                if num_new_devices > 0:
                    # Add the opposite of the max_w to start accepting the points no other accept
                    # The j % num_new_devices is to separate at start, 
                    # the points for the new devices to separate their tendecy to accept different patterns
                    new_devices[j%num_new_devices].add_point(1-max_w,event)
                    j += 1
            self.devices[power] += new_devices
    
    def calculate_event_weight(self,device: Device,event):
        if device.num_points == 0:
            return 1
        weight = 0
        # The 0.1 number is an arbitrary number to be changed depending on the tendency to strong time patterns
        k = device.weight_sum*0.35
        # a,b selected from function desing to be near 1 around 20-40 minutes of distance
        a = 1
        b = -0.008
        # Get the distance from the 3 features
        distance = self.distance_to_kpoints(device.analytics["On_time"],k,event["On"])
        weight += a*math.exp(distance*b)
        distance = self.distance_to_kpoints(device.analytics["Off_time"],k,event["Off"])
        weight += a*math.exp(distance*b)
        distance = self.distance_to_kpoints(device.analytics["Operating_time"],k,event["Off"]-event["On"])
        weight += a*math.exp(distance*b)
        weight /= 3
        # Remove 0.3 to the weight if the event was not the same power in the positive spike and the negative spike.
        weight = max(weight-0.3,0) if event['Complete?'] else weight
        return weight


    def plot_device_analytics(self,power_to_plot: None | list[int] = None):
        for power in self.devices:
            if power_to_plot is not None and power not in power_to_plot:
                continue

            for device in self.devices[power]:
                print(device.power,device.num_points)
                device.analytics.plot(title=f'{device.name} {device.power}W',style='.')
                plt.show()


    def trim_devices(self,percentage_of_points):
        minimum_points = percentage_of_points*self.num_days
        for power in self.devices:
            for i in range(len(self.devices[power])):
                if self.devices[power][i].num_points < minimum_points:
                    del self.devices[power][i]

    def name_devices_from_csv(self,devices_names: pd.DataFrame):
        # function to name the devices from a dataframe with the power usage and usual on and off time of the devices
        # Mainly for testing purposes
        for power,group in devices_names.groupby("Power"):
            if power not in self.devices:
                # TODO add the device to the class dict and add the mean as a point
                continue
            devices_means = pd.DataFrame(columns={
                "On_time":int,
                "Off_time":int,
                "Operating_time":int
            })
            for device in self.devices[power]:
                # Calculate the weighted average
                val = device.analytics.index
                wt = device.analytics
                # Get the means 
                devices_means.loc[len(devices_means)] = (wt.mul(val,axis=0)).sum() / wt.sum()
            
            for i,device in group.iterrows():
                # Calculate the differences to the know devices
                differnces = abs(device["Usual_On_time"] - devices_means["On_time"].values) + abs(device["Usual_Off_time"] - devices_means["Off_time"].values) + abs((device["Usual_Off_time"]-device["Usual_On_time"]) - devices_means["Operating_time"].values)
                # Get the index of the minimum difference
                index = differnces.argmin()
                if index < len(self.devices[power]):
                    self.devices[power][index].name = device["Device_Name"]
            

    def get_list_devices(self):
        list_devices = list(self.devices.values())
        # Unpack the list of lists
        return [item for sublist in list_devices for item in sublist]

    def set_devices_by_list(self,list_devices: list[Device]):
        for i in list_devices:
            if i.power not in self.devices:
                self.devices[i.power] = [i]
            else:
                self.devices[i.power].append(i)