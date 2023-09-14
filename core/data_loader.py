import pandas as pd
import numpy as np
from data_generator.data_generator2 import generate_data
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
