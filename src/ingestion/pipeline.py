from .loaders import load_all_sources, validate_basic_quality
from .schemas import ALL_SOURCES


def run_ingestion() -> dict:
    datasets = load_all_sources()

    quality_report = {}

    for source in ALL_SOURCES:
        quality_report[source.name] = validate_basic_quality(
            datasets[source.name],
            source,
        )

    return {
        "datasets": datasets,
        "quality_report": quality_report,
    }


if __name__ == "__main__":
    result = run_ingestion()

    print("\n=== Narrate IQ Data Ingestion ===\n")

    for source_name, report in result["quality_report"].items():
        print(f"Source: {source_name}")
        print(f"  Rows:           {report['rows']:,}")
        print(f"  Columns:        {report['columns']}")
        print(f"  Duplicates:     {report['duplicate_rows']:,}")
        print(f"  Missing values: {report['missing_values']:,}")
        print(f"  Date range:     {report['date_min']} → {report['date_max']}")
        print()