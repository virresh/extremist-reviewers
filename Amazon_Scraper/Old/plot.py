import matplotlib.pyplot as plt
import plotly.plotly as py

import parse_reviews as db

users_to_brands = {}
for i in ['tv','ac','washing_machine','fridge']:
	users_to_brands.update(db.users_to_brands(i))

suspicious_brands = {}
file = open("coupling.txt",'a')
for key in users_to_brands.keys():
	
	if users_to_brands[key] >= 3:
		user, brand = key
		print(key, users_to_brands[key])
		if brand not in suspicious_brands.keys():
			suspicious_brands[brand] = 0
		suspicious_brands[brand] += 1

		file.write(user + " " + str(users_to_brands[key]) + "\n")

print("Got",len(suspicious_brands),"suspicious brands")

x = list(suspicious_brands.keys())
y = []
for i in x:
	y.append(suspicious_brands[i])

bar = plt.bar(x,y,1/1.5,color='blue')
# plt.xticks(x, rotation=90)

for r in bar:
	h = r.get_height()
	plt.text(r.get_x() + r.get_width()/2.0, h, '%d' % int(h), ha='center', va='bottom')

plt.title("User to brand coupling")
plt.savefig("plot.png")

plt.show()