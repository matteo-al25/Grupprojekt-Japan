from dash import Dash, html, dcc, Input, Output
import pandas as pd
import hashlib as hl
from plotly.subplots import make_subplots
import plotly.graph_objects as go

app = Dash(__name__)

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

lagsporter_topp50_medalj = (medalj_data['lagsporter'].groupby('NOC')['Count'].sum().sort_values(ascending=False).head(50))
indsporter_topp50_medalj = (medalj_data['indiv'].groupby('NOC')['Count'].sum().sort_values(ascending=False).head(50))
medalj_total = medalj_data['lagsporter'].groupby('NOC')['Count'].sum() + medalj_data['indiv'].groupby('NOC')['Count'].sum()
podium_total = medalj_data['lagsporter'].groupby('NOC').size() + medalj_data['indiv'].groupby('NOC').size()
topp50_medalj = medalj_total.sort_values(ascending=False).head(50)
topp50_podium = podium_total.sort_values(ascending=False).head(50)
fig_height = 600
fig_margin = dict(t=80, l=40, r=40, b=40)

fig_topp50 = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Lagsporter topp 50', 'Individuella topp 50')
)
fig_topp50.add_trace(
    go.Bar(x=lagsporter_topp50_medalj.index, y=lagsporter_topp50_medalj.values),
    row=1, col=1
)
fig_topp50.add_trace(
    go.Bar(x=indsporter_topp50_medalj.index, y=indsporter_topp50_medalj.values),
    row=1, col=2
)
fig_topp50.update_layout(title='Topp 50 länder: lag vs individuellt', height=fig_height, margin=fig_margin)

fig_medaljer = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Globalt', 'Japan')
)
fig_medaljer.add_trace(
    go.Bar(x=['Lagsporter','Individuellt'],
           y=[medalj_data['lagsporter']['Count'].sum(), medalj_data['indiv']['Count'].sum()]),
    row=1, col=1
)
fig_medaljer.add_trace(
    go.Bar(x=['Lagsporter','Individuellt'],
           y=[japan['lagvinster']['Count'].sum(), japan['indvinster']['Count'].sum()]),
    row=1, col=2
)
fig_medaljer.update_layout(title='Medaljer lag vs individ (globalt + Japan)', height=fig_height, margin=fig_margin)

fig_kön = make_subplots(
    rows=2, cols=2,
    specs=[
        [{'type': 'domain'}, {'type': 'domain'}],
        [{'type': 'domain'}, {'type': 'domain'}]
    ],
    subplot_titles=('Guld', 'Silver', 'Brons', 'Atleter totalt'),
    horizontal_spacing=0.05,
    vertical_spacing=0.05  
)
fig_kön.add_trace(
    go.Pie(labels=['Kvinnor','Män'],
           values=[len(japan['guld'][japan['guld']['Sex']=='F']),
                   len(japan['guld'][japan['guld']['Sex']=='M'])]),
    row=1, col=1
)
fig_kön.add_trace(
    go.Pie(labels=['Kvinnor','Män'],
           values=[len(japan['silver'][japan['silver']['Sex']=='F']),
                   len(japan['silver'][japan['silver']['Sex']=='M'])]),
    row=1, col=2
)
fig_kön.add_trace(
    go.Pie(labels=['Kvinnor','Män'],
           values=[len(japan['brons'][japan['brons']['Sex']=='F']),
                   len(japan['brons'][japan['brons']['Sex']=='M'])]),
    row=2, col=1
)
fig_kön.add_trace(
    go.Pie(labels=['Kvinnor','Män'],
           values=[antal_jap_f, antal_jap_m]),
    row=2, col=2
)
fig_kön.update_layout(title='Japan könsfördelningar')

fig_podium = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Globalt', 'Japan')
)
fig_podium.add_trace(
    go.Bar(x=['Lagsporter','Individuellt'],
           y=[len(medalj_data['lagsporter']), len(medalj_data['indiv'])]),
    row=1, col=1
)
fig_podium.add_trace(
    go.Bar(x=['Lagsporter','Individuellt'],
           y=[len(japan_lagvinster), len(japan['indvinster'])]),
    row=1, col=2
)
fig_podium.update_layout(title='Podiumplaceringar lag vs individ (globalt + Japan)', height=fig_height, margin=fig_margin)

fig_topp50_tot = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Medaljer topp 50', 'Podiumplaceringar topp 50')
)
fig_topp50_tot.add_trace(
    go.Bar(x=topp50_medalj.index, y=topp50_medalj.values),
    row=1, col=1
)
fig_topp50_tot.add_trace(
    go.Bar(x=topp50_podium.index, y=topp50_podium.values),
    row=1, col=2
)
fig_topp50_tot.update_layout(title='Topp 50 länder: medaljer vs podiumplaceringar', height=fig_height, margin=fig_margin)

plots = {
    'Topp 50 medaljer': fig_topp50,
    'Medaljer lag vs individ (globalt + Japan)': fig_medaljer,
    'Japan könsfördelningar': fig_kön,
    'Podiumplaceringar (globalt + Japan)': fig_podium,
    'Topp 50 podiumjämförelse': fig_topp50_tot    
}

app.layout = html.Div([
    html.H1('Min första Dash-app'),
    
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': key, 'value': key} for key in plots.keys()],
        value=list(plots.keys())[0]
    ),
    dcc.Graph(id='plot')
])

@app.callback(
    Output('plot', 'figure'),
    Input('dropdown', 'value')
)
def update_graph(selected_plot):
    return plots[selected_plot]

if __name__ == '__main__':  
    app.run(debug=True)