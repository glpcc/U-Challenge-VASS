import requests
import json
import datetime
import pandas as pd
from matplotlib import pyplot as plt

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
print(json.dumps(json_response, indent=4, sort_keys=True))

df = pd.read_json(json.dumps(json_response['included'][0]['attributes']['values']))
print(df)
# plot the data
plt.plot(df['value'])
plt.show()
