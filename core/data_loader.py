import pandas as pd
import numpy as np
from data_generator.data_generator2 import generate_data
import requests
import json
import datetime

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
