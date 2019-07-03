import pandas as pd

# df = pd.read_csv('data/params.csv', sep=';')
# lovers = df[df['avg_rating']>=4]
# haters = df[df['avg_rating']<=2]
# others = df[(df['avg_rating']>2) & (df['avg_rating']<4)]

# lovers.to_csv('data/brandlovers.csv', index=False, sep=';')
# haters.to_csv('data/brandhaters.csv', index=False, sep=';')
# others.to_csv('data/others.csv', index=False, sep=';')

df1 = pd.read_csv('data/params.csv', sep=';')
df2 = pd.read_csv('data/time_windows.txt', sep=',', header=None)
df2 = df2.rename(columns={0:'reviewer_id', 1:'avg_delay'})
df3 = pd.read_csv('data/rating_changes.txt', sep=';')
df = pd.merge(df1, df2, on='reviewer_id')
# print(df)
# print(df3)
df = pd.merge(df, df3, on='reviewer_id')
# print(df.describe())
df.to_csv('data/params_final.csv', index=None, sep=';')
