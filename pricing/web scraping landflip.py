import numpy as np
import requests
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def fetch_land_data(url):
    try:
        # Make a request to the URL with a timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e} for URL: {url}")
        return []

    try:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'lxml')
        lands = soup.find_all('span', {'class': 'tag price-ac'})
        
        # Extract and clean data
        land_data = [cleaning(land.get_text()) for land in lands]
        return [data for data in land_data if data]  # Filter out None values
    except (AttributeError, IndexError, ValueError) as e:
        logging.error(f"Data extraction or conversion failed: {e} for URL: {url}")
        return []

def remove_outliers(data):
    # Convert the list to a NumPy array
    data = np.array(data)

    # Calculate Q1 (25th percentile) and Q3 (75th percentile)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)

    # Calculate the IQR
    iqr = q3 - q1

    # Determine the bounds for outliers
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Filter the data to remove outliers
    filtered_data = data[(data >= lower_bound) & (data <= upper_bound)]

    return filtered_data.tolist()

def cleaning(land):
    try:
        # Split the raw data into price and acreage components
        data_list = land.split(':')
        
        # Extract and clean the price
        price_str = data_list[-1].strip()
        translation_table = str.maketrans('', '', '$,K')
        price = float(price_str.translate(translation_table))
        
        # Extract and clean the acreage
        acres_str = data_list[0].strip()
        acres = float(acres_str.split(' ')[0])
        
        return price, acres
    except (IndexError, ValueError) as e:
        logging.error(f"Data cleaning failed: {e} for land: {land}")
        return None

def transformation(price, acres):
    try:
        PPA = round(price / acres, 2)
        return PPA
    except ZeroDivisionError as e:
        logging.error(f"Error in transformation: {e} for price: {price}, acres: {acres}")
        return None

def process_state(state):
    all_land_data = []
    for page_n in range(1, 5):  # Fetching first 4 pages for each state
        url = f'https://www.landflip.com/land-for-sale/{state.lower()}/{page_n}-p/an-s'
        land_data = fetch_land_data(url)
        
        if land_data:
            all_land_data.extend(land_data)

    if all_land_data:
        # Create a DataFrame
        data = []
        for price, acre in all_land_data:
            if acre <= 4:  # Accept only acres less than or equal to 4
                PPA = transformation(price, acre)
                if PPA is not None:
                    data.append({'State': state, 'Price': price, 'Acres': acre, 'Price per Acre': PPA})
        
        df = pd.DataFrame(data)
        
        # Save the raw data to CSV
        df.to_csv(f'{state.lower()}_raw_land_data.csv', index=False)
        logging.info(f"Saved raw data for {state} to {state.lower()}_raw_land_data.csv")
        
        # Remove outliers from price and acres separately
        filtered_prices = remove_outliers(df['Price'].tolist())
        filtered_acres = remove_outliers(df['Acres'].tolist())
        
        # Filter the DataFrame to only include the rows with filtered prices and acres
        filtered_data = df[(df['Price'].isin(filtered_prices)) & (df['Acres'].isin(filtered_acres))]
        
        # Save the filtered data to CSV
        filtered_data.to_csv(f'{state.lower()}_filtered_land_data.csv', index=False)
        logging.info(f"Saved filtered data for {state} to {state.lower()}_filtered_land_data.csv")

def main():
    states = ['VIRGINIA', 'FLORIDA', 'TENNESSEE', 'MICHIGAN', 'TEXAS', 'SOUTH CAROLINA', 'OKLAHOMA', 'NEVADA', 'CALIFORNIA']

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_state, state): state for state in states}
        
        for future in as_completed(futures):
            state = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing state {state}: {e}")

if __name__ == "__main__":
    main()
