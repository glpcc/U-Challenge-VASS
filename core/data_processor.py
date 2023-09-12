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
        power_spikes_dict = dict()
        outlier_spikes = set()
        for i in diffs.index:
            spike_power = diffs["Power_Diff"][i]
            # 
            minute = diffs["Minute"][i]
            if spike_power > 0:
                # Add to the power spike dict the minute that corresponding amount of power came on
                if spike_power in power_spikes_dict:
                    power_spikes_dict[spike_power].append(minute)
                else:
                    power_spikes_dict[spike_power] = [minute]

                # Save to the outlier spike set
                outlier_spikes.add((spike_power,minute))
            else:

                # See if the negative spike has a positive sibling alredy seen
                if abs(spike_power) in power_spikes_dict:
                    # Iterate through all the posible ON times for the device and add them to the result df
                    for j in power_spikes_dict[abs(spike_power)]:
                        df_connections.loc[len(df_connections)] = [abs(spike_power),j,minute,True]
                        outlier_spikes.discard((abs(spike_power)))
                        
            # TODO Take care of the outliers

        return df_connections

            


        

        # Plot the diff dataframe if needed
        # plt.scatter(diffs['Minute'],diffs['Power_Diff'])
        # plt.plot(df['Minute'],df['Power'])
        # plt.show()
