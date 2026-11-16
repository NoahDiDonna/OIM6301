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


if __name__ == "__main__":
    app.run()
