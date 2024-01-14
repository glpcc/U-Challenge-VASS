import pandas as pd
import numpy as np
from data_generator.data_generator import generate_data
import requests
import json
import datetime
from core.device import Device

class DataLoader():

    def __init__(self) -> None:
        # Example of multiple data sources with seamless integration to the user of the class
        self.data_sources = {
            "csv" : self.get_data_from_csv,
            "api" : self.get_data_from_api,
            "generate": self.get_data_from_generator
        }

    def get_data(self,source,source_type)-> pd.DataFrame:
        return self.data_sources[source_type](source)

    def get_data_from_csv(self,source) -> pd.DataFrame:
        df = pd.read_csv(source)
        return df
    
    def get_data_from_api(self,**kwargs):
        ...

    def get_data_from_generator(self,source):
        # function that creates artificial data for testing purposes
        return generate_data()

    def get_electricity_price(self):
        # Get time of yesterday at midnight
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        today = datetime.datetime.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        #Dates as iso format
        today = today.isoformat(timespec='minutes')
        yesterday = yesterday.isoformat(timespec='minutes')
        url = f'https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date={yesterday}&end_date={today}&time_trunc=hour'
        r = requests.get(url,headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Host': 'apidatos.ree.es'}
        )
        #parse the json response
        json_response = json.loads(r.text)
        df = pd.read_json(json.dumps(json_response['included'][0]['attributes']['values']))

        # Pass the dataframe to minutes 
        df_mins = pd.DataFrame(np.zeros((24*60+1,1)),columns=['value'])

        temp = df.set_index(df.index * 60)
        df_mins['value'] = temp['value']
        df_mins.interpolate(method='linear',inplace=True)
        
        return df_mins

    def save_devices_data(self,devices: list[Device],path_to_save:str = "data/"):
        # Save the devices data to a csv file
        analytics_df = pd.DataFrame(columns=['Device_ID','On_time','Off_time','Operating_time','Minute'])
        device_df = pd.DataFrame(columns=['Name','Power','Weight_Sum','Num_Points','UID'])
        i = 0
        for device in devices:
            # Add the device to the dataframe
            device_df.loc[len(device_df)] = [device.name,device.power,device.weight_sum,device.num_points,i]
            temp_df = device.analytics.copy()
            temp_df['Device_ID'] = i
            temp_df['Minute'] = temp_df.index
            # Add the analytics to the dataframe
            analytics_df = pd.concat([analytics_df,temp_df[ (temp_df["On_time"] != 0) | (temp_df["Off_time"] != 0) | (temp_df["Operating_time"] != 0)]])
            i += 1
        # Save the dataframes to csv
        device_df.to_csv(path_to_save+"devices.csv",index=False)
        analytics_df.to_csv(path_to_save + "analytics.csv",index=False)
    

    def load_devices_data(self,path_to_load:str = "data/"):
        # Load the devices data from a csv file
        device_df = pd.read_csv(path_to_load+"devices.csv")
        analytics_df = pd.read_csv(path_to_load + "analytics.csv")
        devices = []
        for id,analytics in analytics_df.groupby('Device_ID'):
            device_row = device_df.loc[id]
            # Create a new device with the old data
            new_device = Device(device_row['Power'],device_row['Name'])
            new_device.num_points = device_row['Num_Points']
            new_device.weight_sum = device_row['Weight_Sum']
            # Add the analytics
            new_device.analytics = pd.DataFrame(np.zeros((1440,3)),columns=["On_time","Off_time","Operating_time"])
            new_device.analytics = new_device.analytics.add(analytics.set_index('Minute').drop(columns=['Device_ID']),fill_value=0)
            # Add the device to the list
            devices.append(new_device)
        return devices