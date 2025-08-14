import polars as pl
from multimodal_communication import S3CloudHelper
from typing import Literal, Any
from typing import Dict, Type


class SGORegistry:
    """Registry for data collection in S3 from Sports Game Odds API using Delta Lake."""

    def __init__(self, schema_dict: dict[str, Dict[str, Type[Any]]], bucket_name: str = 'sgo-api-data', region: str = "us-east-2"):
        self.bucket_name = bucket_name
        self.region = region
        self.s3_helper = S3CloudHelper(region_name=region)
        self.schemas = schema_dict

    def _delta_path(self, sport: str, table: str) -> str:
        # Construct the S3 Delta Lake table path (folder)
        return f"s3://{self.bucket_name}/{sport}-data/{table}/"

    def _load_lazy_frame(self, sport: str, table: str, columns: list[str]) -> pl.LazyFrame:
        """Loads a single Delta table as a lazy Polars DataFrame."""
        delta_path = self._delta_path(sport, table)
        return pl.scan_delta(delta_path, storage_options={"AWS_REGION": self.region}).select(columns)

    def load(
        self,
        primary_table: str,
        sport: Literal["football", "baseball", "basketball", "hockey"],
        columns: list[str] | None = None,
        filters: list | None = None,
        join_tables: list[str] | None = None
    ) -> pl.DataFrame:
        """
        Loads and joins tables based on a Pydantic schema registry, assuming identical column names for joins.

        :param primary_table: The main table to start the query from.
        :param sport: The sport to query data for.
        :param columns: A list of specific columns to select. If None, all columns from all joined tables are selected.
        :param filters: A list of Polars expressions to filter the data (e.g., `[pl.col("season") == 2024]`).
        :param join_tables: A list of other tables to join with the primary table.
        :return: A Polars DataFrame containing the collected data.
        """

        # Step 1: Identify all tables needed and their required columns
        all_tables_needed = {primary_table}
        all_tables_needed.update(list(self.schemas[sport].keys()))
            
        columns_to_load = {}
        for tbl in all_tables_needed:
            schema_model = self.schemas[sport][tbl]
            table_cols = list(schema_model.model_fields.keys())
            columns_to_load[tbl] = table_cols

        # Step 2: Load all required tables lazily
        lazy_frames = {}
        for tbl, cols in columns_to_load.items():
            lazy_frames[tbl] = self._load_lazy_frame(sport, tbl, cols)

        # Step 3: Start with the primary table and iteratively join others
        # Note, if we ever get a lot of tables this may slow the process down,
        # As we have to load in all the tables, even if we don't need them.
        result = lazy_frames[primary_table]
        if columns:
            for tbl_to_join in list(self.schemas[sport].keys()):
                lazy_df_to_join = lazy_frames[tbl_to_join]
                
                # Find the common columns for joining
                join_keys = list(set(result.columns) & set(lazy_df_to_join.columns))
                
                if join_keys:
                    result = result.join(lazy_df_to_join, on=join_keys, how="inner")

        # Step 4: Apply optional filters
        if filters:
            combined_filter = pl.all_horizontal(filters) if len(filters) > 1 else filters[0]
            result = result.filter(combined_filter)

        # Step 5: Select the user-requested columns before collection to optimize memory
        if columns is not None:
            final_columns = [col for col in columns if col in result.columns]
            if not final_columns:
                raise ValueError("None of the requested columns exist in the joined table.")
            result = result.select(final_columns)

        return result
        