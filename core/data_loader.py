


class DataLoader():

    def __init__(self) -> None:
        # Example of multiple data sources with seamless integration to the user of the class
        self.data_sources = {
            "csv" : self.get_data_from_csv,
            "api" : self.get_data_from_api
        }
        self.source_type = "csv"

    def get_data(self,**kwargs):
        self.data_sources[self.source_type](**kwargs)
    
    def get_data_from_csv(self,filename,**kwargs):
        print(filename)
    
    def get_data_from_api(self,**kwargs):
        ...