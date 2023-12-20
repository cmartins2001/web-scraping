'''
Python Program for Obtaining NFT Sales Data from the Reservoir NFT API
Connor Martins and Ward Doornbos - Bentley University
12/18/2023
'''

# Import packages:
from datetime import datetime
import pandas as pd
import requests
import os
import time as tm

# The API Key:
key = "14899665-a9aa-574c-a7e8-6404e40572ad"

# Dictionary of collection slugs and corresponding IDs from documentation:
slug_ids = {'super-puma' : '0x283c0bba69ebd4643cfce761b34b0206e75b2091',
            'guttermelo' : '0x232e97b08266510de8f43f179fd0efbfe2910975',
            'rtfkt-nike-cryptokicks' : '0xf661d58cfe893993b11d53d11148c4650590c692',
            'superplastic-supergucci' : '0x78d61c684a992b0289bbfe58aaa2659f667907f8',
            'hugo-x-imaginaryones-embrace-your-emotions' : '0xe4d20bc4a845aa35b008f5f9f85e50b581df7263',
            'inbetweenersdg' : '0x57c4d987431a4582a5e3ce9a3a9a5f1e9f55757c',
            'alts-by-adidas' : '0x749f5ddf5ab4c1f26f74560a78300563c34b417d'
            }

# Dictionary of collection slugs and start dates:
collections = ['super-puma', 'guttermelo', 'rtfkt-nike-cryptokicks', 'superplastic-supergucci', 'hugo-x-imaginaryones-embrace-your-emotions', 'inbetweenersdg', 'alts-by-adidas']
dates = ["2023-02-01 00:00:00",
         "2023-06-01 00:00:00",
         "2022-04-01 00:00:00",
         "2022-02-01 00:00:00",
         "2022-10-01 00:00:00",
         "2022-12-01 00:00:00",
         "2023-03-01 00:00:00"]


# Function that converts datetime strings to Unix epoch seconds timestamps:
def convert_time(date_time):
    
    # Convert the date and time to a datetime object:
    dt_object = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    # Convert the datetime object to a Unix epoch timestamp in seconds:
    seconds = int(dt_object.timestamp())

    return seconds


# Dictionary of collection ids and timestamps:
ids = [val for key, val in slug_ids.items()]
seconds_list = [convert_time(x) for x in dates]
ids_times = dict(zip(ids, seconds_list))


# Function that generates a dataframe for a given collection ID:
def fetch_reservoir_events(collection_id: str, after_dt: int, limit:int=1000, api_key:str=None):

    base_url = "https://api.reservoir.tools/sales/v6?collection="
    params = {
        "startTimestamp": after_dt,
        "limit": limit
    }

    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    # Initialize lists to store extracted information
    all_sale_dates = []
    all_quantities = []
    all_symbols = []
    all_sources = []

    # Function to process events
    def process_events(sales):
        sale_dates = []
        quantities = []
        symbols = []
        sources = []

        for sale in sales:
            sale_time = sale.get('timestamp')

            # Quantity and currency info:
            price = sale.get('price')
            currency = price.get('currency')
            amount = price.get('amount')

            # Transaction Source:
            source = sale.get('orderSource')

            # Add to the empty lists:    
            sale_dates.append(sale_time)
            symbols.append(currency.get('symbol'))
            quantities.append(amount.get('decimal'))
            sources.append(source)

        return sale_dates, quantities, symbols, sources

    # Fetch events for the initial page
    while True:
        response = requests.get(base_url+collection_id, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            # Check if the 'sales' key is present in the response:
            if 'sales' in data:
                current_page_events = data['sales']

                # Process events from the current page
                sale_dates, quantities, symbols, sources = process_events(current_page_events)

                # Append data from the current page to the overall lists
                all_sale_dates.extend(sale_dates)
                all_quantities.extend(quantities)
                all_symbols.extend(symbols)
                all_sources.extend(sources)

                # Update the URL for the next page if available
                continuation_token = data.get('continuation')
                if continuation_token:
                    params['continuation'] = data.get('continuation')
                    tm.sleep(1)  # Add a 1-second delay between requests
                    continue
                else:
                    break
            else:
                print("No 'sales' key in the response.")
                break
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    # Create a Pandas DataFrame
    df = pd.DataFrame({
        'Sale Date': all_sale_dates,
        'Quantity': all_quantities,
        'Symbol': all_symbols,
        'Source': all_sources
    })

    # Convert the date column to the correct format and set it as index:
    df['Sale Date'] = pd.to_datetime(df['Sale Date'], unit='s').dt.strftime('%Y-%m-%d')
    df = df.set_index('Sale Date').sort_index(ascending=False)

    return df


# Define export folder:
dir = 'C:/Users/cmart/OneDrive - Bentley University/Research/Scraping NFTs'
# file_path = os.path.join(dir, f'gutter_sales.csv')
# gutter_df = fetch_reservoir_events("0x232e97b08266510de8f43f179fd0efbfe2910975", 1685592000, api_key=key)
# gutter_df.to_csv(file_path)

# Fetch events for all of the listed collections and start dates:
for id, time in ids_times.items():
    coll_df = fetch_reservoir_events(id, time, api_key=key)
    print(coll_df.index.min())

    # Name the output file by the corresponding slug:
    for slug, coll_id in slug_ids.items():
        if coll_id == id:
            name = slug

    file_path = os.path.join(dir, f'{name}_sales.csv')
    coll_df.to_csv(file_path)
