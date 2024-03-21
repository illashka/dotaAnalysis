import pandas as pd
import streamlit as st
import mysql.connector
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import requests

players_url = "https://api.opendota.com/api/proPlayers"
teams_url   = 'https://api.opendota.com/api/teams'
heroes_url  = 'https://api.opendota.com/api/heroStats'

players_data_response = requests.get(players_url)
teams_data_response   = requests.get(teams_url)
heroes_data_response  = requests.get(teams_url)

df        = pd.DataFrame(players_data_response.json())
df_heroes = pd.DataFrame(teams_data_response.json())
df_teams  = pd.DataFrame(heroes_data_response.json())

# df.drop(columns = ['avatar', 'avatarmedium','avatarfull',
#                   'profileurl', 'cheese', 'country_code', 'locked_until'], axis=1, inplace=True)
# df_heroes.drop(columns = ['img', 'name', 'icon','base_mr',
#                   'base_str','base_agi','base_int','str_gain', 'agi_gain',
#                   'int_gain','projectile_speed',
#                   'turn_rate','cm_enabled','legs','turbo_picks', 'turbo_picks_trend',
#                   'turbo_wins', 'turbo_wins_trend',
#                   'pub_pick_trend','pub_win_trend'], axis=1, inplace=True)
# df_teams.drop(columns = ['logo_url'], axis=1, inplace=True)

def dota_page():
    st.write("Dota here")

    def df_output():
        with st.expander("Table"):
            showData=st.multiselect('Columns: ', df.columns, default=['name', 'fantasy_role', 'team_name', 'loccountrycode'])
            st.write(df[showData])
    df_output()

    # Подсчет проф игроков по странам
    players = df
    players['loccountrycode'] = players['loccountrycode'].replace({
    'US': 'USA', 'DE': 'DEU', 'GR': 'GRC', 'SE': 'SWE', 'SG': 'SGP', 'KZ': 'KAZ', 'CZ': 'CZE', 'RU': 'RUS', 
    'BR': 'BRA', 'IL': 'ISR', 'AR': 'ARG', 'LB': 'LBN', 'UA': 'UKR', 'NL': 'NLD', 'PK': 'PAK', 'JP': 'JPN', 
    'UG': 'UGA', 'BY': 'BLR', 'FI': 'FIN', 'AF': 'AFG', 'DK': 'DNK', 'BA': 'BIH', 'SK': 'SVK', 'GB': 'GBR', 
    'ZA': 'ZAF', 'MY': 'MYS', 'AG': 'ATG', 'CA': 'CAN', 'QA': 'QAT', 'CN': 'CHN', 'PH': 'PHL', 'GE': 'GEO', 
    'PT': 'PRT', 'ID': 'IDN', 'AU': 'AUS', 'VN': 'VNM', 'KR': 'KOR', 'PE': 'PER', 'EE': 'EST', 'CO': 'COL', 
    'SV': 'SLV', 'BO': 'BOL', 'VI': 'VIR', 'FR': 'FRA', 'PL': 'POL', 'MN': 'MNG', 'KG': 'KGZ', 'LA': 'LAO', 
    'IS': 'ISL', 'CH': 'CHE', 'YE': 'YEM', 'IN': 'IND', 'ER': 'ERI', 'RS': 'SRB', 'MX': 'MEX', 'NO': 'NOR', 
    'TR': 'TUR'
    })
    count_of_players = players.groupby('loccountrycode').count()
    count_of_players = count_of_players['account_id']
    countries = {
    'country_code': list(count_of_players.index),
    'players_count': list(count_of_players)
    }
    countries = pd.DataFrame(countries)
    
    # Топ 10 побеждающих/проигрывающих героев
    heroes = df_heroes
    heroes['win_percent'] = heroes['pro_win'] / heroes['pro_pick'] * 100
    hero_win = heroes[['localized_name','win_percent']]
    hero_win = hero_win.sort_values(by=['win_percent'], ascending=False)
    hero_win = hero_win.head(10)
    hero_lose = heroes[['localized_name','win_percent']]
    hero_lose = hero_lose.sort_values(by=['win_percent'], ascending=True)
    hero_lose = hero_lose.head(10)


    # Проценты побед команд
    teams = df_teams
    teams_500 = teams.loc[(teams['wins'] + teams['losses'] > 500)]
    teams_500['games'] = teams_500['wins'] + teams_500['losses']
    teams_500['win_percent'] = teams_500['wins'] * 100 / teams_500['games']
    teams_percents = teams_500[['name', 'win_percent']]
    teams_percents = teams_percents.sort_values(by='win_percent', ascending=False)
    teams_percents = teams_percents[5:]
    teams_percents = teams_percents.drop([88, 145])

    def plots():
        # Распределение профессиональных дотеров по странам
        fig_players_by_country = px.choropleth(countries, 
                    locations='country_code',
                    color="players_count",
                    hover_name="country_code",
                    color_continuous_scale=px.colors.sequential.Viridis,
                    projection="natural earth",
                    title = 'Профессиональные игроки, играющие в доту')
        fig_players_by_country.update_layout(
            plot_bgcolor="rgb(0,0,0,0)",
            xaxis=(dict(showgrid=False)))
        st.plotly_chart(fig_players_by_country, use_container_width=True)
        
        # Побеждающие/Проигрывающие герои
        winners_plot = px.bar(
            hero_win,
            x='localized_name',
            y='win_percent',
            title="Топ-10 наиболее часто побеждающих героев",
            labels={'localized_name':'Имя героя', 'win_percent':'Победы, %'}
        )
        losers_plot = px.bar(
            hero_lose,
            x='localized_name',
            y='win_percent',
            title="Топ-10 наиболее часто проигрывающих героев",
            labels={'localized_name':'Имя героя', 'win_percent':'Победы, %'}
        )
        winners_plot.update_traces(marker_color='green')
        losers_plot.update_traces(marker_color='red')
        left,right=st.columns(2)
        left.plotly_chart(winners_plot, use_container_width=True)
        right.plotly_chart(losers_plot, use_container_width=True)

        # Побеждающие команды
        win_teams_plot = px.bar(
            teams_percents,
            x='name',
            y='win_percent',
            title="Процент побед команд, имеющих более 500 сыгранных матчей",
            labels={'name': 'Название команды', 'win_percent': 'Победы, %'}
        )
        win_teams_plot.update_traces(marker_color='purple')
        st.plotly_chart(win_teams_plot, use_container_width=True)


    plots()
