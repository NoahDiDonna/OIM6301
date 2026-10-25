import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Where the Tax Bill Is Lowest
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Anyone deciding where to buy a home in Massachusetts can use it, such as the couple in this example or a family relocating from out of state. It answers the question “which towns can I afford once the yearly property tax is counted, not just the purchase price?” Because the county, budget and tax limit can be changed, they can compare several areas in minutes and narrow a long list of towns down to a few worth visiting.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##2. My plan before AI
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To find the towns where the average home price and tax bill fit their limits, I would first define all the variables such as the county name, budget, annual tax limit, and fiscal year, which is already defined for us. Then, I would make a request to /ma/towns, passing Middlesex county as the parameter point. I would also handle the paginationif the response contains multiple pages of towns, ensuring all towns in Middlesex county are retrieved before filtering. I would then retrieve historical data for each town by making an API request, then filter that historical data so that it corresponds with the target fiscal year, 2026. My next step would be to check the budget conditions, calculate the property tax bill, check the tax condition, and finally keep the qualifying towns that pass both checks. I would then sort the list of qualifying towns to show the cheapest first.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs/Work
    """)
    return


@app.cell
def _():
    import requests

    county = "Middlesex"
    budget_dollars = 700000
    tax_limit_dollars = 7000
    fiscal_year = 2026
    return budget_dollars, county, fiscal_year, requests, tax_limit_dollars


@app.cell
def _(county, requests):
    first_page = requests.get("https://oim.zhili.dev/ma/towns", params={"county": county}).json()
    first_page
    return


@app.cell
def _(county, requests):
    all_towns = requests.get(
        "https://oim.zhili.dev/ma/towns",
        params={"county": county, "per_page": 100},
    ).json()

    all_towns["pagination"]
    return (all_towns,)


@app.cell
def _(requests):
    one_town_history = requests.get(
        "https://oim.zhili.dev/ma/towns/002/history"
    ).json()
    one_town_history
    return (one_town_history,)


@app.cell
def _(fiscal_year, one_town_history):
    one_year = None
    for year_record in one_town_history["years"]:
        if year_record["fiscal_year"] == fiscal_year:
            one_year = year_record

    one_year
    return


@app.cell
def _(all_towns):
    len(all_towns["items"])
    return


@app.cell
def _(all_towns):
    all_towns["pagination"]
    return


@app.cell
def _(all_towns, fiscal_year, requests):
    results = []

    for town in all_towns["items"]:
        town_history = requests.get(
            f"https://oim.zhili.dev/ma/towns/{town['dor_code']}/history"
        ).json()

        one_year2 = None
        for year_record2 in town_history["years"]:
            if year_record2["fiscal_year"] == fiscal_year:
                one_year2 = year_record2

        if one_year2 is not None:
            results.append({
                "name": town["name"],
                "average_value": one_year2["average_single_family_value_dollars"],
                "rate": one_year2["residential_rate_per_thousand"],
                "average_bill": one_year2["average_single_family_bill_dollars"],
            })

    results
    return (results,)


@app.cell
def _(budget_dollars, results, tax_limit_dollars):
    qualifying = []

    for row in results:
        if row["average_value"] <= budget_dollars and row["average_bill"] <= tax_limit_dollars:
            qualifying.append(row)

    qualifying
    return (qualifying,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Answer
    """)
    return


@app.cell
def _(qualifying):
    qualifying_sorted = sorted(qualifying, key=lambda row: row["average_bill"])
    qualifying_sorted
    return (qualifying_sorted,)


@app.cell
def _(budget_dollars, qualifying_sorted, tax_limit_dollars):
    cheapest = qualifying_sorted[0]

    answer = f"Of the {len(qualifying_sorted)} towns in Middlesex County where the average home fits a ${budget_dollars} budget and the average bill stays under ${tax_limit_dollars}, {cheapest['name']} has the lowest average bill at ${cheapest['average_bill']}, with an average home value of ${cheapest['average_value']} and a residential tax rate of {cheapest['rate']} per thousand."

    answer
    return (cheapest,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. How do I know my numbers are right?
    """)
    return


@app.cell
def _(cheapest):
    calculated_bill = cheapest["average_value"] * cheapest["rate"] / 1000
    calculated_bill
    return


@app.cell
def _(cheapest):
    cheapest["average_bill"]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This check confirms that average_bill, average_value, and rate are internally consistent. They weren't pulled from the API as three unrelated numbers that happen not to match. If the town's math works (bill ≈ value × rate ÷ 1,000, within rounding), it means that that the right field names were used, and the API's numbers follow the actual property tax formula.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Working with the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    My agent wrote for town in all_towns["towns"], guessing at the name of the list inside the API response. When I ran it, [it raised a KeyError / I looked at the response and saw the list was under a different key]. I changed it to all_towns["items"]. The agent hadn’t seen the real response, so it was guessing at field names it couldn’t know. If I had trusted the code without checking, the whole analysis would have failed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Reading it Back
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For this function:

    qualifying = []
    for row in results:
        if row["average_value"] <= budget_dollars and row["average_bill"] <= tax_limit_dollars:
            qualifying.append(row)

    qualifying

    In: results, a list of dicts with one entry per town, each holding that town’s average home value and average bill for fiscal_year. It also uses the two limits from the Inputs cell.

    Out: qualifying, the shorter list containing only the towns where both numbers are within the limits.

    A line I had to ask about: the if line, specifically why and is used instead of or, and whether <= is right.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For this function:

    one_year = None
    for year_record in one_town_history["years"]:
        if year_record["fiscal_year"] == fiscal_year:
            one_year = year_record

    one_year

    In: one_town_history, the API reply for one town, which includes a list of yearly records under "years". It also uses fiscal_year from the Inputs cell.

    Out: one_year, the single record for that year, with its home value, tax rate and bill. If the town has no record for that year, it stays None.

    A line I had to ask about: one_year = None. I asked why it’s there before the loop. It gives the variable a safe default, so a missing year gives None I can check for, instead of an error or a leftover value from another town.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Change: tax_limit_dollars = 8000 becomes 7000. Nothing else changes.

    Prediction (write this and commit before running):

    Lowering the limit by $1,000 should shrink the shortlist, because every town with a bill between $7,000 and $8,000 drops out.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    After lowering the limit by $1000, the list of qualifying towns shortened from 12 to 10 items(towns)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further
    """)
    return


@app.cell
def _(qualifying):
    qualifying_by_rate = sorted(qualifying, key=lambda row: row["rate"])
    qualifying_by_rate
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A town can have a low rate but a high average home value, giving it a bigger bill than a town with a higher rate but a cheaper average home. So ranking by rate alone can shuffle the order compared to ranking by bill.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##9. How Many Hours did I spend on this project
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    About 3.5-4
    """)
    return


if __name__ == "__main__":
    app.run()
