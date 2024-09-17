import json

import pandas as pd
import plotly.express as px
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def extract_table_data(stock_symbol):
    url = f"https://finance.yahoo.com/quote/{stock_symbol}/history?"
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        WebDriverWait(driver, 5).until(  # FIXME allow less lag
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.table-container > table.yf-ewueuo")
            )
        )
        # locate the table with the class 'table-container' and 'yf-ewueuo'
        table = driver.find_element(
            By.CSS_SELECTOR, "div.table-container > table.yf-ewueuo"
        )
        headers = table.find_elements(By.CSS_SELECTOR, "thead th")
        column_names = [header.text.strip() for header in headers]
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        table_data = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            row_data = [cell.text.strip() for cell in cells]
            table_data.append(row_data)
        df = pd.DataFrame(table_data, columns=column_names)
        df["Date"] = pd.to_datetime(df["Date"], format="%b %d, %Y")
        df = df[~df.isnull().any(axis=1)]
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            df[col] = pd.to_numeric(df[col].str.replace(",", ""))
        return df
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


def get_url_from_input(input_file: str) -> str:
    with open(input_file, "r") as file:
        input = json.load(file)
    valid_keys = ["symbol", "exchange", "frequency", "start_date", "end_date", "span"]
    keys = list(input.keys())
    invalid_keys = [i for i in keys if i not in valid_keys]
    assert input["symbol"]
    if invalid_keys:
        raise ValueError(f"Incorrect keys: {invalid_keys}, valid keys: {valid_keys}")

    params = {}

    symbol = input["symbol"]
    params["symbol"] = symbol

    def _param(_key: str, _yh: dict[str, str], _default: str) -> str:
        if _key in keys:
            _input = input[_key]
            assert _input in list(_yh.keys())
            return _yh[_key]
        else:
            return _yh[_default]

    yh_exchange = {"NSE": "NS", "BSE": "BO"}
    exchange = _param("exchange", yh_exchange, "NSE")
    params["exchange"] = exchange

    yh_frequency = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
    frequency = _param("frequency", yh_frequency, "Daily")
    params["frequency"] = frequency

    if ("start_date" in keys) and ("end_date" in keys):
        pass
        # default start for max dt.datetime(1980,1,1).timestamp()
    elif "span" in keys:
        pass
    else:
        span = _param(
            "span",
        )

    return input


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="web scrape historical data of a stock from Yahoo"
    )
    parser.add_argument("input_file", type=str, help="path to the input file")
    args = parser.parse_args()
    input = get_url_from_input(args.input_file)
    print(list(input.keys()))
    breakpoint()

# Example usage
# stock_symbol = "3MINDIA.NS"

# df = extract_table_data(stock_symbol)
# print(df)

# if df is not None and not df.empty:
#     print("DataFrame successfully created:")
#     print(df.head())
# else:
#     print("No data to plot.")

# # Plot if DataFrame is valid
# if df is not None and not df.empty:
#     # Create the line plot
#     fig = px.line(
#         df, x="Date", y="Close", title="Stock Closing Prices Over Time", markers=True
#     )

#     # Show the plot
#     fig.show()
# else:
#     print("DataFrame is empty or not defined.")
