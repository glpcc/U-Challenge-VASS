import pandas as pd
import numpy as np

class DataLoader():

    def __init__(self,source, source_type) -> None:
        # Example of multiple data sources with seamless integration to the user of the class
        self.data_sources = {
            "csv" : self.get_data_from_csv,
            "api" : self.get_data_from_api
        }
        self.source_type = source_type
        self.source = source

    def get_data(self)-> pd.DataFrame:
        return self.data_sources[self.source_type]()

    def get_data_from_csv(self) -> pd.DataFrame:
        df = pd.read_csv(self.source)
        return df
    
    def get_data_from_api(self,**kwargs):
        ...