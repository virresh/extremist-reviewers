import pandas as pd
df = pd.read_csv('coupling.txt', header=None, sep=';')
df = df[df[2]>=2]
df = df.drop_duplicates(subset=[0])
df.to_csv('../data_plotting/ranked.csv', index=False, sep=';', header=['reviewer_id', 'brand', 'coupling', 'verified', 'not_verified'])
