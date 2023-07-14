import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os


# Function that starts the web-scraping process using Beautiful Soup and some URL from main():
def get_url(link):
    url = link
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


# Function that returns a player's name, DOB, and national team:
def player_bio(soup):
    player_name = soup.find("h1").text.strip()
    # Find DOB:
    bio_element1 = soup.find("div", id="meta")
    bio_element2 = bio_element1.find_all("div")
    player_dob_date = None
    for div_element in bio_element2:
        span_element = div_element.find("span", id="necro-birth")
        if span_element is not None:
            player_dob_string = span_element.text.strip()
            player_dob_date = datetime.strptime(player_dob_string, "%B %d, %Y")
            break
    # Use player DOB to calculate age using current date:
    current_date = datetime.now()
    player_age = current_date.year - player_dob_date.year
    if current_date.month < player_dob_date.month or (
            current_date.month == player_dob_date.month and current_date.day < player_dob_date.day):
        player_age -= 1
    return player_name, player_age


def player_stats(soup):
    # Find stats table:
    table_element1 = soup.find("table", id="scout_full_FW")
    # Find table header and define the header names:
    table_header = table_element1.find("thead")
    header_row = table_header.find_all("tr")[1]
    header_names = [header_name.text.strip() for header_name in header_row]
    header_names_refined = [x for x in header_names if x != '']
    # Find table body and extract data points into a dictionary:
    stats_dict = {}
    table_body = table_element1.find("tbody")
    for row in table_body.find_all("tr"):
        if "thead over_header thead" in row.get("class", []) or "thead thead" in row.get("class", []):
            continue  # Skip rows with repeated headers
        stat_names_columns = row.find_all("th")
        columns = row.find_all("td")
        stat_names = [stat_name_column.text.strip() for stat_name_column in stat_names_columns]
        stats = [stat.text.strip() for stat in columns]
        for stat_name in stat_names:
            stats_dict[stat_name] = stats
    # Convert the stats dictionary into a pandas dataframe:
    df = pd.DataFrame.from_dict(stats_dict, orient='index')
    df.columns = header_names_refined[1:]
    df.index.name = header_names_refined[0]
    # Remove rows with no values
    df.dropna(axis=0, how='all', inplace=True)
    return df


def main():
    # Make a dictionary of player names and URLs to iterate over and create many dataframes:
    player_links = ["aed3a70f/scout/11566/Ollie-Watkins-Scouting-Report",
                    "93feac6e/scout/11566/Patrick-Bamford-Scouting-Report",
                    "07802f7f/scout/11566/Danny-Ings-Scouting-Report",
                    "e5478b87/scout/11566/Taiwo-Awoniyi-Scouting-Report",
                    "8b529245/scout/11566/Carlos-Vinicius-Scouting-Report"]
    # Basic Player Info:
    for link in player_links:
        url = f"https://fbref.com/en/players/{link}"
        soup = get_url(url)
        """print(f'Player Name: {player_bio(soup)[0]}\n')
        print(f'Player Age: {player_bio(soup)[1]}\n')"""
        # Download Excel file of stats into "player_stats" subfolder:
        df = player_stats(soup)
        file_path = os.path.join('player_stats', f'{player_bio(soup)[0]}.xlsx')
        df.to_excel(file_path, index=True)


if __name__ == '__main__':
    main()
