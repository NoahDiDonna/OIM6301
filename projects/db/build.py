import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The Tables
    """)
    return


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    from pathlib import Path

    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return Path, database, duckdb, mo, pl


@app.cell
def _():
    as_of = "2022-12-31"
    return


@app.cell
def _(database, duckdb):
    database.unlink(missing_ok=True)

    with duckdb.connect(database) as _con:

        _con.execute("""
            CREATE TABLE members (
                member_id INTEGER PRIMARY KEY,
                first_name VARCHAR NOT NULL,
                last_name VARCHAR NOT NULL,
                school_email VARCHAR NOT NULL UNIQUE,
                class_year INTEGER NOT NULL,
                join_date DATE NOT NULL
            )
        """)

        _con.execute("""
            CREATE TABLE portfolios (
                portfolio_id INTEGER PRIMARY KEY,
                member_id INTEGER NOT NULL,
                portfolio_name VARCHAR NOT NULL,
                created_date DATE NOT NULL,
                strategy_label VARCHAR,
                FOREIGN KEY (member_id) REFERENCES members(member_id)
            )
        """)

        _con.execute("""
            CREATE TABLE assets (
                asset_id INTEGER PRIMARY KEY,
                asset_name VARCHAR NOT NULL,
                asset_type VARCHAR NOT NULL
                    CHECK (asset_type IN ('Stock', 'ETF', 'Crypto')),
                sector VARCHAR,
                CHECK (
                    (asset_type = 'Crypto' AND sector IS NULL)
                    OR
                    (asset_type IN ('Stock', 'ETF') AND sector IS NOT NULL)
                )
            )
        """)

        _con.execute("""
            CREATE TABLE asset_tickers (
                ticker_history_id INTEGER PRIMARY KEY,
                asset_id INTEGER NOT NULL,
                ticker VARCHAR NOT NULL,
                effective_start_date DATE NOT NULL,
                effective_end_date DATE,
                UNIQUE (asset_id, effective_start_date),
                UNIQUE (ticker, effective_start_date),
                CHECK (
                    effective_end_date IS NULL
                    OR effective_end_date >= effective_start_date
                ),
                FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
            )
        """)

        _con.execute("""
            CREATE TABLE closing_prices (
                asset_id INTEGER NOT NULL,
                price_date DATE NOT NULL,
                closing_price DECIMAL(12, 4) NOT NULL
                    CHECK (closing_price > 0),
                PRIMARY KEY (asset_id, price_date),
                FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
            )
        """)

        _con.execute("""
            CREATE TABLE trades (
                trade_id INTEGER PRIMARY KEY,
                portfolio_id INTEGER NOT NULL,
                asset_id INTEGER NOT NULL,
                trade_date DATE NOT NULL,
                trade_type VARCHAR NOT NULL
                    CHECK (trade_type IN ('Buy', 'Sell')),
                quantity DECIMAL(18, 6) NOT NULL
                    CHECK (quantity > 0),
                price_per_unit DECIMAL(12, 4) NOT NULL
                    CHECK (price_per_unit > 0),
                fee DECIMAL(12, 4) NOT NULL DEFAULT 0
                    CHECK (fee >= 0),
                UNIQUE (portfolio_id, asset_id, trade_date),
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id),
                FOREIGN KEY (asset_id, trade_date)
                    REFERENCES closing_prices(asset_id, price_date)
            )
        """)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The Data
    """)
    return


@app.cell
def _(Path):

    import csv
    import random
    from datetime import date, timedelta

    SEED = 42
    random.seed(SEED)

    AS_OF = date(2026, 10, 31)
    START_DATE = AS_OF - timedelta(days=364)

    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating data from {START_DATE} through {AS_OF}")

    def write_csv(filename, rows, columns):
        path = DATA_DIR / filename

        with open(path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        print(f"Created {path}")


    def date_range(start, end):
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)

    first_names = [
        "James", "Emma", "Liam", "Olivia", "Noah",
        "Sophia", "Lucas", "Mia", "Ethan", "Ava",
        "Mason", "Isabella", "Logan", "Amelia", "Henry"
    ]

    last_names = [
        "Smith", "Johnson", "Brown", "Davis", "Wilson",
        "Miller", "Moore", "Taylor", "Anderson", "Thomas",
        "Jackson", "White", "Harris", "Martin", "Thompson"
    ]

    members = []

    for i in range(15):
        members.append({
            "member_id": i + 1,
            "first_name": first_names[i],
            "last_name": last_names[i],
            "school_email": (
                f"{first_names[i].lower()}.{last_names[i].lower()}@babson.edu"
            ),
            "class_year": random.choice([2026, 2027, 2028, 2029]),
            "join_date": "2025-09-01"
        })

    write_csv(
        "members.csv",
        members,
        ["member_id", "first_name", "last_name",
         "school_email", "class_year", "join_date"]
    )


    portfolios = []

    strategies = [
        "Growth", "Value", "Income", "Balanced",
        "Index", "Technology", "Long-Term"
    ]

    for i in range(15):
        portfolios.append({
            "portfolio_id": i + 1,
            "member_id": i + 1,
            "portfolio_name": f"Portfolio {i + 1}",
            "created_date": "2025-10-15",
            "strategy_label": strategies[i % len(strategies)]
        })

    write_csv(
        "portfolios.csv",
        portfolios,
        ["portfolio_id", "member_id", "portfolio_name",
         "created_date", "strategy_label"]
    )


    asset_info = [
        ("Apple Inc.", "Stock", "Technology", "AAPL", 190),
        ("Microsoft Corp.", "Stock", "Technology", "MSFT", 400),
        ("Amazon.com Inc.", "Stock", "Consumer Discretionary", "AMZN", 210),
        ("NVIDIA Corp.", "Stock", "Technology", "NVDA", 180),
        ("JPMorgan Chase", "Stock", "Financials", "JPM", 290),
        ("Coca-Cola Co.", "Stock", "Consumer Staples", "KO", 65),
        ("Exxon Mobil", "Stock", "Energy", "XOM", 115),
        ("SPDR S&P 500 ETF", "ETF", "Broad Market", "SPY", 670),
        ("Invesco QQQ Trust", "ETF", "Technology", "QQQ", 600),
        ("Vanguard Total Stock Market ETF", "ETF", "Broad Market", "VTI", 330),
        ("Bitcoin", "Crypto", None, "BTC", 95000),
        ("Ethereum", "Crypto", None, "ETH", 3500)
    ]

    assets = []
    asset_tickers = []

    for i, info in enumerate(asset_info):
        name, asset_type, sector, ticker, starting_price = info

        assets.append({
            "asset_id": i + 1,
            "asset_name": name,
            "asset_type": asset_type,
            "sector": sector
        })

        asset_tickers.append({
            "ticker_history_id": i + 1,
            "asset_id": i + 1,
            "ticker": ticker,
            "effective_start_date": START_DATE.isoformat(),
            "effective_end_date": ""
        })

    write_csv(
        "assets.csv",
        assets,
        ["asset_id", "asset_name", "asset_type", "sector"]
    )

    write_csv(
        "asset_tickers.csv",
        asset_tickers,
        ["ticker_history_id", "asset_id", "ticker",
         "effective_start_date", "effective_end_date"]
    )


    closing_prices = []
    price_lookup = {}

    for i, info in enumerate(asset_info):
        asset_id = i + 1
        asset_type = info[1]
        price = float(info[4])

        for current in date_range(START_DATE, AS_OF):

            if asset_type != "Crypto" and current.weekday() >= 5:
                continue

            if asset_type == "Crypto":
                change = random.uniform(-0.045, 0.045)
            else:
                change = random.uniform(-0.025, 0.025)

            price *= (1 + change)
            price = round(max(price, 0.01), 4)

            price_lookup[(asset_id, current)] = price

            closing_prices.append({
                "asset_id": asset_id,
                "price_date": current.isoformat(),
                "closing_price": f"{price:.4f}"
            })

    write_csv(
        "closing_prices.csv",
        closing_prices,
        ["asset_id", "price_date", "closing_price"]
    )


    trades = []
    holdings = {}

    used_combinations = set()

    initial_buys = [
        (1, 1, date(2025, 11, 3)),
        (2, 2, date(2025, 11, 3))
    ]

    trade_id = 1

    for portfolio_id, asset_id, trade_date in initial_buys:

        price = price_lookup[(asset_id, trade_date)]
        quantity = 10.0

        trades.append({
            "trade_id": trade_id,
            "portfolio_id": portfolio_id,
            "asset_id": asset_id,
            "trade_date": trade_date.isoformat(),
            "trade_type": "Buy",
            "quantity": f"{quantity:.6f}",
            "price_per_unit": f"{price:.4f}",
            "fee": "2.5000"
        })

        holdings[(portfolio_id, asset_id)] = quantity
        used_combinations.add(
            (portfolio_id, asset_id, trade_date)
        )

        trade_id += 1


    trade_candidates = []

    for portfolio_id in range(1, 16):
        for asset_id in range(1, 13):

            for current in date_range(START_DATE, AS_OF):

                key = (portfolio_id, asset_id, current)

                if key in used_combinations:
                    continue

                if (asset_id, current) not in price_lookup:
                    continue

                if current in [date(2026, 10, 29), date(2026, 10, 30)]:
                    if (portfolio_id, asset_id) in [(1, 1), (2, 2)]:
                        continue

                trade_candidates.append(key)

    random.shuffle(trade_candidates)

    selected_trades = sorted(trade_candidates[:298], key=lambda x: x[2])

    for portfolio_id, asset_id, trade_date in selected_trades:

        key = (portfolio_id, asset_id)
        current_holding = holdings.get(key, 0.0)

        if current_holding <= 0 or random.random() < 0.65:
            trade_type = "Buy"
            quantity = round(random.uniform(1, 15), 6)
            holdings[key] = current_holding + quantity

        else:
            trade_type = "Sell"

            quantity = round(
                random.uniform(0.1, min(current_holding, 5.0)),
                6
            )

            holdings[key] = current_holding - quantity

        price = price_lookup[(asset_id, trade_date)]

        trades.append({
            "trade_id": trade_id,
            "portfolio_id": portfolio_id,
            "asset_id": asset_id,
            "trade_date": trade_date.isoformat(),
            "trade_type": trade_type,
            "quantity": f"{quantity:.6f}",
            "price_per_unit": f"{price:.4f}",
            "fee": f"{random.uniform(0, 9.99):.4f}"
        })

        used_combinations.add(
            (portfolio_id, asset_id, trade_date)
        )

        trade_id += 1


    oversell_details = []

    oversell_cases = [
        (1, 1, date(2026, 10, 29)),
        (2, 2, date(2026, 10, 30))
    ]

    for portfolio_id, asset_id, trade_date in oversell_cases:

        key = (portfolio_id, asset_id)

        balance = 0.0

        for trade in sorted(trades, key=lambda x: (x["trade_date"], x["trade_id"])):

            if (
                trade["portfolio_id"] == portfolio_id
                and trade["asset_id"] == asset_id
                and date.fromisoformat(trade["trade_date"]) < trade_date
            ):
                quantity = float(trade["quantity"])

                if trade["trade_type"] == "Buy":
                    balance += quantity
                else:
                    balance -= quantity

        oversell_quantity = round(balance + 10.0, 6)

        price = price_lookup[(asset_id, trade_date)]

        trades.append({
            "trade_id": trade_id,
            "portfolio_id": portfolio_id,
            "asset_id": asset_id,
            "trade_date": trade_date.isoformat(),
            "trade_type": "Sell",
            "quantity": f"{oversell_quantity:.6f}",
            "price_per_unit": f"{price:.4f}",
            "fee": "2.5000"
        })

        oversell_details.append({
            "trade_id": trade_id,
            "portfolio_id": portfolio_id,
            "asset_id": asset_id,
            "trade_date": trade_date.isoformat(),
            "previous_holdings": round(balance, 6),
            "quantity_sold": oversell_quantity
        })

        trade_id += 1

    trades.sort(key=lambda x: x["trade_id"])

    write_csv(
        "trades.csv",
        trades,
        ["trade_id", "portfolio_id", "asset_id", "trade_date",
         "trade_type", "quantity", "price_per_unit", "fee"]
    )


    # --------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------

    print("\n========== DATA GENERATION SUMMARY ==========")

    print(f"Members: {len(members)}")
    print(f"Portfolios: {len(portfolios)}")
    print(f"Assets: {len(assets)}")
    print(f"Ticker histories: {len(asset_tickers)}")
    print(f"Closing prices: {len(closing_prices)}")
    print(f"Trades: {len(trades)}")

    print("\nIntentional rule violations:")
    for violation in oversell_details:
        print(violation)

    print("\nAll CSV files successfully generated.")
    print(f"Data directory: {DATA_DIR}")
    print(f"AS_OF date: {AS_OF}")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #A Look at the Data
    """)
    return


@app.cell
def _(pl):
    import matplotlib.pyplot as plt

    prices = pl.read_csv("projects/db/data/closing_prices.csv")

    apple_prices = (
        prices
        .filter(pl.col("asset_id") == 1)
        .with_columns(
            pl.col("price_date").str.to_date()
        )
        .sort("price_date")
    )

    apple_prices.head()
    return apple_prices, plt


@app.cell
def _(apple_prices, plt):
    plt.figure(figsize=(12, 5))

    plt.plot(
        apple_prices["price_date"].to_list(),
        apple_prices["closing_price"].to_list()
    )

    plt.title("Apple (AAPL) Daily Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Closing Price ($)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Apple's closing prices show frequent daily fluctuations over the year, which somewhat resembles real stock market behavior, although the prices are artificially generated using random percentage changes rather than actual market data.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Row Counts
    """)
    return


@app.cell
def _(Path, pl):
    data_dir = Path("projects/db/data")

    for file in data_dir.glob("*.csv"):
        df = pl.read_csv(file)
        print(f"{file.name}: {df.height} rows")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #A Row It Refuses
    """)
    return


@app.cell
def _(database, duckdb):
    try:
        with duckdb.connect(database) as _con:
            _con.execute("""
                INSERT INTO trades (
                    trade_id,
                    portfolio_id,
                    asset_id,
                    trade_date,
                    trade_type,
                    quantity,
                    price_per_unit,
                    fee
                )
                VALUES (
                    9999,
                    1,
                    1,
                    '2026-10-30',
                    'Buy',
                    -5,
                    190,
                    2.50
                )
            """)

    except Exception as e:
        print("Database rejected the row:")
        print(e)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I attempted to insert a trade with a negative quantity of -5. The database rejected the row because the trades table has a CHECK constraint requiring quantity to be greater than zero. This demonstrates that the database successfully enforces the positive quantity rule and prevents invalid trades from being stored.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Answers You Already Knew
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. How many members are in the investment club
    2. How many assets are in the database
    3. How many portfolios in the database
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #A View
    """)
    return


@app.cell
def _(database, duckdb):
    con = duckdb.connect(database)

    con.execute("""
        CREATE OR REPLACE VIEW current_portfolio_holdings AS
        SELECT
            m.member_id,
            m.first_name,
            m.last_name,
            p.portfolio_id,
            p.portfolio_name,
            a.asset_id,
            a.asset_name,
            SUM(
                CASE
                    WHEN t.trade_type = 'Buy' THEN t.quantity
                    WHEN t.trade_type = 'Sell' THEN -t.quantity
                END
            ) AS units_held
        FROM trades t
        JOIN portfolios p
            ON t.portfolio_id = p.portfolio_id
        JOIN members m
            ON p.member_id = m.member_id
        JOIN assets a
            ON t.asset_id = a.asset_id
        GROUP BY
            m.member_id,
            m.first_name,
            m.last_name,
            p.portfolio_id,
            p.portfolio_name,
            a.asset_id,
            a.asset_name
        HAVING SUM(
            CASE
                WHEN t.trade_type = 'Buy' THEN t.quantity
                WHEN t.trade_type = 'Sell' THEN -t.quantity
            END
        ) > 0
    """)

    con.close()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I created a view called `current_portfolio_holdings` to answer the weekly business question: "How many units of each asset does every member currently hold in their portfolio?" The view joins the members, portfolios, assets, and trades tables and calculates current holdings by subtracting sold quantities from purchased quantities. This allows investment club members to quickly review their portfolio positions without manually calculating their transactions each week. Because it is a view rather than a separate stored table, it automatically reflects the latest transactions whenever it is queried.
    """)
    return


if __name__ == "__main__":
    app.run()
