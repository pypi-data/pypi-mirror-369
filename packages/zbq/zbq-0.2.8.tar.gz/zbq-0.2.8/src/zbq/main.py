from polars.exceptions import PolarsError
from google.cloud import bigquery
from zbq.base import BaseClientManager, ZbqAuthenticationError, ZbqOperationError
import polars as pl
import re
import tempfile
import os
from typing import Dict, Any


class BigQueryHandler(BaseClientManager):
    """Enhanced Google BigQuery handler with improved error handling and logging"""

    def __init__(
        self,
        project_id: str = "",
        default_timeout: int = 300,
        log_level: str = "INFO",
    ):
        super().__init__(project_id, log_level)
        self.default_timeout = default_timeout

    def _create_client(self):
        return bigquery.Client(project=self.project_id)

    def _substitute_parameters(self, query: str, parameters: Dict[str, Any] | None = None) -> str:
        """
        Substitute parameters in a SQL query using @param_name syntax.
        
        Args:
            query: SQL query string with @param_name placeholders
            parameters: Dictionary mapping parameter names to values
            
        Returns:
            Query string with parameters substituted
            
        Raises:
            ZbqOperationError: If parameter substitution fails
        """
        if not parameters:
            return query
            
        # Validate parameters dict
        if not isinstance(parameters, dict):
            raise ZbqOperationError("Parameters must be a dictionary")
        
        # Validate parameter names (only alphanumeric and underscore allowed)
        for param_name in parameters.keys():
            if not isinstance(param_name, str) or not re.match(r'^\w+$', param_name):
                raise ZbqOperationError(f"Invalid parameter name: '{param_name}'. Parameter names must contain only letters, numbers, and underscores.")
            
        try:
            # Find all @param_name patterns in the query
            param_pattern = r'@(\w+)'
            found_params = re.findall(param_pattern, query)
            
            # Validate that all found parameters have values
            missing_params = [param for param in found_params if param not in parameters]
            if missing_params:
                raise ZbqOperationError(
                    f"Missing values for parameters: {', '.join(missing_params)}"
                )
            
            # Substitute parameters
            result_query = query
            for param_name in found_params:
                param_value = parameters[param_name]
                
                # Handle different parameter types
                if isinstance(param_value, str):
                    # For string values, check if it looks like a table/dataset identifier
                    if '.' in param_value and not param_value.startswith('`'):
                        # Likely a table identifier, add backticks
                        substituted_value = f"`{param_value}`"
                    else:
                        # Regular string value, add quotes
                        substituted_value = f"'{param_value.replace('\'', '\'\'')}'"
                elif isinstance(param_value, (int, float)):
                    # Numeric values don't need quotes
                    substituted_value = str(param_value)
                elif param_value is None:
                    substituted_value = "NULL"
                elif isinstance(param_value, bool):
                    substituted_value = "TRUE" if param_value else "FALSE"
                else:
                    # For other types, convert to string and quote
                    substituted_value = f"'{str(param_value).replace('\'', '\'\'')}'"
                
                # Replace all occurrences of @param_name
                result_query = result_query.replace(f'@{param_name}', substituted_value)
            
            return result_query
            
        except Exception as e:
            if isinstance(e, ZbqOperationError):
                raise
            raise ZbqOperationError(f"Parameter substitution failed: {str(e)}")

    def validate(self):
        """Optional helper: raise if ADC or project_id not set"""
        if not self._check_adc():
            raise RuntimeError(
                "Missing ADC. Run: gcloud auth application-default login"
            )
        if not self.project_id:
            raise RuntimeError("Project ID not set.")

    def read(
        self,
        query: str | None = None,
        timeout: int | None = None,
        parameters: Dict[str, Any] | None = None,
    ):
        """
        Execute a SQL query and return results as a Polars DataFrame.

        Args:
            query (str): SQL query string. Can include @param_name placeholders.
            timeout (int, optional): Query timeout in seconds. Uses default_timeout if not specified.
            parameters (Dict[str, Any], optional): Parameters for @param_name substitution in query.

        Returns:
            pl.DataFrame: Query results as a Polars DataFrame.

        Raises:
            ValueError: If query is empty.
            ZbqOperationError: If parameter substitution fails.
            TimeoutError: If query times out.
        """

        if query:
            try:
                return self._query(query, timeout, parameters)
            except TimeoutError as e:
                print(f"Read operation timed out: {e}")
                raise
            except Exception as e:
                print(f"Read operation failed: {e}")
                raise
        else:
            raise ValueError("Query is empty.")

    def insert(self, query: str, timeout: int | None = None, parameters: Dict[str, Any] | None = None):
        return self.read(query, timeout, parameters)

    def update(self, query: str, timeout: int | None = None, parameters: Dict[str, Any] | None = None):
        return self.read(query, timeout, parameters)

    def delete(self, query: str, timeout: int | None = None, parameters: Dict[str, Any] | None = None):
        return self.read(query, timeout, parameters)

    def write(
        self,
        df: pl.DataFrame,
        full_table_path: str,
        write_type: str = "append",
        warning: bool = True,
        create_if_needed: bool = True,
        timeout: int | None = None,
    ):
        self._check_requirements(df, full_table_path)
        return self._write(
            df, full_table_path, write_type, warning, create_if_needed, timeout
        )

    def _check_requirements(self, df, full_table_path):
        if df.is_empty() or not full_table_path:
            missing = []
            if df.is_empty():
                missing.append("df")
            if not full_table_path:
                missing.append("full_table_path")
            raise ValueError(f"Missing required argument(s): {', '.join(missing)}")

    def _query(self, query: str, timeout: int | None = None, parameters: Dict[str, Any] | None = None) -> pl.DataFrame | pl.Series:
        timeout = timeout or self.default_timeout
        
        # Substitute parameters if provided
        if parameters:
            query = self._substitute_parameters(query, parameters)

        try:
            # Use fresh client for each query to eliminate shared state issues
            with self._fresh_client() as client:
                query_job = client.query(query)

                if re.search(r"\b(insert|update|delete)\b", query, re.IGNORECASE):
                    try:
                        query_job.result(timeout=timeout)
                        return pl.DataFrame(
                            {"status": ["OK"], "job_id": [query_job.job_id]}
                        )
                    except Exception as e:
                        if "timeout" in str(e).lower():
                            raise TimeoutError(
                                f"Query timed out after {timeout} seconds"
                            )
                        raise

                try:
                    rows = query_job.result(timeout=timeout).to_arrow(
                        progress_bar_type=None
                    )
                    df = pl.from_arrow(rows)
                except Exception as e:
                    if "timeout" in str(e).lower():
                        raise TimeoutError(f"Query timed out after {timeout} seconds")
                    raise

        except PolarsError as e:
            print(f"PanicException: {e}")
            print("Retrying with Pandas DF")
            try:
                with self._fresh_client() as client:
                    query_job = client.query(query)
                    pandas_df = query_job.result(timeout=timeout).to_dataframe(
                        progress_bar_type=None
                    )
                    df = pl.from_pandas(pandas_df)
            except Exception as e:
                if "timeout" in str(e).lower():
                    raise TimeoutError(f"Query timed out after {timeout} seconds")
                raise

        return df

    def _write(
        self,
        df: pl.DataFrame,
        full_table_path: str,
        write_type: str = "append",
        warning: bool = True,
        create_if_needed: bool = True,
        timeout: int | None = None,
    ):
        timeout = timeout or self.default_timeout
        destination = full_table_path
        temp_file = tempfile.NamedTemporaryFile(suffix=".parquet", delete=False)
        temp_file_path = temp_file.name
        temp_file.close()

        try:
            df.write_parquet(temp_file_path)

            if write_type == "truncate" and warning:
                try:
                    user_warning = input(
                        "You are about to overwrite a table. Continue? (y/n): "
                    )
                    if user_warning.lower() != "y":
                        return "CANCELLED"
                except (EOFError, KeyboardInterrupt):
                    print("\nOperation cancelled by user")
                    return "CANCELLED"

            write_disp = (
                bigquery.WriteDisposition.WRITE_TRUNCATE
                if write_type == "truncate"
                else bigquery.WriteDisposition.WRITE_APPEND
            )

            create_disp = (
                bigquery.CreateDisposition.CREATE_IF_NEEDED
                if create_if_needed
                else bigquery.CreateDisposition.CREATE_NEVER
            )

            # Use fresh client for write operation to eliminate shared state issues
            with self._fresh_client() as client:
                with open(temp_file_path, "rb") as source_file:
                    job = client.load_table_from_file(
                        source_file,
                        destination=destination,
                        project=self.project_id,
                        job_config=bigquery.LoadJobConfig(
                            source_format=bigquery.SourceFormat.PARQUET,
                            write_disposition=write_disp,
                            create_disposition=create_disp,
                        ),
                    )
                    # Add timeout to prevent hanging on job.result()
                    try:
                        result = job.result(timeout=timeout)
                        return result.state
                    except Exception as e:
                        if "timeout" in str(e).lower():
                            raise TimeoutError(
                                f"Write operation timed out after {timeout} seconds"
                            )
                        raise

        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass  # Ignore cleanup errors
