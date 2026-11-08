# The Scenario

I chose the Babson Investment Club database scenario.

The Babson Investment Club manages paper investment portfolios for its members to help them learn about investing. The database will replace the club's current system of spreadsheets and broker screenshots with a centralized system that tracks members, portfolios, assets, trades, and historical closing prices.

The database will use 2022 as its year of historical data so that it can capture the Facebook ticker change from FB to META. It will include approximately 15 members, at least 12 assets, at least 300 trades, and historical closing prices for every weekday for stocks and ETFs and every day for cryptocurrency.

The goal is to maintain a complete history of investment activity, calculate portfolio holdings, and determine portfolio values over time.

# The ERD

```mermaid
erDiagram
    MEMBERS ||--o{ PORTFOLIOS : owns
    PORTFOLIOS ||--o{ TRADES : contains
    ASSETS ||--o{ TRADES : involved_in
    ASSETS ||--|{ ASSET_TICKERS : has
    ASSETS ||--o{ CLOSING_PRICES : has
    CLOSING_PRICES ||--o{ TRADES : prices

    MEMBERS {
        int member_id PK
        string first_name
        string last_name
        string school_email UK
        string class_year
        date join_date
    }

    PORTFOLIOS {
        int portfolio_id PK
        int member_id FK
        string portfolio_name
        date created_date
        string strategy_label
    }

    ASSETS {
        int asset_id PK
        string asset_name
        string asset_type
        string sector
    }

    ASSET_TICKERS {
        int ticker_history_id PK
        int asset_id FK
        string ticker
        date effective_start_date
        date effective_end_date
    }

    TRADES {
        int trade_id PK
        int portfolio_id FK
        int asset_id FK
        date trade_date FK
        string trade_type
        decimal quantity
        decimal price_per_unit
        decimal fee
    }

    CLOSING_PRICES {
        int asset_id PK, FK
        date price_date PK
        decimal closing_price
    }
```

# What One Row Means

- **Members:** One row represents one Babson Investment Club member, including their personal information and membership details.
- **Portfolios:** One row represents one investment portfolio owned by one member.
- **Assets:** One row represents one unique investment asset, such as a stock, ETF, or cryptocurrency.
- **Asset_Tickers:** One row represents a ticker symbol associated with an asset during a specific period of time.
- **Trades:** One row represents one purchase or sale of an asset within a portfolio on a specific date.
- **Closing_Prices:** One row represents the closing price of one asset on one specific date.

# Design Choices