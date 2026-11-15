import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    import duckdb
    import polars as pl
    from pathlib import Path

    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return (ask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Question #1
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think there will be one row per portfolio, with columns for trades, spent on buys, and received from sells. Portfolios with no trades in the window should show 0 trades and 0 dollars, not disappear. Also, buys should come out higher than the quantity × price, and sells lower, because of the fees.
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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
