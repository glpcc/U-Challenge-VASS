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

    def save_events(self,events : pd.DataFrame, min_num_devices: dict[int,int]):
        '''Function to save the events to the analytics of the devices in the knowledge base
            Events is a dataframe with the following columns:
            Power: int
            On: int
            Off: int
            Complete?: bool
        '''
        self.num_days += 1
        for power,group in events.groupby("Power"):
            power = int(power) # type: ignore
            # Check if there is any device with that power
            if power not in self.devices:
                # Create new device
                new_device = Device(power,name=f"Unknown device {power}W 0")
                self.devices[power] = [new_device]

            # Make a list of the new devices that need to be created
            num_new_devices = max(min_num_devices.get(power,0) - len(self.devices[power]),0)
            new_devices = [Device(power,name=f"Unknown device {power}W {i +1 + len(self.devices[power])}") for i in range(num_new_devices)]
            j = 0
            for i,(_,on_time,off_time,complete) in group.iterrows():
                max_w = 0
                weights = []
                for device in self.devices[power]:
                    w = self.calculate_event_weight(device,on_time,off_time,complete)
                    weights.append(w)
                    max_w = max(max_w,w)
                

                for j,device in enumerate(self.devices[power]):
                    w = weights[j]
                    w -= 0.5 if max_w > w else -0.2
                    w = max(w,0)
                    device.add_point(w,on_time,off_time)

                if num_new_devices > 0:
                    # Add the opposite of the max_w to start accepting the points no other accept
                    # The j % num_new_devices is to separate at start, 
                    # the points for the new devices to separate their tendecy to accept different patterns
                    new_devices[j%num_new_devices].add_point(1-max_w,on_time,off_time)
                    j += 1
            self.devices[power] += new_devices
    
    def calculate_event_weight(self,device: Device,on_time,off_time,complete):
        '''Function to calculate the weight of a certain event for a device'''
        if device.num_points == 0:
            return 1
        weight = 0
        # The 0.1 number is an arbitrary number to be changed depending on the tendency to strong time patterns
        k = round(device.weight_sum*0.35)
        # b selected from function desing to be near 1 around 20-40 minutes of distance
        b = 2e-5
        # Get the distance from the 3 features
        distance = self.distance_to_kpoints(device.on_time_analytics,k,on_time)
        weight += self._distance_to_weight_function(b,distance)
        distance = self.distance_to_kpoints(device.off_time_analytics,k,off_time)
        weight += self._distance_to_weight_function(b,distance)
        distance = self.distance_to_kpoints(device.operating_time_analytics,k,off_time-on_time)
        weight += self._distance_to_weight_function(b,distance)
        weight /= 3
        # Remove 0.3 to the weight if the event was not the same power in the positive spike and the negative spike.
        weight = max(weight-0.4,0) if complete else weight
        return weight

    @staticmethod
    def _distance_to_weight_function(b,distance):
        '''Customizable function to convert the distance to a weight'''
        return math.exp(-b*(distance**2))


    def distance_to_kpoints(self, point_distribution: np.ndarray, k: int, starting_point: int):
        '''Function to calculate the distance to the k points around the starting point'''
        total_points = point_distribution[starting_point]
        distance = 1
        # While in the circle arround the starting point there are less than k points
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
        
    def plot_device_analytics(self,power_to_plot: None | list[int] = None):
        '''Function to plot the analytics of the devices'''
        for power in self.devices:
            if power_to_plot is not None and power not in power_to_plot:
                continue

            for device in self.devices[power]:
                analytics = device.get_as_dataframe()
                on_time_analytics = device.on_time_analytics
                off_time_analytics = device.off_time_analytics
                operating_time_analytics = device.operating_time_analytics
                # Create 1d gaussian kernel
                size = 100
                std = 30
                x = np.linspace(-size / 2, size / 2, size)
                gaussian = np.exp(-(x / std) ** 2)
                # apply gaussian convolution to the analytics
                on_time_analytics = np.convolve(on_time_analytics, gaussian, mode='same')
                off_time_analytics = np.convolve(off_time_analytics, gaussian, mode='same')
                operating_time_analytics = np.convolve(operating_time_analytics, gaussian, mode='same')
                # Plot area 
                plt.fill_between(analytics.index,0,on_time_analytics,alpha=0.8)
                plt.fill_between(analytics.index,0,off_time_analytics,alpha=0.8)
                plt.fill_between(analytics.index,0,operating_time_analytics,alpha=0.8)
                # Add the legend
                plt.legend(["On time","Off time","Operating time"])
                # Add the title
                plt.title(f"{device.name} {device.power}W")
                # Add the labels
                plt.xlabel("Tiempo (Minutos)")
                plt.ylabel("Peso")
                plt.show()


    def trim_devices(self,percentage_of_points):
        '''Function to trim the devices that have less than the percentage of points of the total days'''
        minimum_points = percentage_of_points*self.num_days
        for power in self.devices:
            for i in range(len(self.devices[power])):
                if self.devices[power][i].num_points < minimum_points:
                    del self.devices[power][i]

    def name_devices_from_stats(self,devices_names: pd.DataFrame):
        '''Function to name the devices from a dataframe with the power usage and usual on and off time of the devices '''
        for power,group in devices_names.groupby("Power"):
            if power not in self.devices:
                raise Exception(f"No devices with power {power}W")

            time_index = np.arange(0,1440)
            on_time_means = np.empty(len(self.devices[power]))
            off_time_means = np.empty(len(self.devices[power]))
            operating_time_means = np.empty(len(self.devices[power]))
            # Calculate the weighted means of the devices
            for i,device in enumerate(self.devices[power]):
                on_time_means[i] = np.average(time_index,weights=device.on_time_analytics)
                off_time_means[i] = np.average(time_index,weights=device.off_time_analytics)
                operating_time_means[i] = np.average(time_index,weights=device.operating_time_analytics)
            
            for i,device in group.iterrows():
                # Calculate the differences to the know devices
                differnces = abs(device["Usual_On_time"] - on_time_means) + abs(device["Usual_Off_time"] - off_time_means) + abs((device["Usual_Off_time"]-device["Usual_On_time"]) - operating_time_means)
                # Get the index of the minimum difference
                index = differnces.argmin()
                if index < len(self.devices[power]):
                    self.devices[power][index].name = device["Device_Name"]
            
    def create_known_devices(self,devices_names: pd.DataFrame):
        '''Function to create the devices from a dataframe with only the power and name of the devices '''
        for i, (name,power) in devices_names.iterrows():
            if power not in self.devices:
                # Create new device
                new_device = Device(power,name)
                self.devices[power] = [new_device]
            else:
                new_device = Device(power,name)
                self.devices[power].append(new_device)
        
    def get_list_devices(self):
        '''Function to get a list of all the devices in the knowledge base'''
        list_devices = list(self.devices.values())
        # Unpack the list of lists
        return [item for sublist in list_devices for item in sublist]

    def set_devices_by_list(self,list_devices: list[Device]):
        '''Function to set the devices in the knowledge base from a list of devices'''
        for i in list_devices:
            if i.power not in self.devices:
                self.devices[i.power] = [i]
            else:
                self.devices[i.power].append(i)