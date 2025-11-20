import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import hashlib as hl

athlete_events = pd.read_csv(r'athlete_events.csv')

athlete_events_enc = athlete_events.copy()
athlete_events_enc['Name'] = athlete_events_enc['Name'].apply(lambda x: hl.sha256(x.encode()).hexdigest())
athlete_events_enc = athlete_events_enc.rename(columns={'Name': 'SHA-256-Name'})


def gruppering(df):
    medaljer = df[df['Medal'].notna()]
    placeringar = medaljer.groupby(['Year', 'NOC', 'Event', 'Medal']).size().reset_index(name='Count')
    os_med_count = df.merge(placeringar, on=['Year', 'NOC', 'Event', 'Medal'], how='right')

    lagsporter = placeringar[placeringar['Count'] > 1]
    indiv = placeringar[placeringar['Count'] == 1]

    return {
        'medaljer': medaljer,
        'placeringar': placeringar,
        'os_med_count': os_med_count,
        'lagsporter': lagsporter,
        'indiv': indiv
    }

def japan_stats(df_grupperad):
    os_japaner = df_grupperad['os_med_count'][df_grupperad['os_med_count']['NOC'] == 'JPN']

    jap_lag = os_japaner[os_japaner['Count'] > 1]
    jap_ind = os_japaner[os_japaner['Count'] == 1]

    guld = os_japaner[os_japaner['Medal'] == 'Gold']
    silver = os_japaner[os_japaner['Medal'] == 'Silver']
    brons = os_japaner[os_japaner['Medal'] == 'Bronze']

    return {
        'os_japaner': os_japaner,
        'lagvinster': jap_lag,
        'indvinster': jap_ind,
        'guld': guld,
        'silver': silver,
        'brons': brons
    }

def könsfördelning(df):
    totalt = df['ID'].nunique()
    kvinnor = df[df['Sex'] == 'F']['ID'].nunique()
    män = df[df['Sex'] == 'M']['ID'].nunique()

    return totalt, kvinnor, män

medalj_data = gruppering(athlete_events_enc)
japan = japan_stats(medalj_data)
japan_lagvinster = medalj_data['lagsporter'][medalj_data['lagsporter']['NOC']=='JPN']
antal_jap, antal_jap_f, antal_jap_m = könsfördelning(japan['os_japaner'])

lagsporter_topp50 = (medalj_data['lagsporter'].groupby('NOC')['Count'].sum().sort_values(ascending=False).head(50))
indsporter_topp50 = (medalj_data['indiv'].groupby('NOC')['Count'].sum().sort_values(ascending=False).head(50))

fig = plt.figure(figsize=(20, 14))
gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1])

ax1 = fig.add_subplot(gs[0, :])
ax1.bar(lagsporter_topp50.index, lagsporter_topp50.values)
ax1.set_title('Medaljer i lagsporter för topp 50 land')
ax1.set_xlabel('Land (NOC)')
ax1.set_ylabel('Antal medaljer')
ax1.tick_params(axis='x', rotation=90)

ax2 = fig.add_subplot(gs[1, :])
ax2.bar(indsporter_topp50.index, indsporter_topp50.values)
ax2.set_title('Medaljer i individuella sporter för topp 50 land')
ax2.set_xlabel('Land (NOC)')
ax2.tick_params(axis='x', rotation=90)

ax3 = fig.add_subplot(gs[2, 0])
ax3.bar(['Lagsporter', 'Individuellt'], [medalj_data['lagsporter']['Count'].sum(), medalj_data['indiv']['Count'].sum()])
ax3.set_title('Antal medaljer i lag vs individuellt (globalt)')
ax3.set_ylabel('Antal medaljer')

ax4 = fig.add_subplot(gs[2, 1])
ax4.bar(['Lagsporter', 'Individuellt'], [japan['lagvinster']['Count'].sum(), japan['indvinster']['Count'].sum()])
ax4.set_title('Antal medaljer i lag vs individuellt (Japan)')
ax4.set_ylabel('Antal medaljer')

plt.tight_layout()
plt.show()

fig, axes = plt.subplots(1, 2, figsize=(12, 6))

axes[0].bar(['Lagsporter', 'Individuellt'], [len(medalj_data['lagsporter']), len(medalj_data['indiv'])])
axes[0].set_title('Antal podiumplaceringar i lag vs individuellt (globalt)')
axes[0].set_ylabel('Antal podiumplaceringar')

axes[1].bar(['Lagsporter', 'Individuellt'], [len(japan_lagvinster), len(japan['indvinster'])])
axes[1].set_title('Antal podiumplaceringar i lag vs individuellt (Japan)')
axes[1].set_ylabel('Antal podiumplaceringar')

plt.tight_layout()
plt.show()

fig, axes = plt.subplots(2, 2, figsize=(12, 12))

axes[0, 0].pie([len(japan['guld'][japan['guld']['Sex']=='F']), len(japan['guld'][japan['guld']['Sex']=='M'])], labels=['Kvinnor', 'Män'], autopct='%2.2f%%', startangle=90)
axes[0, 0].set_title('Könsfördelning guldplaceringar (Japan)')

axes[0, 1].pie([len(japan['silver'][japan['silver']['Sex']=='F']), len(japan['silver'][japan['silver']['Sex']=='M'])], labels=['Kvinnor', 'Män'], autopct='%2.2f%%', startangle=90)
axes[0, 1].set_title('Könsfördelning silverplaceringar (Japan)')

axes[1, 0].pie([len(japan['brons'][japan['brons']['Sex']=='F']), len(japan['brons'][japan['brons']['Sex']=='M'])], labels=['Kvinnor', 'Män'], autopct='%2.2f%%', startangle=90)
axes[1, 0].set_title('Könsfördelning bronsplaceringar (Japan)')

axes[1, 1].pie([antal_jap_f, antal_jap_m], labels=['Kvinnor', 'Män'], autopct='%2.2f%%', startangle=90)
axes[1, 1].set_title('Könsfördelning atleter (Japan)')

plt.tight_layout()
plt.show()