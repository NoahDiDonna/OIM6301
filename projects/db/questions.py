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
    Counting the 30 days back from the latest trade in the data (my choice, since I read “last 30 days” as relative to the data and not to as_of), 12 portfolios traded, led by portfolio 1 with 5 trades, portfolio 7 with the biggest buy spend ($42,476.66 including fees) and portfolio 9 with the biggest sell proceeds at 325,875.17 after fees.
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
    All 15 members have exactly 1 portfolio (none are missing one), and the total they bought (quantity × price, without fees) runs from $67,260.21 for member 11 to $2,143,422.29 for member 15.
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
    On 2026-10-31, the 15 portfolios hold 146 positive asset positions in total, with Portfolio 1 holding 10 assets, led by 31.62 units of Ethereum.
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
    In the 90 days ending at the latest trade date, all 77 trades I can see matched a closing price, and the first 10 were priced exactly at the close (0% difference).
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
    Every asset the club follows has been traded by at least one portfolio, so the list of never-traded assets is empty (0 rows), which means the query found no asset with a missing trade.
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
    My query returned 0 rows, so it found no asset with more than one ticker in asset_tickers, which means I can’t report a value traded.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I checked every trade against the closing-price rule and none broke it: every trade falls on a date when its asset has a closing price, so the list of violations is empty (0 rows), which means my tables refuse that kind of row.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q8
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will be a short list, where a portfolio sold more units of an asset than it held at that point. I’ll find them by adding up each portfolio’s buys minus sells for each asset up to the date of every sell, then keeping only the sells where that running holding goes below zero. If my tables already block that kind of row, the list will come back empty and I’ll show that refusal in my answer instead.
    """)
    return


@app.cell
def _(ask):
    ask("""
        WITH running AS (
            SELECT
                t.trade_id,
                t.portfolio_id,
                t.asset_id,
                t.trade_date,
                t.trade_type,
                t.quantity,
                SUM(CASE WHEN t.trade_type = 'Buy'
                    THEN t.quantity ELSE -t.quantity END)
                    OVER (
                        PARTITION BY t.portfolio_id, t.asset_id
                        ORDER BY t.trade_date
                    ) AS units_held_after
            FROM trades AS t
        )
        SELECT
            r.trade_id,
            r.portfolio_id,
            p.portfolio_name,
            r.asset_id,
            a.asset_name,
            r.trade_date,
            r.quantity AS sell_quantity,
            r.units_held_after
        FROM running AS r
        JOIN portfolios AS p ON p.portfolio_id = r.portfolio_id
        JOIN assets AS a ON a.asset_id = r.asset_id
        WHERE r.trade_type = 'Sell' AND r.units_held_after < 0
        ORDER BY r.portfolio_id, r.asset_id, r.trade_date
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three sells broke the rule that a portfolio never sells more than it holds: trade 301 (Portfolio 1 selling 22.824 units of Apple Inc. on 2026-10-29), trade 284 (Portfolio 1 selling 0.091 units of Invesco QQQ Trust on 2026-10-13), and trade 302 (Portfolio 2 selling 37.516 units of Microsoft Corp. on 2026-10-30), each leaving the portfolio with a negative holding right after the sale.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q9
    Which trades happened before their portfolio was created? (checks a rule)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will be no results. I’ll join trades to portfolios on portfolio_id and keep only the trades where trade_date is less than created_date, and since no constraint blocks this, any rows that show up are real violations. If I didn’t plant one for this rule, I expect the list to come back empty, which would mean the data follows the rule even though nothing forces it to.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT
            t.trade_id,
            t.portfolio_id,
            p.portfolio_name,
            p.created_date,
            t.trade_date
        FROM trades AS t
        JOIN portfolios AS p ON p.portfolio_id = t.portfolio_id
        WHERE t.trade_date < p.created_date
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    No trade happened before its portfolio was created: comparing every trade’s date to its portfolio’s created date returned 0 rows, so the data follows this rule even though nothing in the tables forces it to.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prediction: Q10
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Each portfolio’s market value by sector on the as_of date
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I think the result will have one row per portfolio and sector pair, showing the market value of what that portfolio holds in that sector on 2026-10-31. For each asset I’ll take units bought minus units sold, multiply by that asset’s closing price on that date, and then add those up by sector, so portfolios that hold nothing in a sector won’t have a row for it. If an asset has no closing price on exactly 2026-10-31, I expect its value to drop out or show NULL, which would make some portfolio totals come out too low.
    """)
    return


@app.cell
def _(ask):
    ask("""
        WITH holdings AS (
            SELECT
                t.portfolio_id,
                t.asset_id,
                SUM(CASE WHEN t.trade_type = 'Buy'
                    THEN t.quantity ELSE -t.quantity END) AS units_held
            FROM trades AS t
            WHERE t.trade_date <= DATE '2026-10-31'
            GROUP BY t.portfolio_id, t.asset_id
            HAVING SUM(CASE WHEN t.trade_type = 'Buy'
                THEN t.quantity ELSE -t.quantity END) > 0
        )
        SELECT
            p.portfolio_id,
            p.portfolio_name,
            a.sector,
            SUM(h.units_held * c.closing_price) AS market_value
        FROM holdings AS h
        JOIN portfolios AS p ON p.portfolio_id = h.portfolio_id
        JOIN assets AS a ON a.asset_id = h.asset_id
        JOIN closing_prices AS c
            ON c.asset_id = h.asset_id AND c.price_date = DATE '2026-10-31'
        GROUP BY p.portfolio_id, p.portfolio_name, a.sector
        ORDER BY p.portfolio_id, a.sector
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    On 2026-10-31 (the date hard-coded in my query), all 15 portfolios have a market value, ranging from $56,424.47 for Portfolio 3 up to $1,571,741.39 for Portfolio 15, but every sector comes back as None, so this result can’t yet be split by sector.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How I Know These Numbers Are Right.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Check 1: Q1 totals equal the sum of its grouped parts
    """)
    return


@app.cell
def _(ask):
    _grouped = ask("""
        SELECT
            portfolio_id,
            COUNT(*) AS trade_count,
            SUM(CASE WHEN trade_type = 'Buy'
                THEN quantity * price_per_unit + fee ELSE 0 END)
                AS buy_spend
        FROM trades
        WHERE trade_date >= (SELECT MAX(trade_date) FROM trades) - INTERVAL 30 DAY
        GROUP BY portfolio_id
    """)

    _total = ask("""
        SELECT
            COUNT(*) AS trade_count,
            SUM(CASE WHEN trade_type = 'Buy'
                THEN quantity * price_per_unit + fee ELSE 0 END)
                AS buy_spend
        FROM trades
        WHERE trade_date >= (SELECT MAX(trade_date) FROM trades) - INTERVAL 30 DAY
    """)

    grouped_trade_count = _grouped["trade_count"].sum()
    grouped_buy_spend = _grouped["buy_spend"].sum()
    total_trade_count = _total["trade_count"][0]
    total_buy_spend = _total["buy_spend"][0]

    print("sum of grouped trade_count:", grouped_trade_count, "| ungrouped total:", total_trade_count)
    print("sum of grouped buy_spend:", grouped_buy_spend, "| ungrouped total:", total_buy_spend)

    assert grouped_trade_count == total_trade_count, "trade counts don't match"
    assert abs(grouped_buy_spend - total_buy_spend) < 0.01, "buy spend totals don't match"
    print("Check 1 passed: grouped totals match ungrouped totals.")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Check 2: Holdings recomputed a second way (separate buy and sell totals)
    """)
    return


@app.cell
def _():
    return


@app.cell
def _(ask):
    _holdings = ask("""
        SELECT
            portfolio_id,
            asset_id,
            SUM(CASE WHEN trade_type = 'Buy'
                THEN quantity ELSE -quantity END) AS units_held
        FROM trades
        WHERE trade_date <= DATE '2026-10-31'
        GROUP BY portfolio_id, asset_id
        HAVING SUM(CASE WHEN trade_type = 'Buy'
            THEN quantity ELSE -quantity END) > 0
        ORDER BY portfolio_id, asset_id
    """)

    _bought_minus_sold = ask("""
        WITH bought AS (
            SELECT portfolio_id, asset_id, SUM(quantity) AS units_bought
            FROM trades
            WHERE trade_type = 'Buy' AND trade_date <= DATE '2026-10-31'
            GROUP BY portfolio_id, asset_id
        ),
        sold AS (
            SELECT portfolio_id, asset_id, SUM(quantity) AS units_sold
            FROM trades
            WHERE trade_type = 'Sell' AND trade_date <= DATE '2026-10-31'
            GROUP BY portfolio_id, asset_id
        )
        SELECT
            b.portfolio_id,
            b.asset_id,
            b.units_bought - COALESCE(s.units_sold, 0) AS units_held
        FROM bought AS b
        LEFT JOIN sold AS s
            ON s.portfolio_id = b.portfolio_id AND s.asset_id = b.asset_id
        WHERE b.units_bought - COALESCE(s.units_sold, 0) > 0
        ORDER BY b.portfolio_id, b.asset_id
    """)

    print("rows from CASE WHEN method:", len(_holdings))
    print("rows from bought-minus-sold method:", len(_bought_minus_sold))

    _merged = _holdings.join(
        _bought_minus_sold,
        on=["portfolio_id", "asset_id"],
        suffix="_check"
    )

    assert len(_holdings) == len(_bought_minus_sold), "row counts don't match"
    assert (_merged["units_held"] - _merged["units_held_check"]).abs().max() < 0.0001, \
        "units held don't match between the two methods"
    print("Check 2 passed: both methods agree on units held.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Working With the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    What the AI gave me: For Q5 (assets never traded), the agent wrote a LEFT JOIN from assets to trades with WHERE t.trade_id IS NULL, and it returned 0 rows. The agent called that a valid answer.

    What I did: I didn’t accept an empty table at face value, since a broken query can look the same, so I asked whether 0 rows was correct. I compared COUNT(*) on assets to COUNT(DISTINCT asset_id) on trades, and both were 12, so I changed nothing and wrote the answer as “every asset has been traded.”

    How I knew: The LEFT JOIN ... IS NULL pattern is the standard anti-join, and the matching counts confirmed to me that no asset was missing a trade. The evidence is in the Q5 cell, which shows the query, the “No results” output, and my answer sentence.

    Related pushback: After the Q7 closing-price check also came back empty, I asked whether I should change my data to avoid an empty result. The agent said no and pointed me to my Part A notes, and the Q8 oversell check, which did return rows, showed the data can fail a rule when I’ve planted a violation.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reading It Back
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q3: Prediction
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    I think the result will have one row per portfolio and asset pair, showing units bought minus units sold up to 2026-10-31, with only the positive holdings kept. Assets that were completely sold off will drop out, so there should be fewer rows than the total number of portfolio and asset combinations in trades. If I forget to count sells as negative, the numbers will come out too high because everything would just add up as bought. Before any grouping, I think the joins alone (trades to portfolios to assets) will produce exactly one row per trade, so 302 rows total, since portfolio_id and asset_id are foreign keys and every trade is guaranteed to match exactly one portfolio and exactly one asset, never zero and never more than one.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
