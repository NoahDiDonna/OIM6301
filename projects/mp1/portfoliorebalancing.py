# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of option, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    The question I will be answering is C., rebalancing a portfolio. In the real world, a financial advisor or portfolio manager would use this to help them make decisions on how to allocate a cash in a portfolio for their client. Since we have the target allocations given, the program will help them decide how many shares to buy or sell given changes in the stock price in order to keep the target allocation percentage consistent with the client's investment goals.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    *Before you ask your agent anything, write how you would solve it: the steps, in order, in plain words, in five lines or more. Then answer these two questions:*

    - *What does your loop carry from one step to the next, the way a running total carries its sum?*
    - *Which check will you use in section 6, and which two numbers should agree?*

    *Commit this notebook with the message `mp1: plan before AI`.*

    ### My Plan

    First, I would calculate the total value of the portfolio by adding up the total cash value of the 6 holdings plus the $5,000. Then, I would multiply the total portfolio value by each stocks preferred allocation percentage to figure out the correct dollar amount for each holding. After that, I would calculate for the whole shares by dividing the stocks target amount by its current price, and then round down to the nearest whole number. Next, I would subtract the current shares from the target shares to find the desired transaction amount, which will indicate whether to buy or sell. Finally, I would figure out the remainging cash by multiplying the target shares by the price to get the ending stock values, and subtract this total from the overall portfolio value to find the leftover cash, and then find each stocks percentage weight to find how far it deviates from its target.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your option from the Mini Project 1 page. If you chose D, your own option, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    holdings = [
        ("AAPL", 100, 173.93),
        ("MSFT", 50, 319.53),
        ("GOOG", 80, 131.36),
        ("AMZN", 200, 129.33),
        ("NVDA", 20, 410.17),
        ("TSLA", 150, 255.70),
    ]
    cash = 5000.00
    target_weights = {"AAPL": 0.20, "MSFT": 0.20, "GOOG": 0.15,
                      "AMZN": 0.15, "NVDA": 0.15, "TSLA": 0.15}
    return cash, holdings, target_weights


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _(cash, holdings):
    portfolio_value = cash
    for ticker, shares, price in holdings:
        portfolio_value = portfolio_value + shares * price
    portfolio_value
    return portfolio_value, price, ticker


@app.cell
def _(holdings, portfolio_value, target_weights):
    for ticker1, shares1, price1 in holdings:
        target_dollars = portfolio_value * target_weights[ticker1]
        print(f"{ticker1}: target dollar amount = {target_dollars:.2f}")
    return


@app.cell
def _(holdings, portfolio_value, target_weights):
    for ticker2, shares2, price2 in holdings:
        target_shares = (portfolio_value * target_weights[ticker2]) // price2
        print(f"{ticker2}: target shares = {target_shares}")
    return


@app.cell
def _(holdings, portfolio_value, target_weights):
    for ticker3, shares3, price3 in holdings:
        target_shares1 = (portfolio_value * target_weights[ticker3]) // price3
        transaction = target_shares1 - shares3
        print(f"{ticker3}: transaction = {transaction}")
    return


@app.cell
def _(holdings, portfolio_value, target_weights):
    total_ending_value = 0
    for ticker4, shares4, price4 in holdings:
        target_shares2 = (portfolio_value * target_weights[ticker4]) // price4
        ending_value = target_shares2 * price4
        total_ending_value = total_ending_value + ending_value

    leftover_cash = portfolio_value - total_ending_value
    leftover_cash

    for ticker4, shares4, price4 in holdings:
        target_shares3 = (portfolio_value * target_weights[ticker4]) // price4
        ending_value2 = target_shares3 * price4
        weight = ending_value2 / portfolio_value
        deviation = weight - target_weights[ticker4]
        print(f"{ticker4}: weight = {weight:.4f}, deviation = {deviation:.4f}")
    return (leftover_cash,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _(holdings, portfolio_value, target_weights):
    for ticker5, shares5, price5 in holdings:
        _target_shares = (portfolio_value * target_weights[ticker5]) // price5
        _transaction = _target_shares - shares5
        _value_after = _target_shares * price5
        _weight_after = _value_after / portfolio_value
        print(f"{ticker5}: shares now = {shares5}, shares at target = {_target_shares}, "
              f"buy/sell = {_transaction}, value after = {_value_after:.2f}, "
              f"weight after = {_weight_after:.4f}")
    return


@app.cell
def _(leftover_cash):
    print(f"leftover cash is {leftover_cash}, which is positive, so no trade overspends the portfolio's cash.")
    return


@app.cell
def _(holdings, portfolio_value, target_weights):
    for ticker6, shares6, price6 in holdings:
        _target_shares = (portfolio_value * target_weights[ticker6]) // price6
        _value_after = _target_shares * price6
        _weight_after = _value_after / portfolio_value
        _deviation_points = (_weight_after - target_weights[ticker6]) * 100
        print(f"{ticker6}: weight after = {_weight_after:.4f}, deviation = {_deviation_points:.2f} points")

    return


@app.cell
def _():
    print("Every stock lands within about a quarter of a percentage point of its target, which is close enough for practical rebalancing.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _(holdings, leftover_cash, portfolio_value, target_weights):
    check_total = leftover_cash
    for ticker7, shares7, price7 in holdings:
        _target_shares = (portfolio_value * target_weights[ticker7]) // price7
        check_total = check_total + _target_shares * price7
    check_total
    return (check_total,)


@app.cell
def _(check_total, portfolio_value):
    print(f"portfolio value (section 4) = {portfolio_value:.2f}")
    print(f"leftover cash + ending stock values (section 6) = {check_total:.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This rebuilds the total portfolio value a second way: starting from leftover_cash and adding back each stock's ending value, instead of starting from the original cash and adding each stock's starting value.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A problem I consistently has was naming the variables: price, shares, and ticker in each individual cell when solving the next part of the problem. Since marimo won't let you define the same name twice, I was putting a number after each variable to differentiate them. My agent would only recognize the pattern when I copy and pasted the updated chunk with the updated variables into the chat. For example, in the first code chunk in section 4, I was able to use the base variables when calculating the portfolio value. But, when I tried to calculate the target shares, I had to edit the code and change the variable names to unique ones. When the agent got it right the first time, I would often copy and paste my output back into it and ask if my output was correct. My agent would then varify it by doing the mathematical calculations, which made it much more clear to me.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For my going further section, I decided to imagine if there was a one-day price shock of NVDA, as this is the most historically volatile stock of the six. I simulated a scenario where NVDA experiences a sudden one-day price shock of 10%, and analyzed how this shockimpacts the overall portfolio's value given its weight in the portfolio. This will shows how sensitive the rebalance is to a single stock's move.
    """)
    return


@app.cell
def _(holdings):
    shocked_holdings = []
    for ticker8, shares8, price8 in holdings:
        if ticker8 == "NVDA":
            price8 = price8 * 1.10
        shocked_holdings.append((ticker8, shares8, price8))
    shocked_holdings
    return (shocked_holdings,)


@app.cell
def _(cash, shocked_holdings):
    shocked_portfolio_value = cash
    for ticker9, shares9, price9 in shocked_holdings:
        shocked_portfolio_value = shocked_portfolio_value + shares9 * price9
    shocked_portfolio_value
    return (shocked_portfolio_value,)


@app.cell
def _(
    price,
    shocked_holdings,
    shocked_portfolio_value,
    target_weights,
    ticker,
):
    for ticker10, shares10, price10 in shocked_holdings:
        _target_shares = (shocked_portfolio_value * target_weights[ticker]) // price
        _value_after = _target_shares * price10
        _weight_after = _value_after / shocked_portfolio_value
        _deviation_points = (_weight_after - target_weights[ticker10]) * 100
        print(f"{ticker10}: weight after = {_weight_after:.4f}, deviation = {_deviation_points:.2f} points")
    return


if __name__ == "__main__":
    app.run()
