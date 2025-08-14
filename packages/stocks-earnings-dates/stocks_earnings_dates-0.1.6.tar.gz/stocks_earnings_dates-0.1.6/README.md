
# 📈 stocks-earnings-dates

A lightweight Python package to query **historical earnings release dates** for all stocks in the **S&P 500** and the **top 100 Nasdaq**.  
It provides access to the last 21 years of earnings dates, since the earnings was released as the Item 2.02 in the 8-K Reports (the number of earnings for stock is fewer if the company is more recently listed).


---

##  Installation

Install the package via pip:

```bash
pip install stocks-earnings-dates --upgrade
```

---
## Project structure

```
stocks-earnings-dates/
├─ build/
├─ dist/
├─ edgar_earnings_pipeline/
│  ├─ 8k-link-builder/
│  │  ├─ EDGAR_8K_LINKS_GENERATOR.py
│  │  └─ edgar_8k_links_only.csv
│  ├─ earnings_item_2_02_scrapper/
│  │  └─ scrapping_script.py
│  ├─ ticker_cik_mapping/
│  │  ├─ CIK_GENERATOR.py
│  │  └─ tickers_with_cik.csv
│  └─ earnings_final.csv
├─ stocks_earnings_dates/
│  ├─ data/
│  │  └─ earnings.db
│  ├─ __init__.py
│  └─ core.py
├─ stocks_earnings_dates.egg-info/
├─ earnings_final.csv
└─ generate_db.py
```

---

##  What’s Inside?

This package uses a built-in SQLite database with over **37,000+ earnings dates** collected from the public sources of SEC EDGAR

You can easily:

- Get all historical earnings dates for a given stock.
- List all supported tickers.
- **Analyze price movement (%) after each earnings date**:  
  - Close → Open  
  - Close → Close  
  - Open → Close

---

##  Usage

### 🔍 Get earnings dates only:

```python
from stocks_earnings_dates import get_earnings, list_all_tickers

# Get earnings dates for a specific ticker
dates = get_earnings("AAPL")
print(dates)
# Output: ['2024-08-01', '2024-05-02', ..., '2014-07-22']

# List all tickers available in the database
tickers = list_all_tickers()
print(tickers)
```

---

### Get price reactions for each earnings date:

```python
from stocks_earnings_dates import get_earnings_price_reactions

reactions = get_earnings_price_reactions("AAPL")
for r in reactions:
    print(
        f"Earnings Date: {r['date']}, "
        f"Close→Open: {r['close_to_open_pct']}%, "
        f"Close→Close: {r['close_to_close_pct']}%, "
        f"Open→Close: {r['open_to_close_pct']}%"
    )
```

Output example:

```
Earnings Date: 2024-04-25, Close→Open: +2.45%, Close→Close: +4.38%, Open→Close: +1.88%
Earnings Date: 2024-01-19, Close→Open: -0.89%, Close→Close: -1.25%, Open→Close: -0.36%
```

These values are automatically calculated using [`yfinance`](https://pypi.org/project/yfinance/).

---
## Rebuild the DB

```bash
python generate_db.py
```

## How It Works

The earnings dates are stored locally in a **bundled SQLite database**. When using the price reaction function, the package:
- Loads the dates from the local database
- Fetches the daily stock price data surrounding those earnings dates from Yahoo Finance.
- Calculates the percentage change from:
  - **Previous Close → Next Open**
  - **Previous Close → Next Close**
  - **Next Open → Next Close**
-“Previous Close” refers to the stock’s closing price just before the earnings release (typically after hours). “Next Open” is the price at market open the following day, and “Next Close” is the closing price on that same day.
---
## ⚙️ Why SQLite?

This package uses SQLite internally to optimize both speed and memory usage when querying earnings dates.

Instead of loading the entire `.csv` file into memory every time, only the subset of data requested (such as the earnings dates for a single ticker) is loaded when needed.  
This improves the efficiency when accessing multiple tickers.

---

## Pipeline of Data extraction 

How the scrapping links are created:

For each stock in the tickers_with_cik.csv, the edgar_8k_links_generator creates 4 links for each stock's CIK 

How Earnings Dates Are Detected:

The scrapping code looks for SEC 8-K filings that report quarterly results (Item 2.02).

For older filings (before Aug 23 2004), it also includes Item 12, the previous code for earnings releases.

If more than one earnings-related 8-K is filed for the same quarter (e.g., corrections or updates), only the first filing within a 60-day window is kept to avoid duplicates.
The earnings database was compiled from publicly accessible financial websites.  
The CSV was cleaned, normalized and converted to a bundled SQLite database.


## Limitations

- This is a static dataset. Updates are not (yet) automated.
- EPS data and surprise values are not included (yet).

---

## Future Plans

- Add EPS (expected vs actual) and calculate surprise %
- Automatically update the database each quarter scrapping EDGAR 



## Fair use

- Set a real **User‑Agent** with contact email.  
- Sleep between requests; do not hammer SEC EDGAR.  
- Not affiliated with the SEC.

---

## 👨‍💻 Author

Made by **Albert Pérez**  
GitHub: [AlbertPerez7](https://github.com/AlbertPerez7)

---
