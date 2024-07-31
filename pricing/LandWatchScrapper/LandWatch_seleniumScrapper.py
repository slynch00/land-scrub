from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
import numpy as np

# Initialize the driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

minAcres = input("Enter the minimum acres: ")
maxAcres = input("Enter the maximum acres: ")

all_data = []

def extract_data(zipCode):
    """Function to extract land price and size data from the current page."""
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '#search-button'))
        WebDriverWait(driver, 1).until(element_present)

        landPrice = driver.find_elements(By.CLASS_NAME, '_6ae86')
        landSize = driver.find_elements(By.CLASS_NAME, '_6a6db')

        data = []
        for price, size in zip(landPrice, landSize):
            price_value = float(price.text.replace('$', '').replace(',', ''))
            size_value = float(size.text.split()[0].replace(',', ''))
            price_per_acre = float(price_value / size_value)
            data.append((zipCode, price_value, size_value, price_per_acre))

        return data

    except Exception as e:
        print(f"An error occurred while extracting data: {e}")
        return []

def process_zip_code(zipCode):
    """Process all pages for a given zip code and collect data."""
    driver.get(f'https://www.landwatch.com/zip-{zipCode}/undeveloped-land/acres-{minAcres}-{maxAcres}/sold')
    print(f'Processing Zip Code: {zipCode}')

    try:
        skip_element_present = EC.presence_of_element_located((By.CLASS_NAME, '_20540'))
        if WebDriverWait(driver, 1).until(skip_element_present):
            print(f"Skipping Zip Code: {zipCode} due to no results")
            return

    except Exception:
        pass

    for _ in range(4):
        all_data.extend(extract_data(zipCode))

        try:
            next_button_present = EC.presence_of_element_located((By.CLASS_NAME, 'b68ea'))
            next_button = WebDriverWait(driver, 1).until(next_button_present)
            next_button.click()
            time.sleep(2)
        except Exception:
            break

if os.path.exists("land_data.xlsx"):
    os.remove("land_data.xlsx")
if os.path.exists("average_price_per_acre.xlsx"):
    os.remove("average_price_per_acre.xlsx")

csv_file_path = 'Export-NH-counties (Cleaned).xlsx - Sheet1.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path, dtype={'ZIP': str})

# Remove leading zeros from ZIP codes
df['ZIP'] = "0" + df['ZIP']
df_cleaned = df.drop_duplicates(subset=["ZIP"])
zip_codes = df_cleaned['ZIP']

print(zip_codes.size)  # Debugging

for zipCode in zip_codes:
    process_zip_code(zipCode)

# Close the browser
driver.quit()

# Create a DataFrame for all data
df = pd.DataFrame(all_data, columns=["Zipcode", "Price", "LandSize", "Price per Acre"])

# Remove duplicates and rows with null Zipcode
df_cleaned = df.drop_duplicates(subset=["Zipcode", "Price", "LandSize"])
df_cleaned = df_cleaned.dropna(subset=['Zipcode'])

# Remove outliers based on 'Price per Acre' column
Q1 = df_cleaned["Price per Acre"].quantile(0.25)
Q3 = df_cleaned["Price per Acre"].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df_no_outliers = df_cleaned[
    (df_cleaned["Price per Acre"] >= lower_bound) &
    (df_cleaned["Price per Acre"] <= upper_bound)
]

# Save the cleaned data to an Excel file
df_no_outliers.to_excel("land_data.xlsx", index=False)
print("Cleaned data saved to land_data.xlsx")

# Calculate average price per acre grouped by zip code from the cleaned data
average_price_per_acre = df_no_outliers.groupby("Zipcode")["Price per Acre"].mean().reset_index()
    
# Save the average price per acre data to an Excel file
average_price_per_acre.to_excel("average_price_per_acre.xlsx", index=False)
print("Average Price per Acre data saved to average_price_per_acre.xlsx")
