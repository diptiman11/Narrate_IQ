from .cross_validation import (
    validate_inventory_arithmetic,
    validate_marketing_logic,
    validate_referential_integrity,
    validate_sales_arithmetic,
)
from .loaders import load_all_sources


def main():

    datasets = load_all_sources()

    sales = datasets["sales"]
    inventory = datasets["inventory"]
    marketing = datasets["marketing"]

    print("\n=== Cross-Source Validation ===\n")

    print("1. Referential Integrity")
    result = validate_referential_integrity(
        sales,
        inventory,
        marketing,
    )
    print(result)

    print("\n2. Sales Arithmetic")
    print(
        validate_sales_arithmetic(sales)
    )

    print("\n3. Inventory Arithmetic")
    print(
        validate_inventory_arithmetic(inventory)
    )

    print("\n4. Marketing Logic")
    print(
        validate_marketing_logic(marketing)
    )


if __name__ == "__main__":
    main()