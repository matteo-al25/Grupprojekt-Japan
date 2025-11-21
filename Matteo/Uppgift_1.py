import pandas as pd
import hashlib
import matplotlib.pyplot as plt
from dash import Dash, html

df = pd.read_csv('/mnt/c/Users/emicr/Documents/GitHub/Grupprojekt-Japan/athlete_events.csv')

# SHA-256
df['Name_h'] = df['Name'].apply(
    lambda name: 
        hashlib.sha256(name.encode()).hexdigest()
)
# masking and filtering **Gemini 3.0 AI**
japan_medals = df[(df['Team'].str.contains('Japan', case=False, na=False)) & (df['Medal'].notna())]
medal_count = len(japan_medals) 
print(f"Japan's total medal count is: {medal_count}")

# Japan's best 3 sports
top_3_sport = japan_medals['Sport'].value_counts().head(3) 
print("Japan's top 3 most successful sports:")
print(top_3_sport)

# Japan's partecipation over the years
medals_per_OS = japan_medals['Year'].value_counts().sort_index(ascending=True)
print(medals_per_OS)

# Japan's athletes age 
Japan_age = df[(df['Team'].str.contains('Japan', case=False, na=False)) & (df['Age'].notna())]
plt.figure(figsize=(10, 6))
Japan_age['Age'].hist(
    bins=20, 
    edgecolor='black', 
    color='skyblue'
)

plt.title('Age Distribution of Japanese Athletes')
plt.xlabel('Age')
plt.ylabel('Frequency (Count)')
plt.grid(axis='y', alpha=0.5)