from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataSource:
    name: str
    filename: str
    required_columns: tuple[str, ...]
    date_column: str | None = None
    date_format: str | None = None

    @property
    def path(self) -> Path:
        return Path("data/raw") / self.filename


SALES_SOURCE = DataSource(
    name="sales",
    filename="sales.csv",
    required_columns=(
        "date",
        "order_id",
        "product_id",
        "product_name",
        "category",
        "region",
        "channel",
        "units",
        "list_price",
        "discount_pct",
        "net_unit_price",
        "revenue",
        "gross_margin",
    ),
    date_column="date",
    date_format="%Y-%m-%d",
)


MARKETING_SOURCE = DataSource(
    name="marketing",
    filename="marketing.csv",
    required_columns=(
        "date",
        "campaign_id",
        "channel",
        "campaign_type",
        "region",
        "impressions",
        "clicks",
        "spend",
        "conversions",
    ),
    date_column="date",
    date_format="%Y-%m-%d",
)


INVENTORY_SOURCE = DataSource(
    name="inventory",
    filename="inventory.csv",
    required_columns=(
        "date",
        "product_id",
        "region",
        "warehouse",
        "opening_stock",
        "units_received",
        "units_sold",
        "closing_stock",
        "stockout_hours",
    ),
    date_column="date",
    date_format="%Y-%m-%d",
)


EVENTS_SOURCE = DataSource(
    name="business_events",
    filename="business_events.csv",
    required_columns=(
        "event_date",
        "event_name",
        "event_type",
        "description",
    ),
    date_column="event_date",
    date_format="%Y-%m-%d",
)


KPI_SOURCE = DataSource(
    name="kpi_dictionary",
    filename="kpi_dictionary.csv",
    required_columns=(
        "kpi_name",
        "definition",
        "formula",
        "primary_drivers",
        "refresh_cadence",
        "materiality_threshold",
        "source",
        "owner",
    ),
)


METADATA_SOURCE = DataSource(
    name="source_metadata",
    filename="source_metadata.csv",
    required_columns=(
        "source",
        "description",
        "grain",
        "refresh_cadence",
        "refresh_time",
        "owner",
        "data_quality_score",
        "security_scope",
    ),
)


ALL_SOURCES = (
    SALES_SOURCE,
    MARKETING_SOURCE,
    INVENTORY_SOURCE,
    EVENTS_SOURCE,
    KPI_SOURCE,
    METADATA_SOURCE,
)