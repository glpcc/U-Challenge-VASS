import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data-generator/data/example_day0.csv")
df.plot(x="Minute",y="Power")
plt.show()