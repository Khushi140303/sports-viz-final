"""
Does Money Buy Wins?
Visualizing the Payroll-Performance Relationship in NFL, NBA & MLB
CS-GY 6313: Information Visualization — Final Project
Author: Khushi Agarwal
"""

import os
import pandas as pd
import requests
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Configuration ─────────────────────────────────────────
# Set your Groq API key here or as an environment variable:
# export GROQ_API_KEY="your_key_here"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
COLORS = {'NBA': '#1170AA', 'NFL': '#FC7D0B', 'MLB': '#A30000'}

# ── Data Loading ──────────────────────────────────────────

def load_data():
    # NBA Payroll
    nba_pay = pd.read_csv('NBA Payroll(1990-2023).csv')
    nba_pay['payroll'] = (nba_pay['payroll']
                          .str.replace('$', '', regex=False)
                          .str.replace(',', '', regex=False)
                          .astype(float))
    nba_pay = nba_pay[['team', 'seasonStartYear', 'payroll']]
    nba_pay.columns = ['team', 'season', 'payroll']

    # NBA Wins from Games.csv
    games = pd.read_csv('Games.csv', low_memory=False,
                        usecols=['hometeamCity', 'hometeamName',
                                 'awayteamCity', 'awayteamName',
                                 'homeScore', 'awayScore',
                                 'gameType', 'gameDate'])
    games = games[games['gameType'] == 'Regular Season'].copy()
    games['gameDate'] = pd.to_datetime(games['gameDate'])
    games['season'] = games['gameDate'].apply(
        lambda x: x.year if x.month >= 9 else x.year - 1)
    games['home_team'] = games['hometeamCity'] + ' ' + games['hometeamName']
    games['away_team'] = games['awayteamCity'] + ' ' + games['awayteamName']
    games['home_win'] = (games['homeScore'] > games['awayScore']).astype(int)

    home = games[['home_team', 'season', 'home_win']].copy()
    home.columns = ['team', 'season', 'win']
    away = games[['away_team', 'season', 'home_win']].copy()
    away['win'] = 1 - away['home_win']
    away.columns = ['team', 'season', 'win']

    all_games = pd.concat([home, away], ignore_index=True)
    nba_wins = all_games.groupby(['team', 'season']).agg(
        wins=('win', 'sum'), games=('win', 'count')).reset_index()
    nba_wins['losses'] = nba_wins['games'] - nba_wins['wins']
    nba_wins['win_pct'] = nba_wins['wins'] / nba_wins['games']
    nba_wins = nba_wins[['team', 'season', 'wins', 'losses', 'win_pct']]

    # Team name mapping
    name_map = {
        'Atlanta Hawks': 'Atlanta', 'Boston Celtics': 'Boston',
        'Brooklyn Nets': 'Brooklyn', 'New Jersey Nets': 'Brooklyn',
        'Charlotte Hornets': 'Charlotte', 'Charlotte Bobcats': 'Charlotte',
        'Chicago Bulls': 'Chicago', 'Cleveland Cavaliers': 'Cleveland',
        'Dallas Mavericks': 'Dallas', 'Denver Nuggets': 'Denver',
        'Detroit Pistons': 'Detroit', 'Golden State Warriors': 'Golden State',
        'Houston Rockets': 'Houston', 'Indiana Pacers': 'Indiana',
        'Los Angeles Clippers': 'LA Clippers',
        'Los Angeles Lakers': 'LA Lakers',
        'Memphis Grizzlies': 'Memphis', 'Vancouver Grizzlies': 'Memphis',
        'Miami Heat': 'Miami', 'Milwaukee Bucks': 'Milwaukee',
        'Minnesota Timberwolves': 'Minnesota',
        'New Orleans Pelicans': 'New Orleans',
        'New Orleans Hornets': 'New Orleans',
        'New York Knicks': 'New York',
        'Oklahoma City Thunder': 'Oklahoma City',
        'Orlando Magic': 'Orlando', 'Philadelphia 76ers': 'Philadelphia',
        'Phoenix Suns': 'Phoenix', 'Portland Trail Blazers': 'Portland',
        'Sacramento Kings': 'Sacramento', 'San Antonio Spurs': 'San Antonio',
        'Toronto Raptors': 'Toronto', 'Utah Jazz': 'Utah',
        'Washington Wizards': 'Washington',
        'Washington Bullets': 'Washington',
        'Seattle SuperSonics': 'Oklahoma City',
    }
    nba_wins['team'] = nba_wins['team'].replace(name_map)
    nba_wins = nba_wins[nba_wins['season'] >= 1990]
    nba_wins = (nba_wins.sort_values('wins', ascending=False)
                .drop_duplicates(subset=['team', 'season'])
                .sort_values(['team', 'season']))

    nba = pd.merge(nba_pay, nba_wins, on=['team', 'season'], how='inner')
    nba['league'] = 'NBA'
    nba['payroll_rank'] = nba.groupby('season')['payroll'].rank(ascending=False)

    # NFL
    nfl = pd.read_excel('NFL Salary By Position Group.xlsx')
    nfl['payroll'] = nfl['Offense'] + nfl['Defense']
    nfl = nfl[['Team', 'Season', 'payroll', 'W', 'W_PCT']].copy()
    nfl.columns = ['team', 'season', 'payroll', 'wins', 'win_pct']
    nfl['league'] = 'NFL'
    nfl['losses'] = 17 - nfl['wins']
    nfl['payroll_rank'] = nfl.groupby('season')['payroll'].rank(ascending=False)

    # MLB
    mlb = pd.read_csv('mlb_teams.csv')
    mlb[['season', 'team']] = mlb['TeamName'].str.split(' ', n=1, expand=True)
    mlb['season'] = mlb['season'].astype(int)
    mlb = mlb[['team', 'season', 'salary', 'W', 'L', 'W-L%']].copy()
    mlb.columns = ['team', 'season', 'payroll', 'wins', 'losses', 'win_pct']
    mlb['league'] = 'MLB'
    mlb['payroll_rank'] = mlb.groupby('season')['payroll'].rank(ascending=False)

    # Combine
    cols = ['team', 'season', 'payroll', 'wins', 'losses',
            'win_pct', 'league', 'payroll_rank']
    all_data = pd.concat([nba[cols], nfl[cols], mlb[cols]], ignore_index=True)
    return all_data


# ── Load data ─────────────────────────────────────────────
print("Loading data...")
all_data = load_data()
print(f"Data loaded: {len(all_data)} records across "
      f"{all_data['league'].nunique()} leagues")

# ── Team dropdown options ─────────────────────────────────
team_options = [
    {'label': f"{row['team']} ({row['league']})", 'value': row['team']}
    for _, row in all_data[['team', 'league']].drop_duplicates()
                  .sort_values(['league', 'team']).iterrows()
]

# ── AI context summary ────────────────────────────────────
data_summary = f"""
You are an expert sports analytics assistant. Answer questions about this
dataset concisely in 2-4 sentences. Be specific and reference actual numbers.

Dataset:
- NBA payroll + win% data 1990-2021 ({len(all_data[all_data['league']=='NBA'])} records)
- NFL payroll + win% data 2013-2022 ({len(all_data[all_data['league']=='NFL'])} records)
- MLB payroll + win% data 2018-2022 ({len(all_data[all_data['league']=='MLB'])} records)

Key findings:
- NBA: top payroll teams win 76% vs 27% for lowest spenders (strongest correlation)
- NFL: top payroll teams win 70% vs 34% (weaker — hard salary cap)
- MLB: top payroll teams win 69% vs 31% (moderate correlation)
- NBA has steepest regression slope — money matters most there
- NFL has flattest slope — salary cap promotes parity

Top 5 NBA payrolls:
{all_data[all_data['league']=='NBA'].nlargest(5,'payroll')[['team','season','payroll','win_pct']].to_string()}

Top 5 NFL payrolls:
{all_data[all_data['league']=='NFL'].nlargest(5,'payroll')[['team','season','payroll','win_pct']].to_string()}

Top 5 MLB payrolls:
{all_data[all_data['league']=='MLB'].nlargest(5,'payroll')[['team','season','payroll','win_pct']].to_string()}
"""

# ── App Layout ────────────────────────────────────────────
app = Dash(__name__)

app.layout = html.Div([

    html.H1("Does Money Buy Wins?",
            style={'textAlign': 'center', 'fontFamily': 'Arial',
                   'color': '#2c3e50', 'marginBottom': '5px',
                   'fontSize': '36px', 'fontWeight': 'bold'}),
    html.H3("Payroll vs Performance across NFL, NBA & MLB",
            style={'textAlign': 'center', 'fontFamily': 'Arial',
                   'color': '#7f8c8d', 'marginTop': '0px',
                   'fontWeight': 'normal'}),

    # ── Filters ───────────────────────────────────────────
    html.Div([
        html.Div([
            html.Label("Filter by League:",
                       style={'fontFamily': 'Arial', 'fontWeight': 'bold',
                              'fontSize': '13px'}),
            dcc.Checklist(
                id='league-filter',
                options=[{'label': '  NBA', 'value': 'NBA'},
                         {'label': '  NFL', 'value': 'NFL'},
                         {'label': '  MLB', 'value': 'MLB'}],
                value=['NBA', 'NFL', 'MLB'],
                inline=True,
                style={'fontFamily': 'Arial', 'fontSize': '14px',
                       'marginTop': '5px'}
            )
        ], style={'width': '25%', 'display': 'inline-block',
                  'verticalAlign': 'top', 'padding': '10px'}),

        html.Div([
            html.Label("Season Range:",
                       style={'fontFamily': 'Arial', 'fontWeight': 'bold',
                              'fontSize': '13px'}),
            dcc.RangeSlider(
                id='season-slider',
                min=int(all_data['season'].min()),
                max=int(all_data['season'].max()),
                step=1,
                value=[int(all_data['season'].min()),
                       int(all_data['season'].max())],
                marks={y: str(y) for y in range(
                    int(all_data['season'].min()),
                    int(all_data['season'].max()) + 1, 5)},
                tooltip={'placement': 'bottom', 'always_visible': False}
            )
        ], style={'width': '70%', 'display': 'inline-block',
                  'verticalAlign': 'top', 'padding': '10px'})
    ], style={'backgroundColor': '#f8f9fa', 'borderRadius': '8px',
              'margin': '10px 20px', 'padding': '5px'}),

    # ── View 1: Scatter ────────────────────────────────────
    html.Div([
        html.H4("View 1: Payroll Rank vs Win %",
                style={'fontFamily': 'Arial', 'color': '#2c3e50',
                       'marginLeft': '20px', 'marginBottom': '2px'}),
        html.P("Click any dot to see that team's history in View 2.",
               style={'fontFamily': 'Arial', 'color': '#7f8c8d',
                      'marginLeft': '20px', 'fontSize': '13px',
                      'marginTop': '0px'}),
        dcc.Graph(id='scatter-plot', style={'height': '420px'})
    ], style={'margin': '10px 20px', 'backgroundColor': 'white',
              'borderRadius': '8px',
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
              'paddingTop': '10px'}),

    # ── Views 2 & 3 side by side ───────────────────────────
    html.Div([
        html.Div([
            html.H4("View 2: Team Payroll & Win % Over Time",
                    style={'fontFamily': 'Arial', 'color': '#2c3e50',
                           'marginBottom': '6px'}),
            dcc.Dropdown(
                id='team-dropdown',
                options=team_options,
                value='LA Lakers',
                clearable=False,
                style={'fontFamily': 'Arial', 'fontSize': '13px',
                       'marginBottom': '8px'}
            ),
            dcc.Graph(id='time-series', style={'height': '350px'})
        ], style={'width': '55%', 'display': 'inline-block',
                  'verticalAlign': 'top', 'padding': '15px',
                  'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                  'boxSizing': 'border-box'}),

        html.Div([
            html.H4("View 3: Playoff Rate by Payroll Quintile",
                    style={'fontFamily': 'Arial', 'color': '#2c3e50',
                           'marginBottom': '2px'}),
            html.P("Higher spenders win more — but by how much?",
                   style={'fontFamily': 'Arial', 'color': '#7f8c8d',
                          'fontSize': '13px', 'marginTop': '0px'}),
            dcc.Graph(id='heatmap', style={'height': '380px'})
        ], style={'width': '43%', 'display': 'inline-block',
                  'verticalAlign': 'top', 'padding': '15px',
                  'marginLeft': '2%', 'backgroundColor': 'white',
                  'borderRadius': '8px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                  'boxSizing': 'border-box'})
    ], style={'margin': '10px 20px', 'display': 'flex',
              'flexDirection': 'row', 'alignItems': 'flex-start'}),

    # ── View 4: 3D Scatter ─────────────────────────────────
    html.Div([
        html.H4("View 4: 3D — Payroll Rank × Season × Win %",
                style={'fontFamily': 'Arial', 'color': '#2c3e50',
                       'marginLeft': '20px', 'marginBottom': '2px'}),
        html.P("Rotate to explore how the payroll-performance relationship "
               "evolved over time. Each dot is one team-season. "
               "Drag to rotate, scroll to zoom.",
               style={'fontFamily': 'Arial', 'color': '#7f8c8d',
                      'marginLeft': '20px', 'fontSize': '13px',
                      'marginTop': '0px'}),
        dcc.Graph(id='scatter-3d', style={'height': '600px'})
    ], style={'margin': '10px 20px', 'backgroundColor': 'white',
              'borderRadius': '8px',
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
              'paddingTop': '10px'}),

    # ── View 5: AI Chat ────────────────────────────────────
    html.Div([
        html.H4("🤖 Ask AI About the Data",
                style={'fontFamily': 'Arial', 'color': '#2c3e50',
                       'marginBottom': '4px'}),
        html.P("Powered by Llama 3 via Groq. Ask anything about payroll, "
               "performance, or team history.",
               style={'fontFamily': 'Arial', 'color': '#7f8c8d',
                      'fontSize': '13px', 'marginTop': '0px',
                      'marginBottom': '10px'}),
        html.Div([
            html.Span("Try asking: ",
                      style={'fontFamily': 'Arial', 'fontSize': '12px',
                             'color': '#7f8c8d', 'marginRight': '5px'}),
            html.Button("Which league benefits most from spending?",
                        id='q1', n_clicks=0,
                        style={'margin': '3px', 'padding': '5px 10px',
                               'fontSize': '11px', 'cursor': 'pointer',
                               'backgroundColor': '#eaf2fb',
                               'border': '1px solid #1170AA',
                               'borderRadius': '12px', 'color': '#1170AA'}),
            html.Button("Which team gets best value for money?",
                        id='q2', n_clicks=0,
                        style={'margin': '3px', 'padding': '5px 10px',
                               'fontSize': '11px', 'cursor': 'pointer',
                               'backgroundColor': '#eaf2fb',
                               'border': '1px solid #1170AA',
                               'borderRadius': '12px', 'color': '#1170AA'}),
            html.Button("Does the NFL salary cap make competition more equal?",
                        id='q3', n_clicks=0,
                        style={'margin': '3px', 'padding': '5px 10px',
                               'fontSize': '11px', 'cursor': 'pointer',
                               'backgroundColor': '#eaf2fb',
                               'border': '1px solid #1170AA',
                               'borderRadius': '12px', 'color': '#1170AA'}),
        ], style={'marginBottom': '12px'}),
        html.Div([
            dcc.Input(
                id='ai-input', type='text', n_submit=0,
                placeholder='Type your question here...',
                debounce=False,
                style={'width': '78%', 'padding': '10px',
                       'fontSize': '14px', 'fontFamily': 'Arial',
                       'border': '1.5px solid #ddd', 'borderRadius': '6px',
                       'marginRight': '1%', 'outline': 'none'}
            ),
            html.Button('Ask', id='ai-submit', n_clicks=0,
                        style={'width': '20%', 'padding': '10px',
                               'backgroundColor': '#1170AA', 'color': 'white',
                               'border': 'none', 'borderRadius': '6px',
                               'fontSize': '14px', 'cursor': 'pointer',
                               'fontFamily': 'Arial', 'fontWeight': 'bold'})
        ], style={'display': 'flex', 'marginBottom': '12px',
                  'alignItems': 'center'}),
        html.Div(id='ai-output',
                 children="Your answer will appear here...",
                 style={'backgroundColor': '#f8f9fa', 'padding': '15px',
                        'borderRadius': '6px', 'fontFamily': 'Arial',
                        'fontSize': '14px', 'color': '#2c3e50',
                        'minHeight': '80px', 'lineHeight': '1.8',
                        'border': '1px solid #e0e0e0',
                        'whiteSpace': 'pre-wrap'})
    ], style={'margin': '10px 20px', 'backgroundColor': 'white',
              'borderRadius': '8px',
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
              'padding': '20px', 'marginBottom': '30px'})

], style={'backgroundColor': '#f0f2f5', 'minHeight': '100vh',
          'padding': '20px'})


# ── Callbacks ─────────────────────────────────────────────

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('league-filter', 'value'),
    Input('season-slider', 'value')
)
def update_scatter(leagues, season_range):
    filtered = all_data[
        (all_data['league'].isin(leagues)) &
        (all_data['season'] >= season_range[0]) &
        (all_data['season'] <= season_range[1])
    ].copy()
    fig = px.scatter(
        filtered, x='payroll_rank', y='win_pct', color='league',
        hover_name='team',
        hover_data={'season': True, 'payroll': ':,.0f',
                    'wins': True, 'league': False},
        trendline='ols', color_discrete_map=COLORS,
        labels={'payroll_rank': 'Payroll Rank (1 = Highest Spender)',
                'win_pct': 'Win Percentage', 'league': 'League'},
        opacity=0.65
    )
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        legend=dict(orientation='h', y=-0.15),
        margin=dict(l=50, r=20, t=20, b=80)
    )
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    return fig


@app.callback(
    Output('team-dropdown', 'value'),
    Input('scatter-plot', 'clickData'),
    Input('team-dropdown', 'value')
)
def update_dropdown_from_click(clickData, current_team):
    if clickData is None:
        return current_team
    point = clickData['points'][0]
    if 'hovertext' in point and point['hovertext']:
        clicked_team = point['hovertext']
        if clicked_team in all_data['team'].values:
            return clicked_team
    return current_team


@app.callback(
    Output('time-series', 'figure'),
    Input('team-dropdown', 'value')
)
def update_timeseries(team):
    if not team:
        raise PreventUpdate
    team_data = all_data[all_data['team'] == team].sort_values('season')
    if len(team_data) == 0:
        fig = go.Figure()
        fig.update_layout(title=f"No data for: {team}",
                          plot_bgcolor='white', paper_bgcolor='white')
        return fig
    league = team_data['league'].values[0]
    color = COLORS.get(league, '#1170AA')
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=team_data['season'], y=team_data['win_pct'],
        name='Win %', mode='lines+markers',
        line=dict(color=color, width=2.5), marker=dict(size=7)
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=team_data['season'], y=team_data['payroll'],
        name='Payroll ($)', mode='lines+markers',
        line=dict(color='gray', width=2, dash='dash'), marker=dict(size=5)
    ), secondary_y=True)
    fig.update_layout(
        title=f"{team} ({league})", plot_bgcolor='white',
        paper_bgcolor='white', font=dict(family='Arial', size=11),
        hovermode='x unified', legend=dict(orientation='h', y=-0.2),
        margin=dict(l=50, r=60, t=40, b=80)
    )
    fig.update_xaxes(title_text='Season', showgrid=True,
                     gridcolor='lightgray')
    fig.update_yaxes(title_text='Win %', secondary_y=False,
                     showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(title_text='Payroll ($)', secondary_y=True)
    return fig


@app.callback(
    Output('heatmap', 'figure'),
    Input('league-filter', 'value'),
    Input('season-slider', 'value')
)
def update_heatmap(leagues, season_range):
    filtered = all_data[
        (all_data['league'].isin(leagues)) &
        (all_data['season'] >= season_range[0]) &
        (all_data['season'] <= season_range[1])
    ].copy()
    filtered['payroll_quintile'] = pd.qcut(
        filtered['payroll_rank'], q=5,
        labels=['Q1 (Highest)', 'Q2', 'Q3', 'Q4', 'Q5 (Lowest)'],
        duplicates='drop'
    )
    filtered['made_playoffs'] = (filtered['win_pct'] >= 0.5).astype(int)
    hmap = (filtered.groupby(['league', 'payroll_quintile'], observed=True)
            ['made_playoffs'].mean().reset_index())
    hmap.columns = ['league', 'payroll_quintile', 'playoff_rate']
    hmap['payroll_quintile'] = hmap['payroll_quintile'].astype(str)
    pivot = hmap.pivot(index='league', columns='payroll_quintile',
                       values='playoff_rate')
    col_order = [c for c in
                 ['Q1 (Highest)', 'Q2', 'Q3', 'Q4', 'Q5 (Lowest)']
                 if c in pivot.columns]
    pivot = pivot[col_order]
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale='Blues', showscale=False,
        text=[[f"{v:.0%}" if not pd.isna(v) else "" for v in row]
              for row in pivot.values],
        texttemplate="%{text}", textfont={"size": 14}, hoverongaps=False
    ))
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=11),
        margin=dict(l=50, r=20, t=20, b=80),
        xaxis_title='Payroll Quintile (Q1 = Highest Spend)',
        yaxis_title='League'
    )
    return fig


@app.callback(
    Output('scatter-3d', 'figure'),
    Input('league-filter', 'value'),
    Input('season-slider', 'value')
)
def update_3d(leagues, season_range):
    filtered = all_data[
        (all_data['league'].isin(leagues)) &
        (all_data['season'] >= season_range[0]) &
        (all_data['season'] <= season_range[1])
    ].copy()
    fig = px.scatter_3d(
        filtered, x='payroll_rank', y='season', z='win_pct',
        color='league', hover_name='team',
        hover_data={'payroll': ':,.0f', 'wins': True},
        color_discrete_map=COLORS, opacity=0.7,
        labels={'payroll_rank': 'Payroll Rank', 'season': 'Season',
                'win_pct': 'Win %', 'league': 'League'}
    )
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(
        font=dict(family='Arial', size=11),
        scene=dict(
            xaxis_title='Payroll Rank (1=Highest)',
            yaxis_title='Season', zaxis_title='Win %',
            camera=dict(eye=dict(x=1.8, y=1.8, z=0.8)),
            xaxis=dict(backgroundcolor='#f0f4f8', gridcolor='lightgray',
                       showbackground=True),
            yaxis=dict(backgroundcolor='#f8f9fa', gridcolor='lightgray',
                       showbackground=True),
            zaxis=dict(backgroundcolor='#eaf2fb', gridcolor='lightgray',
                       showbackground=True),
        ),
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation='h', y=-0.05),
        paper_bgcolor='white'
    )
    return fig


@app.callback(
    Output('ai-output', 'children'),
    Output('ai-input', 'value'),
    Input('ai-submit', 'n_clicks'),
    Input('q1', 'n_clicks'),
    Input('q2', 'n_clicks'),
    Input('q3', 'n_clicks'),
    Input('ai-input', 'n_submit'),
    State('ai-input', 'value'),
    prevent_initial_call=True
)
def ask_ai(submit_clicks, q1_clicks, q2_clicks, q3_clicks,
           n_submit, user_input):
    from dash import callback_context
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'q1':
        question = "Which league benefits most from spending more money on players?"
    elif trigger == 'q2':
        question = ("Which team gets the best value for money — "
                    "highest wins relative to their payroll rank?")
    elif trigger == 'q3':
        question = ("Does the NFL salary cap make competition more equal "
                    "compared to MLB and NBA?")
    else:
        question = user_input
        if not question or not question.strip():
            return "Please type a question first!", ""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": data_summary},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 300,
                "temperature": 0.5
            },
            timeout=30
        )
        result = response.json()
        if 'choices' in result:
            answer = result['choices'][0]['message']['content']
        else:
            answer = (f"Error: {result.get('error', {}).get('message', 'Unknown error')}")
    except Exception as e:
        answer = f"Error: {str(e)}"

    return answer, ""


# ── Run ───────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, port=8050)
