'''
Web scraping FBref using the soccerdata API
Last Updated: 2/12/2024
'''

# Import the soccerdata module
import soccerdata as sd
import pandas as pd
import os

# Global variables for data export:
dir = 'C:/Users/cmart/OneDrive - Bentley University/Research/Player Valuation Model'


# Generate a pandas dataframe using a method:
def get_player_stats(league: str, season : str, stat_type: str = 'passing'):

    # Create an instance of the FBref class:
    sd_inst = sd.FBref(leagues=league, seasons=season)

    # Return a Pandas dataframe:
    return sd_inst.read_player_season_stats(stat_type=stat_type)


# Function that writes the output data to an Excel file:
def make_xl(path, df, file_name):
    file_path = os.path.join(path, f'{file_name}.xlsx')
    return df.to_excel(file_path, index=True)           # Remove index=True if getting permission error


# Try making two statistics dataframes and joining on the player name column:
test_df1 = get_player_stats('ENG-Premier League', '1819', 'passing')
test_df2 = get_player_stats('ENG-Premier League', '1819', 'shooting')

def join_dfs(df1, df2):
    merged_df = pd.merge(df1, df2, on='player')
    return merged_df


# Test the joining function:
# make_xl(dir, join_dfs(test_df1, test_df2), 'test_merge')

# List of league IDs, seasons, and statistic types for bulk scraping:
league_ids = ['ENG-Premier League', 'ESP-La Liga', 'FRA-Ligue 1', 'GER-Bundesliga', 'INT-World Cup', 'ITA-Serie A']
stat_types = ['standard', 'shooting', 'passing', 'passing_types', 'goal_shot_creation', 'defense', 'possession', 'playing_time'] #, 'misc', 'keeper', 'keeper_adv']
season_ids = ['1516', '1617', '1718', '1819', '1920', '2021', '2122', '2223']

# Iterate over the lists and create a series of dataframes with output data:
# WARNING: Attempting to iterate over all leagues and seasons will likely not worl. Break it up if needed:
for league in league_ids:
    for season in season_ids:

        # Initialize the list of statistic dataframes:
        df_list = []

        for stat in stat_types:
            print(f'\nWorking on the {stat} statistic for {league}...\n')

            # Create the dataframe using SD and print its row count:
            stat_df = get_player_stats(league=league, season=season, stat_type=stat)
            print(f'\n{stat} statistic dataframe row count: {stat_df.shape[1]}\n')

            # Add the dataframe to the list:
            df_list.append(stat_df)
            print(f'\nSuccessfully added the {stat} statistic dataframe list of dataframes.\n')

        # Sort the multi index of each dataframe for more efficient merging later on:
        for df in df_list:
            df = df.sort_index(level=['league', 'season', 'team', 'player'], inplace=True)

        # Define initial dataframe:
        joined_df = df_list[0]

        # Join each subsequent dataframe from the list to the previous one:
        for df, stat in zip(df_list[1:], stat_types[1:]):

            # Overwrite the initialized dataframe by joining the current dataframe to past joins:
            joined_df = joined_df.join(df, how='outer', lsuffix=f'_r', rsuffix=f'_{stat}')

        # Send final season-level output to Excel:
        make_xl(dir, joined_df, file_name=f'{league}_{season}_full_join')

print('Success.')
