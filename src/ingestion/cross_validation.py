import pandas as pd


class CrossSourceValidationError(Exception):
    """Raised when cross-source business rules fail."""


def validate_referential_integrity(
    sales: pd.DataFrame,
    inventory: pd.DataFrame,
    marketing: pd.DataFrame,
) -> dict:

    sales_products = set(sales["product_id"].unique())
    inventory_products = set(inventory["product_id"].unique())

    missing_products = sales_products - inventory_products

    sales_regions = set(sales["region"].unique())
    inventory_regions = set(inventory["region"].unique())
    marketing_regions = set(marketing["region"].unique())

    missing_inventory_regions = sales_regions - inventory_regions
    missing_marketing_regions = sales_regions - marketing_regions

    return {
        "sales_products_not_in_inventory": sorted(missing_products),
        "sales_regions_not_in_inventory": sorted(
            missing_inventory_regions
        ),
        "sales_regions_not_in_marketing": sorted(
            missing_marketing_regions
        ),
    }


def validate_sales_arithmetic(
    sales: pd.DataFrame,
    tolerance: float = 0.05,
) -> dict:

    expected_revenue = (
        sales["units"] * sales["net_unit_price"]
    )

    difference = (
        sales["revenue"] - expected_revenue
    ).abs()

    invalid_rows = difference > tolerance

    return {
        "rows_checked": len(sales),
        "invalid_rows": int(invalid_rows.sum()),
        "max_difference": float(difference.max()),
        "mean_difference": float(difference.mean()),
        "p95_difference": float(difference.quantile(0.95)),
    }


def validate_inventory_arithmetic(
    inventory: pd.DataFrame,
) -> dict:

    expected_closing = (
        inventory["opening_stock"]
        + inventory["units_received"]
        - inventory["units_sold"]
    )

    difference = (
        inventory["closing_stock"] - expected_closing
    ).abs()

    invalid_rows = difference > 0.01

    return {
        "rows_checked": len(inventory),
        "invalid_rows": int(invalid_rows.sum()),
        "max_difference": float(difference.max()),
    }


def validate_marketing_logic(
    marketing: pd.DataFrame,
) -> dict:

    invalid_impressions = (
        marketing["clicks"] > marketing["impressions"]
    )

    invalid_conversions = (
        marketing["conversions"] > marketing["clicks"]
    )

    invalid_spend = (
        marketing["spend"] < 0
    )

    return {
        "clicks_gt_impressions": int(
            invalid_impressions.sum()
        ),
        "conversions_gt_clicks": int(
            invalid_conversions.sum()
        ),
        "negative_spend": int(
            invalid_spend.sum()
        ),
    }