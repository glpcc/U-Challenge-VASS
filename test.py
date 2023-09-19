import requests
import json
import datetime
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

# make a to a server with certain headers
# Get time of yesterday at midnight
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
today = datetime.datetime.now()
today = today.replace(hour=0, minute=0, second=0, microsecond=0)
#today as iso format
today = today.isoformat(timespec='minutes')
yesterday = yesterday.isoformat(timespec='minutes')
url = f'https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date={yesterday}&end_date={today}&time_trunc=hour'
print(url)

r = requests.get(url,headers={
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Host': 'apidatos.ree.es'}
)
print(r.status_code)
print(r.headers['content-type'])
#parse the json response
json_response = json.loads(r.text)
# pretty print the response
#print(json.dumps(json_response, indent=4, sort_keys=True))

df = pd.read_json(json.dumps(json_response['included'][0]['attributes']['values']))
#print(df)

# Pass the dataframe to minutes 
df_mins = pd.DataFrame(np.zeros((24*60+1,1)),columns=['value'])

temp = df.set_index(df.index * 60)
df_mins['value'] = temp['value']
df_mins.interpolate(method='linear',inplace=True)

test_power = 1000
test_usage_time = 235
power_usage = np.zeros(test_usage_time)
power_usage.fill(test_power)
# Pass to mega Watts
power_usage = power_usage/1e6
# Pass the prices of price per minute
df_mins['value'] = df_mins['value']/60
limits = (0,1440)

convolution = np.convolve(power_usage,df_mins['value'][limits[0]:limits[1]],mode='valid')
print(convolution)
print(convolution.min())

plt.plot(convolution)
plt.show()
