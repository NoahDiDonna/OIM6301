import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl

    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return ask, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q1
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think there will be one row per portfolio, with columns for trades, spent on buys, and received from sells. Portfolios with no trades in the window should show 0 trades and 0 dollars, not disappear.Also, buys should come out higher than the quantity × price, and sells lower, because of the fees.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Trades, buy spend, and sell proceeds by portfolio (last 30 days)
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            portfolio_id,
            COUNT(*) AS trade_count,
            SUM(CASE WHEN trade_type = 'Buy'
                THEN quantity * price_per_unit + fee ELSE 0 END)
                AS buy_spend,
            SUM(CASE WHEN trade_type = 'Sell'
                THEN quantity * price_per_unit - fee ELSE 0 END)
                AS sell_proceeds
        FROM trades
        WHERE trade_date >= (SELECT MAX(trade_date) FROM trades) - INTERVAL 30 DAY
        GROUP BY portfolio_id
        ORDER BY portfolio_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q2
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will have one row per member, so the row count should match however many members are in the members table. Members with no portfolio should still show up with 0 portfolios and 0 dollars bought, as long as I use LEFT JOINs. Most members will probably have one or two portfolios, and the ones with more will have the biggest totals. I’m also expecting the portfolio counts to come out too high at first, because each portfolio repeats for every trade after the join, so I’ll need COUNT(DISTINCT) to fix that. The total bought should only count buy trades.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Portfolio count and total value bought, by member
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            m.member_id,
            COUNT(DISTINCT p.portfolio_id) AS portfolio_count,
            COALESCE(SUM(CASE WHEN t.trade_type = 'Buy'
                THEN t.quantity * t.price_per_unit ELSE 0 END), 0)
                AS total_bought
        FROM members AS m
        LEFT JOIN portfolios AS p ON p.member_id = m.member_id
        LEFT JOIN trades AS t ON t.portfolio_id = p.portfolio_id
        GROUP BY m.member_id
        ORDER BY m.member_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q3
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will have one row per portfolio and asset pair, showing units bought minus units sold up to 2022-12-31, with only the positive holdings kept. Assets that were completely sold off will drop out, so there should be fewer rows than the total number of portfolio and asset combinations in trades. If I forget to count sells as negative, the numbers will come out too high because everything would just add up as bought.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Current holdings by portfolio, as of 2026-10-31
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            t.portfolio_id,
            p.portfolio_name,
            t.asset_id,
            a.asset_name,
            SUM(CASE WHEN t.trade_type = 'Buy'
                THEN t.quantity ELSE -t.quantity END) AS units_held
        FROM trades AS t
        JOIN portfolios AS p ON p.portfolio_id = t.portfolio_id
        JOIN assets AS a ON a.asset_id = t.asset_id
        WHERE t.trade_date <= DATE '2026-10-31'
        GROUP BY t.portfolio_id, p.portfolio_name, t.asset_id, a.asset_name
        HAVING SUM(CASE WHEN t.trade_type = 'Buy'
            THEN t.quantity ELSE -t.quantity END) > 0
        ORDER BY t.portfolio_id, a.asset_name
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q4
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will have one row per trade in the 90 days ending 2026-10-31, so the row count should match how many trades happened in that window. Each trade gets matched to the closing price for the same asset on the same date, and the percent difference is (trade price minus closing price) divided by closing price times 100. Most of the differences should be pretty small, within a few percent, but any trade on a day with no closing price (like a weekend) might drop out or show NULL depending on my join.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            t.trade_id,
            t.portfolio_id,
            a.asset_name,
            t.trade_date,
            t.price_per_unit AS trade_price,
            c.closing_price,
            (t.price_per_unit - c.closing_price) / c.closing_price * 100
                AS pct_diff_from_close
        FROM trades AS t
        JOIN assets AS a ON a.asset_id = t.asset_id
        JOIN closing_prices AS c
            ON c.asset_id = t.asset_id AND c.price_date = t.trade_date
        WHERE t.trade_date >= (SELECT MAX(trade_date) FROM trades) - INTERVAL 90 DAY
        ORDER BY t.trade_date, t.trade_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q5
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will be a short list of assets, maybe none, one row per asset that the club follows but that never shows up in any trade. I’ll get them with a LEFT JOIN from assets to trades and keep only the rows where the trade side is NULL (or use NOT EXISTS), so I expect it to be way fewer rows than the whole assets table. If I use a plain inner join or filter the wrong way, I’d get the traded assets instead, which is the opposite of what the question asks.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            a.asset_id,
            a.asset_name,
            a.asset_type,
            a.sector
        FROM assets AS a
        LEFT JOIN trades AS t ON t.asset_id = a.asset_id
        WHERE t.trade_id IS NULL
        ORDER BY a.asset_name
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q6
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will be one row for the single asset that changed its ticker, showing the total value traded over the year (quantity times price) combined across both the old and new ticker. The trades are probably split across two ticker values, so I expect to need to group by the asset’s id instead of the ticker, or the total would be split into two rows and look too small. If I only grouped by ticker, I’d get two separate totals that each undercount what the asset really traded.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT asset_id, COUNT(*) AS ticker_count
        FROM asset_tickers
        GROUP BY asset_id
        ORDER BY ticker_count DESC
    """)
    return


@app.cell
def _(ask):
    ask("""
        WITH changed_ticker_asset AS (
            SELECT asset_id
            FROM asset_tickers
            GROUP BY asset_id
            HAVING COUNT(*) > 1
        )
        SELECT
            a.asset_id,
            a.asset_name,
            STRING_AGG(DISTINCT tk.ticker, ', ') AS tickers_used,
            SUM(t.quantity * t.price_per_unit) AS total_value_traded
        FROM changed_ticker_asset AS c
        JOIN assets AS a ON a.asset_id = c.asset_id
        JOIN asset_tickers AS tk ON tk.asset_id = c.asset_id
        JOIN trades AS t ON t.asset_id = c.asset_id
        GROUP BY a.asset_id, a.asset_name
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##Prediction: Q7
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will be a very short list, each one on a date where its asset has no closing price (like a weekend or holiday). I’ll find them by LEFT JOINing trades to prices on both asset and trade date and keeping only the rows where the price side is NULL, so everything else should drop out. If my tables already refuse that kind of row, the list will come back empty and I’ll have to show that refusal in my answer instead.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            t.trade_id,
            t.portfolio_id,
            t.asset_id,
            t.trade_date
        FROM trades AS t
        LEFT JOIN closing_prices AS c
            ON c.asset_id = t.asset_id AND c.price_date = t.trade_date
        WHERE c.asset_id IS NULL
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
