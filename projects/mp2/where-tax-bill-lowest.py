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
    A · Where the Tax Bill Is Lowest
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. My plan before AI
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To find the towns where the average home price and tax bill fit their limits, I would first define all the variables such as the county name, budget, annual tax limit, and fiscal year, which is already defined for us. Then, I would make a request to /ma/towns, passing Middlesex county as the parameter point. I would also handle the paginationif the response contains multiple pages of towns, ensuring all towns in Middlesex county are retrieved before filtering. I would then retrieve historical data for each town by making an API request, then filter that historical data so that it corresponds with the target fiscal year, 2026. My next step would be to check the budget conditions, calculate the property tax bill, check the tax condition, and finally keep the qualifying towns that pass both checks. I would then sort the list of qualifying towns to show the cheapest first.
    """)
    return


if __name__ == "__main__":
    app.run()
