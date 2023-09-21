import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class DataProcessor():
    def __init__(self,maximum_noise_level: float,max_power_spike_variance: int) -> None:
        self.maximum_noise_level = maximum_noise_level
        self.max_power_spike_variance = max_power_spike_variance


    def process_data(self,df: pd.DataFrame):
        diffs = pd.DataFrame()
        diffs['Power_Diff'] = df['Power'].diff()
        diffs['Minute'] = df['Minute']
        # leave only elements above 5 in the diffs dataframe
        diffs = diffs[abs(diffs['Power_Diff']) > self.maximum_noise_level]
        # Round to the nearest multiple of the supplied variance to be able to use the spikes as dict keys
        diffs["Power_Diff"] = (diffs["Power_Diff"]/self.max_power_spike_variance).round() * self.max_power_spike_variance
        # Connect Posible On/Off moments for Same power devices
        df_connections = pd.DataFrame(columns={
            "Power":int,
            "On":int,
            "Off":int,
            "Complete?":bool
        })
        positive_spikes_dict = dict()
        negative_spikes_dict = dict()
        min_num_devices = dict()
        for i,row in diffs.iterrows():
            spike_power = row["Power_Diff"]
            minute = row["Minute"]
            
            if spike_power > 0:
                # Add one device to the min_num_devices dict if not already there
                if spike_power not in min_num_devices:
                    min_num_devices[spike_power] = 1

                # Add to the power spike dict the minute that corresponding amount of power came on
                if spike_power in positive_spikes_dict:
                    # Check if there must be more devices with that power 
                    positive_spikes_dict[spike_power].append(minute)
                    if min_num_devices[spike_power] < len(positive_spikes_dict[spike_power]):
                        min_num_devices[spike_power] += 1
                else:
                    positive_spikes_dict[spike_power] = [minute]

            else:
                if abs(spike_power) in negative_spikes_dict:
                    negative_spikes_dict[abs(spike_power)].append(minute)
                else:
                    negative_spikes_dict[abs(spike_power)] = [minute]

                # See if the negative spike has a positive sibling already seen
                if abs(spike_power) in positive_spikes_dict:
                    # Iterate through all the posible ON times for the device and add them to the result df
                    for j in positive_spikes_dict[abs(spike_power)]:
                        df_connections.loc[len(df_connections)] = [abs(spike_power),j,minute,True]
                    
                    pending_positive_spikes = len(positive_spikes_dict[abs(spike_power)])
                    pending_negative_spikes = len(negative_spikes_dict[abs(spike_power)])
                    if pending_negative_spikes == pending_positive_spikes:
                        # Clear both out to asume they were the same devices 
                        # as the posibility of two devices adding up the same power 
                        # and turning up at the same time is consider negligible on the long term
                        positive_spikes_dict[abs(spike_power)] = []
                        negative_spikes_dict[abs(spike_power)] = []
                    

                    
        # Take care of the outliers
        # exhaustively match the left over positive an negative spikes with each other
        for p in positive_spikes_dict:
            if len(positive_spikes_dict[p]) == 0:
                continue
            for pn in negative_spikes_dict:
                if len(negative_spikes_dict[pn]) == 0 or p == pn:
                    continue
                # If there are positive outliers with the same power dont consider it
                if len(positive_spikes_dict.get(pn,[])) > 0:
                    continue

                for min_p in positive_spikes_dict[p]:
                    for min_n in negative_spikes_dict[pn]:
                        if (min_n > min_p):
                            df_connections.loc[len(df_connections)] = [p,min_p,min_n,False]
                            df_connections.loc[len(df_connections)] = [pn,min_p,min_n,False]


        return df_connections, min_num_devices

            


        

        # Plot the diff dataframe if needed
        # plt.scatter(diffs['Minute'],diffs['Power_Diff'])
        # plt.plot(df['Minute'],df['Power'])
        # plt.show()
