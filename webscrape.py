import time

import pandas as pd
import plotly.express as px
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Specify path to the WebDriver executable
webdriver_service = Service(
    "/Users/atibhisharma/Documents/python_code/XKDR/XKDR-Assignment/chromedriver.exe"
)

# Start the WebDriver session
driver = webdriver.Chrome()  # service=webdriver_service, options=chrome_options)


def clean_numeric(value):
    """Clean and convert values to numeric, handling non-numeric characters and None values"""
    if value is None:
        return float("nan")  # Handle None values by returning NaN

    try:
        # Remove commas and other non-numeric characters
        cleaned_value = value.replace(",", "").split()[0]
        return float(cleaned_value)
    except ValueError:
        # Return NaN for non-numeric values j
        return float("nan")


def extract_table_data(stock_symbol):
    url = f"https://finance.yahoo.com/quote/{stock_symbol}/history?p={stock_symbol}"
    driver.get(url)

    # Allow time for the page to load
    time.sleep(10)  # Adjust this sleep time if needed

    try:
        # Wait until the table is present and visible
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.table-container > table.yf-ewueuo")
            )
        )

        # Locate the table with the class 'table-container' and 'yf-ewueuo'
        table = driver.find_element(
            By.CSS_SELECTOR, "div.table-container > table.yf-ewueuo"
        )

        # Extract column names
        headers = table.find_elements(By.CSS_SELECTOR, "thead th")
        column_names = [header.text.strip() for header in headers]

        # Extract rows
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        table_data = []

        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            row_data = [cell.text.strip() for cell in cells]
            table_data.append(row_data)

        # Create DataFrame
        df = pd.DataFrame(table_data, columns=column_names)

        # Clean and format DataFrame
        # Convert Date to datetime format
        df["Date"] = pd.to_datetime(df["Date"], format="%b %d, %Y")

        # Remove commas and convert to numeric types
        # Clean and convert numeric columns
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            df[col] = df[col].apply(clean_numeric)

        print(df)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser session
        driver.quit()


# Example usage
stock_symbol = "HINDALCO.NS"

df = extract_table_data(stock_symbol)

if df is not None and not df.empty:
    print("DataFrame successfully created:")
    print(df.head())
else:
    print("No data to plot.")

# Plot if DataFrame is valid
if df is not None and not df.empty:
    # Create the line plot
    fig = px.line(
        df, x="Date", y="Close", title="Stock Closing Prices Over Time", markers=True
    )

    # Show the plot
    fig.show()
else:
    print("DataFrame is empty or not defined.")
