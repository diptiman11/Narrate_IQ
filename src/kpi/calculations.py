import pandas as pd


def calculate_revenue(sales: pd.DataFrame) -> pd.Series:
    """
    Daily total revenue.
    """
    return sales.groupby("date")["revenue"].sum()


def calculate_units_sold(sales: pd.DataFrame) -> pd.Series:
    """
    Daily total units sold.
    """
    return sales.groupby("date")["units"].sum()


def calculate_average_selling_price(
    sales: pd.DataFrame,
) -> pd.Series:
    """
    Revenue-weighted average realized selling price.

    ASP = Total Revenue / Total Units Sold
    """
    daily = sales.groupby("date").agg(
        revenue=("revenue", "sum"),
        units=("units", "sum"),
    )

    return daily["revenue"] / daily["units"]


def calculate_marketing_spend(
    marketing: pd.DataFrame,
) -> pd.Series:
    """
    Daily total marketing spend.
    """
    return marketing.groupby("date")["spend"].sum()


def calculate_conversion_rate(
    marketing: pd.DataFrame,
) -> pd.Series:
    """
    Daily conversion rate.

    Conversion Rate =
        Total Conversions / Total Clicks
    """
    daily = marketing.groupby("date").agg(
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
    )

    return daily["conversions"] / daily["clicks"]


def calculate_stockout_rate(
    inventory: pd.DataFrame,
) -> pd.Series:
    """
    Daily stockout rate.

    We use 24 hours as the theoretical available time
    for each product-region observation.

    Stockout Rate =
        Total Stockout Hours /
        (Number of observations × 24)
    """
    daily = inventory.groupby("date").agg(
        stockout_hours=("stockout_hours", "sum"),
        observations=("stockout_hours", "size"),
    )

    available_hours = daily["observations"] * 24

    return daily["stockout_hours"] / available_hours


def calculate_daily_kpis(
    sales: pd.DataFrame,
    marketing: pd.DataFrame,
    inventory: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the canonical daily KPI table.
    """

    revenue = calculate_revenue(sales)
    units = calculate_units_sold(sales)
    asp = calculate_average_selling_price(sales)

    marketing_spend = calculate_marketing_spend(marketing)
    conversion_rate = calculate_conversion_rate(marketing)

    stockout_rate = calculate_stockout_rate(inventory)

    kpis = pd.concat(
        [
            revenue.rename("revenue"),
            units.rename("units_sold"),
            asp.rename("average_selling_price"),
            marketing_spend.rename("marketing_spend"),
            conversion_rate.rename("conversion_rate"),
            stockout_rate.rename("stockout_rate"),
        ],
        axis=1,
    ).sort_index()

    return kpis.reset_index()