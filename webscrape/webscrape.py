import datetime as dt
import json

import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def extract_table_data(url: str) -> pd.DataFrame:
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
            df[col] = pd.to_numeric(df[col].str.replace(",", "").str.replace("-", ""))
            # FIXME make this filtering moe robust
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
            return _yh[_input]
        else:
            return _yh[_default]

    yh_exchange = {"NSE": "NS", "BSE": "BO"}
    exchange = _param("exchange", yh_exchange, "NSE")
    params["exchange"] = exchange

    yh_frequency = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
    frequency = _param("frequency", yh_frequency, "Daily")
    params["frequency"] = frequency

    if "start_date" in keys:
        period1 = int(dt.datetime.strptime(input["start_date"], "%Y-%m-%d").timestamp())
        if "end_date" in keys:
            period2 = int(
                dt.datetime.strptime(input["end_date"], "%Y-%m-%d").timestamp()
            )
        else:
            period2 = int(dt.datetime.now().timestamp())
        params["period1"] = period1
        params["period2"] = period2
    elif "span" in keys:
        input_span = input["span"]
        if input_span in ["5Y", "Max"]:
            if input_span == "5Y":
                period1 = int(
                    (dt.datetime.today() - dt.timedelta(days=365 * 5)).timestamp()
                )
                period2 = int(dt.datetime.today().timestamp())
                params["period1"] = period1
                params["period2"] = period2
            else:
                period1 = int(dt.datetime(1980, 1, 1).timestamp())  # assumed period1
                period2 = int(dt.datetime.today().timestamp())
                params["period1"] = period1
                params["period2"] = period2
        elif input_span in ["1D", "5D", "3M", "6M", "YTD", "1Y"]:
            params["_span"] = input_span
        else:
            raise ValueError(
                f"incorrect span: {input_span}, span should be one of 5Y, Max, 1D, 5D, 3M, 6M, YTD, 1Y"
            )
    else:
        pass

    if "period1" in params:
        url = f"https://finance.yahoo.com/quote/{params['symbol']}.{params['exchange']}/history?period1={params['period1']}&period2={params['period2']}&frequency={params['frequency']}"
        df = extract_table_data(url)
    elif "_span" in params:
        url = f"https://finance.yahoo.com/quote/{params['symbol']}.{params['exchange']}/history?frequency={params['frequency']}"
        df = extract_table_data(url)
        max_date = df["Date"].max()
        _span = params["_span"]
        if _span == "1D":  # "1D", "5D", "3M", "6M", "YTD", "1Y"
            df = df.head(1)
        elif _span == "5D":
            df = df[df["Date"] >= max_date - dt.timedelta(days=5)]
        elif _span == "3M":
            df = df[df["Date"] >= max_date - relativedelta(months=3)]
        elif _span == "6M":
            df = df[df["Date"] >= max_date - relativedelta(months=6)]
        elif _span == "1Y":
            df = df[df["Date"] >= max_date - relativedelta(months=12)]
        elif _span == "YTD":
            df = df[df["Date"] >= dt.datetime(max_date.year, 1, 1)]
        else:
            raise ValueError(_span)
    else:
        url = f"https://finance.yahoo.com/quote/{params['symbol']}.{params['exchange']}/history?frequency={params['frequency']}"
        df = extract_table_data(url)
    plot_and_save(df, params["symbol"])
    return df


def plot_and_save(df: pd.DataFrame, symbol: str) -> None:
    df.to_csv(f"{symbol}.csv", index=False)
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
            )
        ]
    )
    fig.update_layout(title=f"{symbol}", yaxis_title="Stock Price", xaxis_title="Date")
    fig.show()
    fig.write_html(f"{symbol}.html")
    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="web scrape historical data of a stock from Yahoo"
    )
    parser.add_argument("input_file", type=str, help="path to the input file")
    args = parser.parse_args()
    df = get_url_from_input(args.input_file)
