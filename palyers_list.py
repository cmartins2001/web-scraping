"""import pandas as pd"""
import requests
from bs4 import BeautifulSoup

url = "https://fbref.com/en/players/aa/"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

# Identify and iterate over the list of linked player names:
list_element1 = soup.find("div", class_="section_content")
player_links = list_element1.find_all("p")
player_info = []
for i in player_links:
    name = i.text.strip()
    link = i.find("a", href=True)
    if link:
        link = link["href"]
        player_info.append((name, link))

for name, link in player_info:
    print(f'Player Name: {name}\n'
          f'Player Link: {link}\n')
