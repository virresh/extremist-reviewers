
import matplotlib.pyplot as plt
import plotly.plotly as py
import numpy as np
import pandas as pd
suspicious_brands = {}

for i,line in enumerate(open("coupling.txt",'r')):
	l = line.strip().split("@")
	brand = l[1]
	total,verified,unverified = map(int,l[2:])
	verified /= total
	unverified /= total
	if total >= 2:
		try:
			suspicious_brands[brand][0] += 1
			suspicious_brands[brand][1] += verified
			suspicious_brands[brand][2] += unverified
		except:
			suspicious_brands[brand] = [1,verified,unverified]

	#if i==100: break

x = list(suspicious_brands.keys())
y_total = [i[0] for i in suspicious_brands.values()]
y_verified = [i[1] for i in suspicious_brands.values()]
y_unverified = [i[2] for i in suspicious_brands.values()]

df = pd.DataFrame(np.c_[y_total,y_verified,y_unverified], index = x)
df.columns = ['Total','Verified','Unverified']
df.plot(kind='bar',width=0.8)

plt.title("User to brand coupling")
plt.savefig("coupling_plot.png")
plt.show()