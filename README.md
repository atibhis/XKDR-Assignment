# Stock Market Data

This repository fetches stick market data from Yahoo Finance for listed companies in Indian Stock Exchanges (NSE,BSE).

To fetch the data, the input should be in a JSON format. 

The JSON objects should be:
- `symbol` : Stock Symbol (eg: INFY)
- `exchange` : `NSE` | `BSE` (default: `NSE`)
- `frequency` : `Daily` | `Weekly` | `Monthly` (default: `Daily`)
- `start_date` : Start date for data in YYYY-MM-DD format (eg: `2002-03-01`)
- `end_date` : End date for data in YYYY-MM-DD format (eg: `2012-03-01`) (default: Present Day)
- `span` :   `1D`, `5D`, `3M`, `6M`, `YTD`, `1Y`, `5Y`, `Max` (default: `1Y`)

Note: Either mention `start_date` (& `end_date` in case it should not default to present day) or `span`. If both are provided, `start_date` would be implemented. 
