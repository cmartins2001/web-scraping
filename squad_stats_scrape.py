import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# Create a dictionary of league identifiers to insert/iterate in the URL:
league_url_paths = {"Premier League": "9/Premier-League-Stats",
                    "La Liga": "12/La-Liga-Stats",
                    "Bundesliga": "20/Bundesliga-Stats",
                    "Serie A": "11/Serie-A-Stats",
                    "Ligue 1": "13/Ligue-1-Stats"}
for keys in league_url_paths:
    path = league_url_paths[keys]
    url = f"https://fbref.com/en/comps/{path}"
    page = requests.get(url)
    # Find and print HTML elements by ID:
    soup = BeautifulSoup(page.content, "html.parser")
    league_name = soup.find("h1")
    league_name = league_name.text.strip()
    """print(league_name)"""
    # Find HTML elements by class name and print using for loop:
    table_elements = soup.find_all("div", class_="switcher_content")
    """for table_element in table_elements:
        print(table_element.text, end="\n"*2)"""
    # Identify a wrapped table and its header:
    outer_element1 = soup.find("div", id="all_stats_squads_standard",
                               class_="table_wrapper tabbed")
    outer_element2 = outer_element1.find("div", id="switcher_stats_squads_standard")
    outer_element3 = outer_element2.find("table", id="stats_squads_standard_for")
    table_header = outer_element3.find("thead")
    table = outer_element3.find("tbody")
    # Initialize empty dict:
    dict1 = {}
    # Scrape the header and data from the wrapped table:
    header_row = table_header.find_all("tr")[1]
    header_names = [header_name.text.strip() for header_name in header_row]
    header_names_refined = [x for x in header_names if x != '']
    if table:
        for row in table.find_all("tr"):
            team_name_columns = row.find_all("th")
            columns = row.find_all("td")
            if team_name_columns:
                # Extract team name(s):
                team_names = [team_name_column.text.strip() for team_name_column in team_name_columns]
                # Extract data points:
                values = [column.text.strip() for column in columns]
                # Assign team name(s) as key(s) and corresponding values as value(s) in the dictionary
                for team_name in team_names:
                    dict1[team_name] = values
    else:
        print("Table not found.")
    # Create the pandas dataframe:
    df = pd.DataFrame.from_dict(dict1, orient='index')
    df.columns = header_names_refined[1:]           # used this to ignore the team name field and avoid length mismatch
    df.index.name = header_names_refined[0]         # here, named the row names the first element of the header_names
    # Optional step: export the pandas dataframe as an Excel or CSV file to the squad_stats subfolder:
    file_path = os.path.join('squad_stats', f'{league_name}.xlsx')
    df.to_excel(file_path, index=True)
    """df.to_csv('output.csv', index=True)"""
