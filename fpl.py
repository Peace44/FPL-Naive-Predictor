import math
import os
import sys
import numpy as np
from numpy import float64
from numpy import power as pow
import requests
import pandas as pd
import time
from collections import defaultdict

general_info_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
fixtures_url = "https://fantasy.premierleague.com/api/fixtures/"
upcoming_fixtures_url = "https://fantasy.premierleague.com/api/fixtures/?future=1"

response = requests.get(general_info_url)
general_info_data = response.json()

teams = general_info_data['teams']
positions = general_info_data['element_types']
players = general_info_data['elements']

teams_dict = {team['id']:team['short_name'] for team in teams}
positions_dict = {position['id']:position['singular_name_short'] for position in positions}
players_dict = {player['id']:player for player in players}



# print(teams_dict)
# print('\n\n\n')
# print(positions_dict)
# print('\n\n\n')
# print(players_dict)
# print('\n\n\n')
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
response = requests.get(fixtures_url)
fixtures_data = response.json()

matches_played_dict = {}
goals_for_dict = {}
goals_against_dict = {}
clean_sheets_dict= {}
for fixture in fixtures_data:
    if not fixture["finished"]:
        continue;

    home_team = teams_dict[fixture["team_h"]]
    away_team = teams_dict[fixture["team_a"]]

    home_team_score = fixture["team_h_score"]
    away_team_score = fixture["team_a_score"]
    
    if home_team not in matches_played_dict:
        matches_played_dict[home_team] = 0
        goals_for_dict[home_team] = 0
        goals_against_dict[home_team] = 0
        clean_sheets_dict[home_team] = 0

    matches_played_dict[home_team] += 1
    goals_for_dict[home_team] += home_team_score
    goals_against_dict[home_team] += away_team_score

    if away_team_score == 0:
        clean_sheets_dict[home_team] += 1

    if away_team not in matches_played_dict:
        matches_played_dict[away_team] = 0
        goals_for_dict[away_team] = 0
        goals_against_dict[away_team] = 0
        clean_sheets_dict[away_team] = 0
        
    matches_played_dict[away_team] += 1
    goals_for_dict[away_team] += away_team_score
    goals_against_dict[away_team] += home_team_score

    if home_team_score == 0:
        clean_sheets_dict[away_team] += 1

# print(matches_played_dict)
# print()
# print(goals_for_dict)
# print()
# print(goals_against_dict)
# print()
# print(clean_sheets_dict)
# print()
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
response = requests.get(upcoming_fixtures_url)
upcoming_fixtures_data = response.json()

nxtGW = upcoming_fixtures_data[0]["event"]

prvGWsPtsTrendAvailability = False
if input(f"Do you have previous gameweeks (nxtGWs)PtsTrends ('vvv', 'vv', 'v', '~', '^^^', '^^', '^') data [Y/n]?   ").lower()[0] == 'y':
    prvGWsPtsTrendAvailability = True

if prvGWsPtsTrendAvailability:
    print("\nWhat's the DATETIME from which the data can be fetched from?")
    day = int(input("Provide the day value (1 to 31): "))
    month = int(input("Provide the month value (1 to 12): "))
    year = int(input("Provide the year value: "))
    hour = int(input("Provide the hour value (0 to 23): "))
    minute = int(input("Provide the minute value (0 to 59): "))

    timestr = "%02d'%02d'%4d-%02d:%02d" %(day, month, year, hour, minute)
    prvGWsPtsTrend_file = "data/" + timestr + "/players_stats.csv"

    try:
        prvGWsPtsTrend_df = pd.read_csv(prvGWsPtsTrend_file)[['id', 'nxtGWsPtsTrend']].set_index('id', drop=False)
        prvGWsPtsTrend_dict = prvGWsPtsTrend_df.to_dict()['nxtGWsPtsTrend']
    except Exception as e:
        print(f"\n{e}\n")
        prvGWsPtsTrendAvailability = False



# print('\n\n\n')
# print(prvGWsPtsTrend_dict)
# print('\n\n\n')
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
players_stats = []
for player in players:
    player_dict = {}
    player_dict['id'] = player['id']
    player_dict['1st_name'] = player['first_name']
    player_dict['2nd_name'] = player['second_name']
    player_dict['position'] = positions_dict[player['element_type']] 
    player_dict['team'] = teams_dict[player['team']]  
    player_dict['tot_pts'] = player['total_points']
    if prvGWsPtsTrendAvailability:
        player_dict['prvGWsPtsTrend'] = prvGWsPtsTrend_dict.get(player_dict['id'], '?')
    else:
        player_dict['prvGWsPtsTrend'] = '?'
    player_dict['web_name'] = player['web_name'] + f" ({player_dict['position']}, {player_dict['prvGWsPtsTrend']})"
    player_dict['pts/game'] = float64(player['points_per_game'])
    player_dict['form'] = float64(player['form'])
    # player_dict['xPts'] = round((2/3)*player_dict['pts/game'] + (1/3)*player_dict['form'], 5)   # [2/3 and 1/3 approximate f and (1-f) to 1 decimal ==> f = (g-1) and g = golden_ratio ~ 0.618]
    player_dict['xPts'] = round((1/2)*player_dict['pts/game'] + (1/2)*player_dict['form'], 5) # for a player form is as important as pts/game, for a team fpl_pts/match is more important!
    players_stats.append(player_dict)

players_df = pd.DataFrame(players_stats).set_index('id', drop=False)
players_df = players_df.sort_values(['team', 'form', 'xPts', 'tot_pts'], ascending=[True, False, False, False]) # 'form' gives you info on which players might be currently <appearing>/<playing well> or not

# print(players_df.head(20))
# print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
fpl_teams_stats_df = players_df.groupby('team').sum(numeric_only=True).reset_index().drop(columns=['id', 'pts/game', 'xPts'], axis='columns').rename(columns={'tot_pts':'fpl_pts','form':'fpl_form'})
fpl_teams_stats_df.insert(1, 'matches_played', fpl_teams_stats_df['team'].map(matches_played_dict))
fpl_teams_stats_df.insert(3, 'fpl_pts/match', round(fpl_teams_stats_df['fpl_pts'] / fpl_teams_stats_df['matches_played'], 5))
fpl_teams_stats_df['fpl_xPts'] = round(.618*fpl_teams_stats_df['fpl_pts/match'] + .382*fpl_teams_stats_df['fpl_form'], 5) # for a team fpl_form is less important than fpl_pts/match!

defensive_players = players_df[(players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')] # gkps and defs
attacking_players = players_df[(players_df['position'] == 'MID') | (players_df['position'] == 'FWD')] # mids and fwds

fpl_teams_stats_df['def_pts'] = defensive_players.groupby('team').sum(numeric_only=True).reset_index()['tot_pts']
fpl_teams_stats_df['def_pts/match'] = round(fpl_teams_stats_df['def_pts'] / fpl_teams_stats_df['matches_played'], 5)
fpl_teams_stats_df['def_form'] = defensive_players.groupby('team').sum(numeric_only=True).reset_index()['form']
fpl_teams_stats_df['def_xPts'] = round(.618*fpl_teams_stats_df['def_pts/match'] + .382*fpl_teams_stats_df['def_form'], 5)

fpl_teams_stats_df['att_pts'] = attacking_players.groupby('team').sum(numeric_only=True).reset_index()['tot_pts']
fpl_teams_stats_df['att_pts/match'] = round(fpl_teams_stats_df['att_pts'] / fpl_teams_stats_df['matches_played'], 5)
fpl_teams_stats_df['att_form'] = attacking_players.groupby('team').sum(numeric_only=True).reset_index()['form']
fpl_teams_stats_df['att_xPts'] = round(.618*fpl_teams_stats_df['att_pts/match'] + .382*fpl_teams_stats_df['att_form'], 5)

fpl_teams_stats_df['goals_for'] = fpl_teams_stats_df['team'].map(goals_for_dict)
fpl_teams_stats_df['avg_GF/match'] = round(fpl_teams_stats_df['goals_for'] / fpl_teams_stats_df['matches_played'], 5)

fpl_teams_stats_df['goals_against'] = fpl_teams_stats_df['team'].map(goals_against_dict)
fpl_teams_stats_df['avg_GA/match'] = round(fpl_teams_stats_df['goals_against'] / fpl_teams_stats_df['matches_played'], 5)

fpl_teams_stats_df['clean_sheets'] = fpl_teams_stats_df['team'].map(clean_sheets_dict)
fpl_teams_stats_df['avg_CS/match'] = round(fpl_teams_stats_df['clean_sheets'] / fpl_teams_stats_df['matches_played'], 5)

fpl_teams_stats_df = fpl_teams_stats_df.sort_values(['fpl_xPts','fpl_pts/match','fpl_pts'], ascending=[False,False,False]).reset_index(drop=True)

fpl_teams_stats_df.insert(0, 'fpl_rank', 1 + fpl_teams_stats_df['team'].index)
fpl_teams_stats_df.insert(1, 'fpl_tier', 1 + fpl_teams_stats_df['team'].index//2)
fpl_teams_stats_df = fpl_teams_stats_df.set_index('team', drop=False)

# print(fpl_teams_stats_df)
# print("\n\n\n")
#####################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
def_df = fpl_teams_stats_df[['def_xPts', 'avg_GA/match']]
att_df = fpl_teams_stats_df[['att_xPts', 'avg_GF/match']]

def_df.insert(2, 'def_xPts / ^avg_GA/match', def_df['def_xPts'] / (def_df['avg_GA/match']/def_df['avg_GA/match'].max()))
att_df.insert(2, 'att_xPts * ^avg_GF/match', att_df['att_xPts'] * (att_df['avg_GF/match']/att_df['avg_GF/match'].max()))

def_teams_stats_df = def_df.sort_values('def_xPts / ^avg_GA/match', ascending=False).reset_index(drop=False)
att_teams_stats_df = att_df.sort_values('att_xPts * ^avg_GF/match', ascending=False).reset_index(drop=False)

def_teams_stats_df.insert(0, 'def_rank', 1 + def_teams_stats_df['team'].index)
def_teams_stats_df.insert(1, 'def_tier', 1 + def_teams_stats_df['team'].index//2)

att_teams_stats_df.insert(0, 'att_rank', 1 + att_teams_stats_df['team'].index)
att_teams_stats_df.insert(1, 'att_tier', 1 + att_teams_stats_df['team'].index//2)

def_teams_stats_df = def_teams_stats_df.set_index('team', drop=False)
att_teams_stats_df = att_teams_stats_df.set_index('team', drop=False)

# print(def_teams_stats_df)
# print("\n\n\n")
# print(att_teams_stats_df)
# print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
print(f"\n\n\nThe next gameweek is GW{nxtGW}\n")

gws = []

if input(f"Do you want to simulate a particular gameweek?\nAnswer 'no' if you want to simulate in advance many contiguous gameweeks starting from the next.\n[Y/n]?   ").lower()[0] == 'y':
    gwToSimulate = int(input(f"\nWhich one? Enter a number in the range [1, 38]:    ")) # int(input(f"\nWhich one? Enter a number in the range [{nxtGW}, 38]:    "))
    gws.append(gwToSimulate)
else:
    nberOfGWsInAdvance = int(input(f"\nHow many gameweeks do you want to simulate in advance (1, 2, 3, or 4)?   "))
    if nberOfGWsInAdvance not in [1, 2, 3, 4]:
        sys.exit("\n\n\n    !Bye-\n-Bye!\n\n\n")

    gws.append(nxtGW) 

    if nberOfGWsInAdvance >= 2:
        gws.append(nxtGW + 1)
    if nberOfGWsInAdvance >= 3:
        gws.append(nxtGW + 2)
    if nberOfGWsInAdvance == 4:
        gws.append(nxtGW + 3)

nxtGWs_fixtures = []
fpl_teamsAdv_dict = {}
def_teamsAdv_dict = {}
att_teamsAdv_dict = {}
teams_nxtGWsNberOfMatches_dict = {}

# players_df.loc[(players_df['pts/game'] <= 0) | (players_df['form'] <= 0) | (players_df['xPts'] < 0), 'xPts'] = 0
players_df['^fplAdv*xPts'] = 0 ### ^fplAdv is the normalized fplAdv (to [0,1]) ###
players_df['^defAdv*xPts'] = 0 ### ^defAdv is the normalized defAdv (to [0,1]) ###
players_df['^attAdv*xPts'] = 0 ### ^attAdv is the normalized attAdv (to [0,1]) ###
players_df['^avgAdv*xPts'] = 0 ### ^avgAdv is the normalized avgAdv (to [0,1]) ###

for fixture in fixtures_data: # for fixture in upcoming_fixtures_data
    if fixture["event"] in gws:
        fixture_dict = {}

        home_team = teams_dict[fixture['team_h']]
        away_team = teams_dict[fixture['team_a']]
        
        fixture_dict['home_attAdv'] = def_teams_stats_df.loc[away_team, 'def_tier'] - att_teams_stats_df.loc[home_team, 'att_tier']
        fixture_dict['home_defAdv'] = att_teams_stats_df.loc[away_team, 'att_tier'] - def_teams_stats_df.loc[home_team, 'def_tier'] 
        fixture_dict['home_fplAdv'] = fpl_teams_stats_df.loc[away_team, 'fpl_tier'] - fpl_teams_stats_df.loc[home_team, 'fpl_tier']
        
        fixture_dict['home_team'] = home_team
        fixture_dict['away_team'] = away_team
        
        fixture_dict['away_fplAdv'] = -fixture_dict['home_fplAdv']
        fixture_dict['away_defAdv'] = -fixture_dict['home_attAdv']
        fixture_dict['away_attAdv'] = -fixture_dict['home_defAdv']
        
        nxtGWs_fixtures.append(fixture_dict)

        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        fpl_teamsAdv_dict[home_team] = fpl_teamsAdv_dict.get(home_team, 0) + fixture_dict['home_fplAdv']
        fpl_teamsAdv_dict[away_team] = fpl_teamsAdv_dict.get(away_team, 0) + fixture_dict['away_fplAdv']        
        
        players_df.loc[players_df['team'] == home_team, '^fplAdv*xPts'] += ((9 + fixture_dict['home_fplAdv']) / 18) * players_df['xPts']
        players_df.loc[players_df['team'] == away_team, '^fplAdv*xPts'] += ((9 + fixture_dict['away_fplAdv']) / 18) * players_df['xPts']
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        def_teamsAdv_dict[home_team] = def_teamsAdv_dict.get(home_team, 0) + fixture_dict['home_defAdv']
        def_teamsAdv_dict[away_team] = def_teamsAdv_dict.get(away_team, 0) + fixture_dict['away_defAdv']
        
        players_df.loc[((players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')) & (players_df['team'] == home_team), '^defAdv*xPts'] += ((9 + fixture_dict['home_defAdv']) / 18) * players_df['xPts']
        players_df.loc[((players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')) & (players_df['team'] == away_team), '^defAdv*xPts'] += ((9 + fixture_dict['away_defAdv']) / 18) * players_df['xPts']
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        att_teamsAdv_dict[home_team] = att_teamsAdv_dict.get(home_team, 0) + fixture_dict['home_attAdv']
        att_teamsAdv_dict[away_team] = att_teamsAdv_dict.get(away_team, 0) + fixture_dict['away_attAdv']
        
        players_df.loc[((players_df['position'] == 'MID') | (players_df['position'] == 'FWD')) & (players_df['team'] == home_team), '^attAdv*xPts'] += ((9 + fixture_dict['home_attAdv']) / 18) * players_df['xPts']
        players_df.loc[((players_df['position'] == 'MID') | (players_df['position'] == 'FWD')) & (players_df['team'] == away_team), '^attAdv*xPts'] += ((9 + fixture_dict['away_attAdv']) / 18) * players_df['xPts']
        #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        teams_nxtGWsNberOfMatches_dict[home_team] = teams_nxtGWsNberOfMatches_dict.get(home_team, 0) + 1
        teams_nxtGWsNberOfMatches_dict[away_team] = teams_nxtGWsNberOfMatches_dict.get(away_team, 0) + 1



nxtGWs_fixtures_df = pd.DataFrame(nxtGWs_fixtures)
players_df['^avgAdv*xPts'] = round((players_df['^fplAdv*xPts'] + players_df['^defAdv*xPts'] + players_df['^attAdv*xPts']) / 2, 5)



fpl_teams_stats_df = fpl_teams_stats_df[['fpl_rank', 'fpl_tier', 'team', 'fpl_pts/match', 'fpl_form', 'fpl_xPts']] ###> comment this line to make fpl_teams_stats_df more detailed!

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
fpl_teams_stats_df['fplAdv_nxtGWs'] = fpl_teams_stats_df['team'].map(fpl_teamsAdv_dict)
fpl_teams_stats_df = fpl_teams_stats_df.sort_values(['fplAdv_nxtGWs','fpl_rank'], ascending=[False,True])

players_df['fplAdv_nxtGWs'] = players_df['team'].map(fpl_teamsAdv_dict)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def_teams_stats_df['defAdv_nxtGWs'] = def_teams_stats_df['team'].map(def_teamsAdv_dict)
def_teams_stats_df = def_teams_stats_df.sort_values(['defAdv_nxtGWs','def_rank'], ascending=[False,True])

players_df['defAdv_nxtGWs'] = players_df['team'].map(def_teamsAdv_dict)
players_df.loc[((players_df['position'] == 'MID') | (players_df['position'] == 'FWD')), 'defAdv_nxtGWs'] = 0
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
att_teams_stats_df['attAdv_nxtGWs'] = att_teams_stats_df['team'].map(att_teamsAdv_dict)
att_teams_stats_df = att_teams_stats_df.sort_values(['attAdv_nxtGWs','att_rank'], ascending=[False,True])

players_df['attAdv_nxtGWs'] = players_df['team'].map(att_teamsAdv_dict)
players_df.loc[((players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')), 'attAdv_nxtGWs'] = 0
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



print("\n\n\n")
print(nxtGWs_fixtures_df.to_string(index=False))
print("\n\n\n")
print(fpl_teams_stats_df.to_string(index=False))
print("\n\n\n")
print(def_teams_stats_df.to_string(index=False))
print("\n\n\n")
print(att_teams_stats_df.to_string(index=False))
print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
avg_teams_stats_df = pd.DataFrame().assign(
    team = fpl_teams_stats_df['team'], 
    defAdv_nxtGWs = def_teams_stats_df['defAdv_nxtGWs'], 
    fplAdv_nxtGWs = fpl_teams_stats_df['fplAdv_nxtGWs'],
    attAdv_nxtGWs = att_teams_stats_df['attAdv_nxtGWs'],
    fpl_rank = fpl_teams_stats_df['fpl_rank'])

avg_teams_stats_df = avg_teams_stats_df.set_index('team')

avg_teams_stats_df['avgAdv_nxtGWs'] = round((avg_teams_stats_df['defAdv_nxtGWs'] + avg_teams_stats_df['fplAdv_nxtGWs'] + avg_teams_stats_df['attAdv_nxtGWs'])/3, 2)

avg_teams_stats_df = avg_teams_stats_df.sort_values(['avgAdv_nxtGWs','fplAdv_nxtGWs','fpl_rank'], ascending=[False,False,True]).reset_index(drop=False).drop(columns=['fpl_rank'])

avg_teams_stats_df.insert(0, 'avg_rank', 1 + avg_teams_stats_df['team'].index)
avg_teams_stats_df.insert(1, 'avg_tier', 1 + avg_teams_stats_df['team'].index//2)
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
avg_teams_advanced_stats_df = avg_teams_stats_df[['team', 'attAdv_nxtGWs', 'defAdv_nxtGWs']].set_index('team', drop=False)
avg_teams_advanced_stats_df.insert(0, 'att_rank', att_teams_stats_df['att_rank'])
avg_teams_advanced_stats_df.insert(1, 'def_rank', def_teams_stats_df['def_rank'])
avg_teams_advanced_stats_df.insert(2, 'diff=(def-att)_rank', avg_teams_advanced_stats_df['def_rank'] - avg_teams_advanced_stats_df['att_rank'])
avg_teams_advanced_stats_df.insert(4, 'att_xPts', att_teams_stats_df['att_xPts'])
avg_teams_advanced_stats_df.insert(5, 'def_xPts', def_teams_stats_df['def_xPts'])
avg_teams_advanced_stats_df.insert(6, 'avg_(att-def)_xPts/match', avg_teams_advanced_stats_df['att_xPts'] - avg_teams_advanced_stats_df['def_xPts'])
avg_teams_advanced_stats_df['delta=(att-def)Adv_nxtGWs'] = avg_teams_advanced_stats_df['attAdv_nxtGWs'] - avg_teams_advanced_stats_df['defAdv_nxtGWs']
avg_teams_advanced_stats_df['#OfMatches_nxtGWs'] = avg_teams_advanced_stats_df['team'].map(teams_nxtGWsNberOfMatches_dict)
avg_teams_advanced_stats_df['delta/#OfMatches_nxtGWs'] = round(avg_teams_advanced_stats_df['delta=(att-def)Adv_nxtGWs'] / avg_teams_advanced_stats_df['#OfMatches_nxtGWs'], 5)

avg_teams_advanced_stats_df = avg_teams_advanced_stats_df.sort_values(['delta/#OfMatches_nxtGWs', 'avg_(att-def)_xPts/match', 'diff=(def-att)_rank'], ascending=[True, True, True]) ### IS THE SORTING ORDER THE BEST? I THINK SO!!! IF NOT, INTERCHANGE 'diff...' AND 'avg_(att-def)...' ###

avg_teams_advanced_stats_df['#atts'] = pd.DataFrame([i for i in range(0,20)]).index // 5
avg_teams_advanced_stats_df['#defs'] = 3 - avg_teams_advanced_stats_df['#atts']



players_df['#OfMatches_nxtGWs'] = players_df['team'].map(teams_nxtGWsNberOfMatches_dict)
players_df['tot_xPts'] = round(players_df['#OfMatches_nxtGWs'] * players_df['xPts'], 5)
for gw in gws:
    players_df["gw" + str(gw) + "Pts"] = 0
players_df['tot_aPts'] = 0
players_df['tot_aPts/tot_xPts'] = 0
players_df['nxtGWsPtsTrend'] = '?'



print(avg_teams_stats_df.to_string(index=False))
print("\n\n\n")
print(avg_teams_advanced_stats_df.to_string(index=False))
print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
teams_top_fpl_players_dict = {}
teams_top_fpl_players_df = pd.DataFrame()
for team in fpl_teams_stats_df.index:
    team_top_fpl_players = players_df.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','fplAdv_nxtGWs','xPts','^fplAdv*xPts']].head(7).sort_values(['xPts','tot_pts'], ascending=[False,False]).head(5)   # prime nbers: 11 (max # of players from the same team in a real match) ==> [7 ==> 5] ==> 3 (max # of players from the same team in an fpl game)
    team_top_fpl_players = team_top_fpl_players.round(3)
    teams_top_fpl_players_df = pd.concat([teams_top_fpl_players_df, team_top_fpl_players])
    team_top_fpl_players = [' ==> '.join(i) for i in zip(team_top_fpl_players['web_name'], '(' + team_top_fpl_players['xPts'].map(str) + ', ' + team_top_fpl_players['^fplAdv*xPts'].map(str) + ')')]
    teams_top_fpl_players_dict[team] = team_top_fpl_players
fpl_matrix_df = pd.DataFrame(teams_top_fpl_players_dict).transpose()
fpl_matrix_df.index.name = 'team'
fpl_matrix_df.columns = ['fplPlayer1', 'fplPlayer2','fplPlayer3','fplPlayer4','fplPlayer5']
fpl_matrix_df.insert(loc=0, column='fplAdv_nxtGWs', value=fpl_teams_stats_df['fplAdv_nxtGWs'])
teams_top_fpl_players_df = teams_top_fpl_players_df.loc[teams_top_fpl_players_df['fplAdv_nxtGWs'] >= 0]
teams_top_fpl_players_df_dict = teams_top_fpl_players_df.to_dict('index')



teams_top_defensive_players_dict = {}
teams_top_defensive_players_df = pd.DataFrame() 
defensive_players = players_df[(players_df['position'] == 'GKP') | (players_df['position'] == 'DEF')] # gkps and defs
for team in def_teams_stats_df.index:
    team_top_defensive_players = defensive_players.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','defAdv_nxtGWs','xPts','^defAdv*xPts']].head(5).sort_values(['xPts','tot_pts'], ascending=[False,False])   # 5 ≈ 11/2  ###> head(3) is commented coz sometimes a top-3 player is injured (& you need a reserve to fill-in)
    team_top_defensive_players = team_top_defensive_players.round(3)
    teams_top_defensive_players_df = pd.concat([teams_top_defensive_players_df, team_top_defensive_players])
    team_top_defensive_players = [' ==> '.join(i) for i in zip(team_top_defensive_players['web_name'], '(' + team_top_defensive_players['xPts'].map(str) + ', ' + team_top_defensive_players['^defAdv*xPts'].map(str) + ')')]
    teams_top_defensive_players_dict[team] = team_top_defensive_players
defensive_matrix_df = pd.DataFrame(teams_top_defensive_players_dict).transpose()
defensive_matrix_df.index.name = 'team'
defensive_matrix_df.columns = ['defPlayer1', 'defPlayer2','defPlayer3','defPlayer4','defPlayer5']
defensive_matrix_df.insert(loc=0, column='defAdv_nxtGWs', value=def_teams_stats_df['defAdv_nxtGWs'])
teams_top_defensive_players_df = teams_top_defensive_players_df.loc[teams_top_defensive_players_df['defAdv_nxtGWs'] >= 0]
teams_top_defensive_players_df_dict = teams_top_defensive_players_df.to_dict('index')



teams_top_attacking_players_dict = {}
teams_top_attacking_players_df = pd.DataFrame() 
attacking_players = players_df[(players_df['position'] == 'MID') | (players_df['position'] == 'FWD')] # mids and fwds
for team in att_teams_stats_df.index:
    team_top_attacking_players = attacking_players.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','attAdv_nxtGWs','xPts','^attAdv*xPts']].head(5).sort_values(['xPts','tot_pts'], ascending=[False,False])   # 5 ≈ 11/2 ###> head(3) is commented coz sometimes a top 3-player is injured (& you need a reserve to fill-in)
    team_top_attacking_players = team_top_attacking_players.round(3)
    teams_top_attacking_players_df = pd.concat([teams_top_attacking_players_df, team_top_attacking_players])
    team_top_attacking_players = [' ==> '.join(i) for i in zip(team_top_attacking_players['web_name'], '(' + team_top_attacking_players['xPts'].map(str) + ', ' + team_top_attacking_players['^attAdv*xPts'].map(str) + ')')]
    teams_top_attacking_players_dict[team] = team_top_attacking_players
attacking_matrix_df = pd.DataFrame(teams_top_attacking_players_dict).transpose()
attacking_matrix_df.index.name = 'team'
attacking_matrix_df.columns = ['attPlayer1', 'attPlayer2','attPlayer3','attPlayer4','attPlayer5']
attacking_matrix_df.insert(loc=0, column='attAdv_nxtGWs', value=att_teams_stats_df['attAdv_nxtGWs'])
teams_top_attacking_players_df = teams_top_attacking_players_df.loc[teams_top_attacking_players_df['attAdv_nxtGWs'] >= 0]
teams_top_attacking_players_df_dict = teams_top_attacking_players_df.to_dict('index')



decision_matrix_df = avg_teams_stats_df[['team', 'avgAdv_nxtGWs']].set_index('team', drop=True)
decision_matrix_df['#atts'] = avg_teams_advanced_stats_df['#atts']
decision_matrix_df['#defs'] = avg_teams_advanced_stats_df['#defs']
teams_top_players_for_nxtGWs_dict = {}
teams_top_players_df = pd.DataFrame()
for team in decision_matrix_df.index:
    nberOfTeamTopAttPlayers = decision_matrix_df.at[team, '#atts']
    nberOfTeamTopDefPlayers = decision_matrix_df.at[team, '#defs']
    team_top_attacking_players = attacking_players.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','xPts','^avgAdv*xPts']].head(5).sort_values(['^avgAdv*xPts','xPts','tot_pts'], ascending=[False,False,False]).head(nberOfTeamTopAttPlayers)
    team_top_defensive_players = defensive_players.loc[players_df['team'] == team, ['position','team','web_name','tot_pts','xPts','^avgAdv*xPts']].head(5).sort_values(['^avgAdv*xPts','xPts','tot_pts'], ascending=[False,False,False]).head(nberOfTeamTopDefPlayers)
    team_top_players_for_nxtGWs = pd.concat([team_top_attacking_players, team_top_defensive_players]).sort_values(['^avgAdv*xPts', 'xPts','tot_pts'], ascending=[False,False,False])
    team_top_players_for_nxtGWs = team_top_players_for_nxtGWs.round(5)
    teams_top_players_df = pd.concat([teams_top_players_df, team_top_players_for_nxtGWs])
    team_top_players_for_nxtGWs = [' ==> '.join(i) for i in zip(team_top_players_for_nxtGWs['web_name'], '(' + team_top_players_for_nxtGWs['xPts'].map(str) + ', ' + team_top_players_for_nxtGWs['^avgAdv*xPts'].map(str) + ')')]
    teams_top_players_for_nxtGWs_dict[team] = team_top_players_for_nxtGWs
teams_top_players_for_nxtGWs_df = pd.DataFrame(teams_top_players_for_nxtGWs_dict).transpose()
teams_top_players_for_nxtGWs_df.columns = ['Player1', 'Player2','Player3']
decision_matrix_df = decision_matrix_df.join(teams_top_players_for_nxtGWs_df)
teams_top_players_df = teams_top_players_df.loc[teams_top_players_df['^avgAdv*xPts'] >= 0]
teams_top_players_df_dict = teams_top_players_df.to_dict('index')



print(fpl_matrix_df)
print("\n\n\n")
print(defensive_matrix_df)
print("\n\n\n")
print(attacking_matrix_df)
print("\n\n\n")
print(decision_matrix_df)
print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
def best_team_str(best_team, selection_criterion):
    ans = ""

    grouped_team = defaultdict(list)
    for player in best_team:
        grouped_team[player["position"]].append(player)

    ans += f"\nBEST TEAM according to {selection_criterion}:\n"
    ans += "####################################################################################################################################################################################################################\n"
    for position, players in grouped_team.items():
        str1 = f"#     {position}: "
        ans += str1
        sorted_players = sorted(players, key=lambda x: x[selection_criterion], reverse=True)
        player_strings = [f"{player['web_name']} ({player['team']}) ==> {player[selection_criterion]:.3f}" for player in sorted_players]
        str2 = " /|\ ".join(player_strings)
        ans += str2

        for i in range(len(str1 + str2), 211):
            ans += ' '
        ans += '#\n'
    ans += "####################################################################################################################################################################################################################\n"
    ans += "\n\n\n\n\n"

    return ans



def select_best_team(players, selection_criterion):
    # Organize players by position
    position_map = defaultdict(list)
    for player in players:
        position_map[player["position"]].append(player)
    
    # Sort players in each position by points
    for position in position_map:
        position_map[position] = sorted(position_map[position], key=lambda x: x[selection_criterion], reverse=True)

    # Choose the top goalkeeper
    goalkeeper = position_map['GKP'][:1]

    # Choose the top 5 defenders, 5 midfielders, and 3 forwards
    defenders = position_map['DEF'][:5]
    midfielders = position_map['MID'][:5]
    forwards = position_map['FWD'][:3]
    
    # Select the formation based on the performance of the top players
    # Here we use a simple greedy algorithm that selects the formation with the highest total points
    formations = [
        (3, 4, 3),
        (3, 5, 2),
        (4, 4, 2),
        (4, 3, 3),
        (4, 5, 1),
        (5, 3, 2),
        (5, 4, 1),
    ]

    best_formation = None
    best_points = 0

    for formation in formations:
        criterion_points =  sum(float64([player[selection_criterion] for player in goalkeeper])) + \
                            sum(float64([player[selection_criterion] for player in defenders[:formation[0]]])) + \
                            sum(float64([player[selection_criterion] for player in midfielders[:formation[1]]])) + \
                            sum(float64([player[selection_criterion] for player in forwards[:formation[2]]]))

        if criterion_points > best_points:
            best_points = criterion_points
            best_formation = formation

    print("\nTotal " + selection_criterion + ": " + f"{best_points:.5f}") 
    
    # Select the team based on the best formation
    best_team = (
        goalkeeper +
        defenders[:best_formation[0]] +
        midfielders[:best_formation[1]] +
        forwards[:best_formation[2]]
    )

    return best_team



# players_df_dict = players_df.to_dict('index')
# players_dict_extended = {key : {**players_dict.get(key,{}), **players_df_dict.get(key,{})} for key in set([*players_dict]).union(set([*players_df_dict]))}
# selection_criterion = input("\n\n\nWhich BEST TEAM selection criterion do you want to use?\t")
# best_team = select_best_team(players_dict_extended.values(), selection_criterion)
# print(best_team_str(best_team, selection_criterion))

teams_selections_str = ""

print("Selected Team according to FPL advantage:")
best_team = select_best_team(teams_top_fpl_players_df_dict.values(), '^fplAdv*xPts')
print(best_team_str(best_team, '^fplAdv*xPts'))
teams_selections_str += best_team_str(best_team, '^fplAdv*xPts')

print("Selected Team according to DEFensive advantage:")
best_team = select_best_team(teams_top_defensive_players_df_dict.values(), '^defAdv*xPts')
print(best_team_str(best_team, '^defAdv*xPts'))
teams_selections_str += best_team_str(best_team, '^defAdv*xPts')

print("Selected Team according to ATTacking advantage:")
best_team = select_best_team(teams_top_attacking_players_df_dict.values(), '^attAdv*xPts')
print(best_team_str(best_team, '^attAdv*xPts'))
teams_selections_str += best_team_str(best_team, '^attAdv*xPts')

print("Selected Team according to AVeraGe advantage:")
best_team = select_best_team(teams_top_players_df_dict.values(), '^avgAdv*xPts')
print(best_team_str(best_team, '^avgAdv*xPts'))
teams_selections_str += best_team_str(best_team, '^avgAdv*xPts')
######################################################################################################################################################################################################################################################################################################################################



######################################################################################################################################################################################################################################################################################################################################
timestr = time.strftime("%d'%m'%Y-%H:%M")
folder = "data/" + timestr



def print_to_file(string_to_print, file):
    with open(file, 'w') as f:
        print(string_to_print, file=f)



if input(f"Do you wish to save the results of this fpl simulation/analysis inside the folder '{folder}'  [Y/n]?   ").lower()[0] == 'y':
    folder_path = os.path.join(os.getcwd(), folder)
    os.mkdir(folder_path)

    players_df.to_csv(folder_path + "/players_stats.csv", index=False)
    fpl_teams_stats_df.to_csv(folder_path + "/fpl_teams_stats.csv", index=False)
    def_teams_stats_df.to_csv(folder_path + "/def_teams_stats.csv", index=False)
    att_teams_stats_df.to_csv(folder_path + "/att_teams_stats.csv", index=False)
    avg_teams_stats_df.to_csv(folder_path + "/avg_teams_stats.csv", index=False)
    avg_teams_advanced_stats_df.to_csv(folder_path + "/avg_teams_advanced_stats.csv", index=False)
    nxtGWs_fixtures_df.to_csv(folder_path + "/nxtGWs_fixtures.csv", index=False)
    fpl_matrix_df.to_csv(folder_path + "/fpl_matrix.csv")
    defensive_matrix_df.to_csv(folder_path + "/defensive_matrix.csv")
    attacking_matrix_df.to_csv(folder_path + "/attacking_matrix.csv")
    decision_matrix_df.to_csv(folder_path + "/decision_matrix.csv")
    print_to_file(teams_selections_str, folder_path + "/selected_teams.txt")



print("\n\n\n")
######################################################################################################################################################################################################################################################################################################################################