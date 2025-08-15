import re
from typing import Optional, Any, Union, Tuple, Callable, List
from urllib.parse import urlparse, parse_qsl
import os.path
import ast
from datetime import datetime, timedelta, timezone
from functools import wraps
import json
import csv

from jsonpath_ng import parse as jsonpath_parse
import requests
from optics_framework.common.config_handler import ConfigHandler
from optics_framework.common.logging_config import internal_logger
from optics_framework.common.session_manager import Session
from optics_framework.common.models import ApiData, ElementData
import pandas as pd
from io import StringIO

NO_SESSION_PRESENT = "Session is None after ensure_session call."


def raw_params(*indices):
    """Decorator to mark parameter indices that should remain unresolved."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper._raw_param_indices = indices  # pylint: disable=protected-access  # type: ignore[attr-defined]
        return wrapper

    return decorator


class FlowControl:
    """Manages control flow operations (loops, conditions, data) for a session."""

    def __init__(
        self,
        session: Session,
        keyword_map: dict[str, Callable[..., Any]]
    ) -> None:
        self.session = session
        # modules is a ModuleData instance
        self.modules = self.session.modules
        self.keyword_map = keyword_map

    def _ensure_session(self) -> None:
        """Ensures a Session instance is set."""
        if self.session is None:
            raise ValueError(
                "FlowControl.session is not set. Please assign a valid session instance before using FlowControl."
            )

    def _resolve_param(self, param: str) -> str:
        """Resolve ${variable} references from session.elements."""
        if (
            not isinstance(param, str)
            or not param.startswith("${")
            or not param.endswith("}")
        ):
            return str(param)
        if self.session is None:
            raise ValueError("Session is None in resolve_param.")
        var_name = param[2:-1].strip()
        # Access the shared elements dictionary from the session
        elements = getattr(self.session, "elements", None)
        if not isinstance(elements, ElementData):
            raise ValueError("Session elements is not an ElementData instance or is None.")
        value = elements.get_element(var_name)
        if value is None:
            raise ValueError(f"Variable '{param}' not found in elements dictionary")
        return str(value)

    def execute_module(self, module_name: str) -> List[Any]:
        """Executes a module's keywords using the session's keyword_map."""
        self._ensure_session()
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        if module_name not in self.modules.modules:
            raise ValueError(f"Module '{module_name}' not found in modules.")
        results = []
        module_def = self.modules.get_module_definition(module_name)
        if not module_def:
            raise ValueError(f"No definition found for module '{module_name}'.")
        for keyword, params in module_def:
            func_name = "_".join(keyword.split()).lower()
            method = self.keyword_map.get(func_name)
            if method is None:
                raise ValueError(f"Keyword '{keyword}' not found in keyword_map.")
            try:
                raw_indices = getattr(method, "_raw_param_indices", [])
                resolved_params = [
                    param if i in raw_indices else self._resolve_param(param)
                    for i, param in enumerate(params)
                ]
                internal_logger.debug(
                    f"Executing {keyword} with params: {resolved_params}"
                )
                result = method(*resolved_params)
                results.append(result)
            except Exception as e:
                internal_logger.error(f"Error executing keyword '{keyword}': {e}")
                raise  # Propagate exception to fail the test
        return results

    @raw_params(1, 3, 5, 7, 9, 11, 13, 15)
    def run_loop(self, target: str, *args: str) -> List[Any]:
        """Runs a loop over a target module, either by count or with variables."""
        internal_logger.debug(f"[RUN_LOOP] Called with target={target}, args={args}")
        self._ensure_session()
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        if len(args) == 1:
            internal_logger.debug(f"[RUN_LOOP] Looping by count: {args[0]}")
            return self._loop_by_count(target, args[0])
        internal_logger.debug(f"[RUN_LOOP] Looping with variables: {args}")
        return self._loop_with_variables(target, args)

    def _loop_by_count(self, target: str, count_str: str) -> List[Any]:
        """Runs a loop a specified number of times."""
        internal_logger.debug(f"[_LOOP_BY_COUNT] target={target}, count_str={count_str}")
        try:
            iterations = int(count_str)
            if iterations < 1:
                raise ValueError("Iteration count must be at least 1.")
        except ValueError as e:
            if str(e) == "Iteration count must be at least 1.":
                raise
            internal_logger.error(f"[_LOOP_BY_COUNT] Invalid count_str: {count_str}")
            raise ValueError(f"Expected an integer for loop count, got '{count_str}'.")

        results = []
        for i in range(iterations):
            internal_logger.debug(f"[_LOOP_BY_COUNT] Iteration {i + 1} of {iterations} for target '{target}'")
            result = self.execute_module(target)
            results.append(result)
        internal_logger.debug(f"[_LOOP_BY_COUNT] Completed {iterations} iterations for target '{target}'")
        return results

    def _loop_with_variables(self, target: str, args: Tuple[str, ...]) -> List[Any]:
        """Runs a loop with variable-iterable pairs."""
        internal_logger.debug(f"[_LOOP_WITH_VARIABLES] target={target}, args={args}")
        if len(args) % 2 != 0:
            internal_logger.error(f"[_LOOP_WITH_VARIABLES] Uneven number of arguments for variable-iterable pairs: {args}")
            raise ValueError("Expected an even number of arguments for variable-iterable pairs.")

        variables = args[0::2]
        iterables = args[1::2]
        internal_logger.debug(f"[_LOOP_WITH_VARIABLES] variables={variables}, iterables={iterables}")
        var_names, parsed_iterables = self._parse_variable_iterable_pairs(variables, iterables)
        min_length = min(len(lst) for lst in parsed_iterables)
        internal_logger.debug(f"[_LOOP_WITH_VARIABLES] min_length={min_length}, var_names={var_names}")
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        runner_elements = getattr(self.session, "elements", None)
        if not isinstance(runner_elements, ElementData):
            runner_elements = ElementData()
            setattr(self.session, "elements", runner_elements)

        results = []
        for i in range(min_length):
            internal_logger.debug(f"[_LOOP_WITH_VARIABLES] Iteration {i + 1} of {min_length}")
            for var_name, iterable_values in zip(var_names, parsed_iterables):
                value = iterable_values[i]
                internal_logger.debug(f"[_LOOP_WITH_VARIABLES] Setting {var_name} = {value}")
                runner_elements.add_element(var_name, value)
            internal_logger.debug(f"[_LOOP_WITH_VARIABLES] Executing target '{target}'")
            result = self.execute_module(target)
            results.append(result)
        internal_logger.debug(f"[_LOOP_WITH_VARIABLES] Completed {min_length} iterations for target '{target}'")
        return results

    def _parse_variable_iterable_pairs(
        self, variables: Tuple[str, ...], iterables: Tuple[str, ...]
    ) -> Tuple[List[str], List[List[Any]]]:
        """Parses variable names and their corresponding iterables."""
        var_names = self._parse_variable_names(variables)
        parsed_iterables = self._parse_iterables(variables, iterables)
        return var_names, parsed_iterables

    def _parse_variable_names(self, variables: Tuple[str, ...]) -> List[str]:
        """Extracts and cleans variable names from the input tuple."""
        var_names = []
        for variable in variables:
            var_name = variable.strip()
            if var_name.startswith("${") and var_name.endswith("}"):
                var_name = var_name[2:-1].strip()
            else:
                internal_logger.warning(
                    f"[RUN LOOP] Expected variable in format '${{name}}', got '{variable}'. Using as is."
                )
            var_names.append(var_name)
        return var_names

    def _parse_iterables(
        self, variables: Tuple[str, ...], iterables: Tuple[str, ...]
    ) -> List[List[Any]]:
        """Parses iterables into lists, handling JSON strings and validating input."""
        parsed_iterables = []
        for i, iterable in enumerate(iterables):
            parsed = self._parse_single_iterable(iterable, variables[i])
            if not parsed:
                raise ValueError(f"Iterable for variable '{variables[i]}' is empty.")
            parsed_iterables.append(parsed)
        return parsed_iterables

    def _parse_single_iterable(self, iterable: Any, variable: str) -> List[Any]:
        """Parses a single iterable, converting JSON strings or validating lists."""
        if isinstance(iterable, str):
            try:
                values = json.loads(iterable)
                if not isinstance(values, list):
                    raise ValueError(
                        f"Iterable '{iterable}' for variable '{variable}' must resolve to a list."
                    )
                return values
            except json.JSONDecodeError:
                raise ValueError(
                    f"Invalid iterable format for variable '{variable}': '{iterable}'."
                )
        elif isinstance(iterable, list):
            return iterable
        else:
            raise ValueError(
                f"Expected a list or JSON string for iterable of variable '{variable}', got {type(iterable).__name__}."
            )

    def condition(self, *args: str) -> Optional[List[Any]]:
        """Evaluates conditions and executes corresponding targets."""
        internal_logger.debug(f"[CONDITION] Called with args={args}")
        self._ensure_session()
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        if not args:
            internal_logger.error("[CONDITION] No condition-target pairs provided.")
            raise ValueError("No condition-target pairs provided.")
        pairs, else_target = self._split_condition_args(args)
        internal_logger.debug(f"[CONDITION] Parsed pairs={pairs}, else_target={else_target}")
        return self._evaluate_conditions(pairs, else_target)

    def _split_condition_args(
        self, args: Tuple[str, ...]
    ) -> Tuple[List[Tuple[str, str]], Optional[str]]:
        """Splits args into condition-target pairs and an optional else target."""
        pairs = []
        else_target = None
        if len(args) % 2 == 1:
            for i in range(0, len(args) - 1, 2):
                pairs.append((args[i], args[i + 1]))
            else_target = args[-1]
        else:
            for i in range(0, len(args), 2):
                pairs.append((args[i], args[i + 1]))
        return pairs, else_target

    def _evaluate_conditions(
        self, pairs: List[Tuple[str, str]], else_target: Optional[str]
    ) -> Optional[List[Any]]:
        """Evaluates conditions and executes the first true target's module."""
        internal_logger.debug(f"[_EVALUATE_CONDITIONS] pairs={pairs}, else_target={else_target}")
        for cond, target in pairs:
            cond_str = cond.strip()
            internal_logger.debug(f"[_EVALUATE_CONDITIONS] Evaluating condition: '{cond_str}' for target '{target}'")
            if not cond_str:
                continue
            if self._is_condition_true(cond_str):
                internal_logger.debug(f"[_EVALUATE_CONDITIONS] Condition '{cond_str}' is True. Executing target '{target}'.")
                return self.execute_module(target)
            internal_logger.debug(f"[_EVALUATE_CONDITIONS] Condition '{cond_str}' is False.")
        if else_target is not None:
            internal_logger.debug(f"[_EVALUATE_CONDITIONS] No condition met. Executing ELSE target '{else_target}'.")
            return self.execute_module(else_target)
        internal_logger.debug("[_EVALUATE_CONDITIONS] No condition met and no ELSE target provided.")
        return None

    def _is_condition_true(self, cond: str) -> bool:
        """Evaluates if a condition is true."""
        try:
            resolved_cond = self._resolve_condition(cond)
            return bool(self._safe_eval(resolved_cond))
        except Exception as e:
            raise ValueError(f"Error evaluating condition '{cond}': {e}")

    def _resolve_condition(self, cond: str) -> str:
        """Resolves variables in a condition string."""
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        runner_elements = getattr(self.session, "elements", None)
        if not isinstance(runner_elements, ElementData):
            raise ValueError("Session elements is not an ElementData instance or is None.")
        pattern = re.compile(r"\$\{([^}]+)\}")

        def replacer(match):
            var_name = match.group(1).strip()
            value = runner_elements.get_element(var_name)
            if value is None:
                raise ValueError(
                    f"Variable '{var_name}' not found for condition resolution."
                )
            return f"'{value}'" if isinstance(value, str) else str(value)

        return pattern.sub(replacer, cond)

    @raw_params(0)
    def read_data(
        self, input_element: str, file_path: Union[str, List[Any]], query: str = ""
    ) -> List[Any]:
        """
        Reads tabular data from a CSV file, JSON file, environment variable, or a 2D list,
        applies optional filtering and column selection, and stores the result in the session's elements.

        Parameters:
            input_element (str): The name or identifier for the element to store the data under.
            file_path (Union[str, List[Any]]):
                - Path to a CSV or JSON file (relative or absolute).
                - "ENV:<env_var_name>" to read data from an environment variable (supports JSON or CSV content).
                - A 2D list (first row as headers, subsequent rows as data).
            query (str, optional):
                Query string to filter and/or select columns from the data.
                - Filtering: e.g., "col1 == 'val1'" or "col1 == 'val1' and col2 == 'val2'"
                - Column selection: "select=col1,col2"
                - Combine with semicolon: "col1 == 'val1';select=col2"
                If empty, all rows and columns are returned.

        Returns:
            List[Any]:
                - If a single row is selected, returns a list of string values for that row.
                - If multiple rows are selected, returns a list of lists (each inner list is a row of string values).

        Raises:
            ValueError: If session is not present, file_path is invalid, environment variable is missing,
                        file extension is unsupported, query is invalid, or selected columns are missing.

        Notes:
            - All returned values are converted to strings.
            - Data is stored in the session's elements as a comma-separated string.
            - Only CSV and JSON file formats are supported.
        """
        internal_logger.debug(f"[READ_DATA] Called with input_element={input_element}, file_path={file_path}, query={query}")
        self._ensure_session()
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        elem_name = self._extract_element_name(input_element)
        internal_logger.debug(f"[READ_DATA] Extracted element name: {elem_name}")
        # Load data as DataFrame (CSV, 2D list, or JSON)
        df = None
        if isinstance(file_path, list):
            data = file_path
            internal_logger.debug(f"[READ_DATA] Loading data from list, first row as headers: {data[0] if data and isinstance(data[0], list) else data}")
            if not data or not isinstance(data, list) or not data[0]:
                df = pd.DataFrame()
            else:
                df = pd.DataFrame(data[1:], columns=data[0])
        elif isinstance(file_path, str):
            # ENV:<env_var_name> support
            if file_path.startswith('ENV:'):
                env_var = file_path[4:]
                env_data = os.environ.get(env_var)
                internal_logger.debug(f"[READ_DATA] Loading data from environment variable: {env_var}")
                if env_data is None:
                    raise ValueError(f"Environment variable '{env_var}' not found.")
                # Try JSON first
                try:
                    json_data = json.loads(env_data)
                    internal_logger.debug(f"[READ_DATA] Parsed environment variable as JSON: {json_data}")
                    if isinstance(json_data, dict):
                        for v in json_data.values():
                            if isinstance(v, list):
                                json_data = v
                                break
                        if isinstance(json_data, dict):
                            json_data = [json_data]
                    df = pd.json_normalize(json_data)
                except Exception:
                    internal_logger.debug("[READ_DATA] Failed to parse environment variable as JSON, trying CSV.")
                    try:
                        df = pd.read_csv(StringIO(env_data))
                        internal_logger.debug("[READ_DATA] Parsed environment variable as CSV.")
                        # If CSV parsing yields an empty DataFrame, treat as direct value
                        if df.empty:
                            runner_elements = self.session.elements
                            if isinstance(runner_elements, ElementData):
                                internal_logger.debug("[READ_DATA] Storing direct env value under element '%s': %s", elem_name, env_data)
                                runner_elements.add_element(elem_name, env_data)
                            else:
                                internal_logger.warning("[READ_DATA] Cannot store direct env value: session.elements is not an ElementData instance.")
                            return [env_data]
                    except ValueError:
                        internal_logger.debug("[READ_DATA] Failed to parse environment variable as CSV, treating as direct value.")
                        # If not JSON or CSV, treat as direct value
                        runner_elements = self.session.elements
                        if isinstance(runner_elements, ElementData):
                            internal_logger.debug("[READ_DATA] Storing direct env value under element '%s': %s", elem_name, env_data)
                            runner_elements.add_element(elem_name, env_data)
                        else:
                            internal_logger.warning("[READ_DATA] Cannot store direct env value: session.elements is not an ElementData instance.")
                        return [env_data]
            else:
                # Handle relative path: prepend project_path if not absolute
                if not os.path.isabs(file_path):
                    config_handler = ConfigHandler.get_instance()
                    project_path = getattr(config_handler.config, 'project_path', None)
                    internal_logger.debug(f"[READ_DATA] Resolving relative file path. Project path: {project_path}")
                    if project_path:
                        file_path = os.path.join(project_path, file_path)
                        internal_logger.debug(f"[READ_DATA] Resolved file path: {file_path}")
                ext = os.path.splitext(file_path)[-1].lower()
                internal_logger.debug(f"[READ_DATA] File extension: {ext}")
                # Explicit file existence check for CSV/JSON
                if ext in ['.csv', '.json']:
                    if not os.path.exists(file_path):
                        internal_logger.error(f"[READ_DATA] File not found: {file_path}")
                        raise FileNotFoundError(f"File '{file_path}' not found.")
                if ext == '.csv':
                    df = pd.read_csv(file_path)
                    internal_logger.debug(f"[READ_DATA] Loaded CSV file: {file_path}")
                elif ext == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    internal_logger.debug(f"[READ_DATA] Loaded JSON file: {file_path}")
                    # If the JSON is a dict with a single top-level list, use that list
                    if isinstance(json_data, dict):
                        for v in json_data.values():
                            if isinstance(v, list):
                                json_data = v
                                break
                        if isinstance(json_data, dict):
                            json_data = [json_data]
                    df = pd.json_normalize(json_data)
                else:
                    internal_logger.error(f"[READ_DATA] Unsupported file extension: {ext}")
                    raise ValueError(f"Unsupported file extension: {ext}")
        else:
            internal_logger.error("[READ_DATA] file_path must be a list or a file path string.")
            raise ValueError("file_path must be a list or a file path string.")
        # Parse query
        select_cols = None
        filter_expr = None
        # Ensure all columns are string for consistent querying
        if df is not None and not df.empty:
            df = df.astype(str)
        if query:
            internal_logger.debug(f"[READ_DATA] Parsing query: {query}")
            # Resolve ${...} variables inside the query string
            def resolve_query_vars(q):
                pattern = re.compile(r"\$\{([^}]+)\}")
                runner_elements = getattr(self.session, "elements", None)
                if not isinstance(runner_elements, ElementData):
                    runner_elements = ElementData()
                    setattr(self.session, "elements", runner_elements)
                def replacer(match):
                    var_name = match.group(1).strip()
                    value = runner_elements.get_element(var_name)
                    internal_logger.debug(f"[READ_DATA] Resolving variable in query: {var_name} -> {value}")
                    if value is None:
                        raise ValueError(f"Variable '{var_name}' not found in elements for query resolution.")
                    # Check if the variable is already inside quotes in the query
                    start, end = match.span()
                    before = q[start-1] if start > 0 else ''
                    after = q[end] if end < len(q) else ''
                    if isinstance(value, str) and not (before == "'" and after == "'"):
                        return f"'{value}'"
                    return str(value)
                return pattern.sub(replacer, q)
            parts = [p.strip() for p in query.split(';') if p.strip()]
            for part in parts:
                resolved_part = resolve_query_vars(part)
                internal_logger.debug(f"[READ_DATA] Resolved query part: {resolved_part}")
                if resolved_part.startswith('select='):
                    select_cols = [c.strip() for c in resolved_part[7:].split(',') if c.strip()]
                    internal_logger.debug(f"[READ_DATA] Selected columns: {select_cols}")
                else:
                    filter_expr = resolved_part if filter_expr is None else f"{filter_expr} and {resolved_part}"
                    internal_logger.debug(f"[READ_DATA] Filter expression: {filter_expr}")
        # Apply filter
        if filter_expr:
            try:
                df = df.query(filter_expr)
                internal_logger.debug(f"[READ_DATA] Applied filter expression: {filter_expr}")
            except Exception as e:
                internal_logger.error(f"[READ_DATA] Invalid query expression: {filter_expr}. Error: {e}")
                raise ValueError(f"Invalid query expression: {filter_expr}. Error: {e}")
        # Select columns
        if select_cols:
            missing = [c for c in select_cols if c not in df.columns]
            if missing:
                internal_logger.error(f"[READ_DATA] Columns not found in data: {missing}")
                raise ValueError(f"Columns not found in data: {missing}")
            df = df.loc[:, select_cols]
            internal_logger.debug(f"[READ_DATA] Selected columns from DataFrame: {select_cols}")
        # Convert result to list of lists
        result = df.values.tolist()
        internal_logger.debug(f"[READ_DATA] Resulting data: {result}")
        # Fail if no data found after query/filter
        if df is not None and df.empty:
            internal_logger.error(f"[READ_DATA] No data found matching the query/filter: '{query}'")
            raise ValueError(f"No data found matching the query/filter: '{query}'")
        if len(result) == 1:
            data = result[0]
        else:
            data = result
        # Ensure all values are string (for both single and list cases)
        def to_str(val):
            if isinstance(val, list):
                return [str(v) for v in val]
            return str(val)
        data_str = to_str(data)
        internal_logger.debug(f"[READ_DATA] Data to store: {data_str}")
        runner_elements = self.session.elements
        if isinstance(runner_elements, ElementData):
            # If data_str is a list, join as comma-separated string for storage
            if isinstance(data_str, list):
                store_value = ','.join(data_str)
            else:
                store_value = data_str
            internal_logger.debug(f"[READ_DATA] Storing value under element '{elem_name}': {store_value}")
            runner_elements.add_element(elem_name, store_value)
        else:
            internal_logger.warning("[READ_DATA] Cannot store value: session.elements is not an ElementData instance.")
            # Ensure store_value is assigned even if runner_elements is not ElementData
            if isinstance(data_str, list):
                store_value = ','.join(data_str)
            else:
                store_value = data_str
        return [store_value] if not isinstance(data_str, list) else data_str

    def _load_data_with_query(self, file_path: Union[str, List[Any]], query: str) -> List[Any]:
        # Load as 2D list
        if isinstance(file_path, list):
            data = file_path
        else:
            data = self._load_csv_as_list(file_path)
        if not data or not isinstance(data, list) or not data[0]:
            return []
        headers = data[0]
        rows = data[1:]
        filters, select_cols = self._parse_query(query)
        # Apply filters
        filtered = []
        for row in rows:
            row_dict = {h: row[i] if i < len(row) else "" for i, h in enumerate(headers)}
            if all(str(row_dict.get(k, "")) == v for k, v in filters.items()):
                filtered.append(row_dict)
        # If no filters, use all rows
        if not filters:
            filtered = [{h: row[i] if i < len(row) else "" for i, h in enumerate(headers)} for row in rows]
        # Select columns
        if select_cols:
            result = [[row[c] for c in select_cols if c in row] for row in filtered]
        else:
            result = [list(row.values()) for row in filtered]
        return result

    def _parse_query(self, query: str) -> tuple[dict, list]:
        filters = {}
        select_cols = []
        if not query:
            return filters, select_cols
        parts = [p.strip() for p in query.split(';') if p.strip()]
        for part in parts:
            if part.startswith('select='):
                select_cols = [c.strip() for c in part[7:].split(',') if c.strip()]
            elif '=' in part:
                k, v = part.split('=', 1)
                filters[k.strip()] = v.strip()
        return filters, select_cols

    def _load_csv_as_list(self, file_path: str) -> list:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")
        if os.path.splitext(file_path)[-1].lower() != ".csv":
            raise ValueError("Unsupported file format. Use CSV or provide a list.")
        with open(file_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
        return data

    def _extract_element_name(self, input_element: str) -> str:
        """Extracts and cleans the element name from input."""
        elem_name = input_element.strip()
        if elem_name.startswith("${") and elem_name.endswith("}"):
            return elem_name[2:-1].strip()
        internal_logger.warning(
            f"[READ DATA] Expected element in format '${{name}}', got '{input_element}'. Using as is."
        )
        return elem_name

    def _load_data(
        self, file_path: Union[str, List[Any]], query: str
    ) -> List[Any]:
        """Loads data from a list or CSV file. 'query' is a column name or index for CSV."""
        if isinstance(file_path, list):
            return file_path
        return FlowControl._load_from_csv(file_path, query)


    @staticmethod
    def _load_from_csv(file_path: str, query: str) -> List[Any]:
        """Loads and extracts data from a CSV file using a column name or index as query."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")
        if os.path.splitext(file_path)[-1].lower() != ".csv":
            raise ValueError("Unsupported file format. Use CSV or provide a list.")

        with open(file_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
            if not data:
                raise ValueError(f"CSV file '{file_path}' is empty.")
            return FlowControl._extract_csv_data(data, query)

    @staticmethod
    def _extract_csv_data(data: List[List[str]], query: str) -> List[Any]:
        """Extracts data from CSV based on query (column name or index as string)."""
        headers = data[0]
        rows = data[1:]
        # Try to use as column name first
        if query in headers:
            col_idx = headers.index(query)
            return [row[col_idx] for row in rows if len(row) > col_idx and row[col_idx]]
        # Try to use as integer index
        try:
            idx = int(query)
            if idx >= len(headers):
                raise IndexError("Index out of range.")
            return [row[idx] for row in rows if len(row) > idx and row[idx]]
        except ValueError:
            pass
        raise ValueError(f"Query '{query}' must be a column name or integer index present in the CSV.")

    @raw_params(0)
    def evaluate(self, param1: str, param2: str) -> Any:
        """Evaluates an expression and stores the result in session.elements."""
        self._ensure_session()
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        var_name = self._extract_variable_name(param1)
        result = self._compute_expression(param2)
        runner_elements = getattr(self.session, "elements", None)
        if not isinstance(runner_elements, ElementData):
            runner_elements = ElementData()
            setattr(self.session, "elements", runner_elements)
        runner_elements.add_element(var_name, str(result))
        return result

    def _extract_variable_name(self, param1: str) -> str:
        """Extracts and cleans the variable name from param1."""
        var_name = param1.strip()
        if var_name.startswith("${") and var_name.endswith("}"):
            return var_name[2:-1].strip()
        internal_logger.warning(
            f"[EVALUATE] Expected param1 in format '${{name}}', got '{param1}'. Using as is."
        )
        return var_name

    def _compute_expression(self, param2: str) -> Any:
        """Computes an expression by resolving variables and evaluating it."""
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        runner_elements = getattr(self.session, "elements", None)
        if not isinstance(runner_elements, ElementData):
            raise ValueError("Session elements is not an ElementData instance or is None.")

        def replace_var(match):
            var_name = match.group(1)
            value = runner_elements.get_element(var_name)
            if value is None:
                raise ValueError(f"Variable '{var_name}' not found in elements.")
            return str(value)

        param2_resolved = re.sub(r"\$\{([^}]+)\}", replace_var, param2)
        return self._safe_eval(param2_resolved)

    def _safe_eval(self, expression: str) -> Any:
        """Safely evaluates an expression with restricted operations."""
        try:
            node = ast.parse(expression, mode="eval")
            allowed_nodes = (
                ast.Expression,
                ast.BinOp,
                ast.UnaryOp,
                ast.BoolOp,
                ast.Compare,
                ast.IfExp,
                ast.Constant,
                ast.Name,
                ast.Load,
                ast.List,
                ast.Tuple,
            )
            allowed_operators = (
                ast.Add,
                ast.Sub,
                ast.Mult,
                ast.Div,
                ast.Mod,
                ast.Pow,
                ast.Lt,
                ast.Gt,
                ast.Eq,
                ast.NotEq,
                ast.LtE,
                ast.GtE,
                ast.And,
                ast.Or,
                ast.Not,
            )
            for n in ast.walk(node):
                if not isinstance(n, allowed_nodes) and not isinstance(n, allowed_operators):
                    internal_logger.warning(f"[EVALUATE] Unsafe expression detected: {expression}")
                    raise ValueError(f"Unsafe expression detected: {expression}")
            if self.session is None:
                raise ValueError(NO_SESSION_PRESENT)
            runner_elements = self.session.elements.elements
            return eval(
                expression,
                {"__builtins__": None},
                {k: str(v) for k, v in runner_elements.items()},
            )  # nosec B307 # pylint: disable=eval-used
            # Note: eval() is used here for simplicity, i know it should be should be avoided in production code.
            # In some time, i will replace it with a safer alternative.
            # For now, we are using it with a restricted environment.
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{expression}': {e}")

    def _detect_date_format(self, date_str: str) -> str:
        """Detect the format of the input date string."""
        common_formats = [
            "%m/%d/%Y",  # 04/25/2025
            "%d/%m/%Y",  # 25/04/2025
            "%Y-%m-%d",  # 2025-04-25
            "%d-%m-%Y",  # 25-04-2025
            "%Y/%m/%d",  # 2025/04/25
        ]
        for fmt in common_formats:
            try:
                datetime.strptime(date_str, fmt)
                return fmt
            except ValueError:
                continue
        raise ValueError(f"Unable to detect date format for input: {date_str}")

    @raw_params(0)
    def date_evaluate(
        self, param1: str, param2: str, param3: str, param4: Optional[str] = "%d %B"
    ) -> str:
        """
        Evaluates a date expression based on an input date and stores the result in session.elements.

        Args:
            param1 (str): The variable name (placeholder) where the evaluated date result will be stored.
            param2 (str): The input date string (e.g., "04/25/2025" or "2025-04-25"). Format is auto-detected.
            param3 (str): The date expression to evaluate, such as "+1 day", "-2 days", or "today".
            param4 (Optional[str]): The output format for the evaluated date (default is "%d %B", e.g., "26 April").

        Returns:
            str: The resulting evaluated and formatted date string.

        Raises:
            ValueError: If the session is not present, the input date format cannot be detected,
                        or the expression format is invalid.

        Example:
            date_evaluate("tomorrow", "04/25/2025", "+1 day")
            ➔ Stores "26 April" in session.elements["tomorrow"]
        """
        self._ensure_session()
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)

        var_name = self._extract_variable_name(param1)
        input_date = param2.strip()
        expression = param3.strip()
        output_format = param4 or "%d %B"

        # Detect input format
        input_format = self._detect_date_format(input_date)

        # Parse current date
        base_date = datetime.strptime(input_date, input_format)

        # Parse and apply expression
        expr = expression.lower()
        if expr.startswith("+"):
            number, unit = expr[1:].split()
            number = int(number)
            if unit.startswith("day"):
                base_date += timedelta(days=number)
            else:
                raise ValueError(f"Unsupported unit in expression: {unit}")
        elif expr.startswith("-"):
            number, unit = expr[1:].split()
            number = int(number)
            if unit.startswith("day"):
                base_date -= timedelta(days=number)
            else:
                raise ValueError(f"Unsupported unit in expression: {unit}")
        elif expr in ("today", "now"):
            pass  # No change
        else:
            raise ValueError(f"Unsupported expression format: {expression}")

        # Format result
        result = base_date.strftime(output_format)

        # Store in session.elements
        runner_elements = getattr(self.session, "elements", None)
        if not isinstance(runner_elements, ElementData):
            runner_elements = ElementData()
            setattr(self.session, "elements", runner_elements)
        runner_elements.add_element(var_name, result)
        return result

    def invoke_api(self, api_identifier: str) -> None:
        """Invokes an API call based on a definition from the session's API data."""
        internal_logger.debug(f"[INVOKE_API] Called with api_identifier={api_identifier}")
        self._ensure_session()
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        collection_name, api_name = self._parse_api_identifier(api_identifier)
        internal_logger.debug(f"[INVOKE_API] Parsed collection_name={collection_name}, api_name={api_name}")
        collection = self._get_api_collection(collection_name)
        internal_logger.debug(f"[INVOKE_API] Retrieved API collection: {collection_name}")
        api_def = self._get_api_definition(collection, api_name)
        internal_logger.debug(f"[INVOKE_API] Retrieved API definition: {api_name}")

        url, headers, body = self._prepare_request_details(collection, api_def)
        internal_logger.debug(f"[INVOKE_API] Prepared request details: url={url}, headers={headers}, body={body}, method={api_def.request.method}")
        response = self._execute_request(url, headers, body, api_def.request.method)
        internal_logger.debug(f"[INVOKE_API] Received response: status_code={response.status_code}")
        self._process_response(response, api_def)
        internal_logger.debug(f"[INVOKE_API] Finished processing response for API: {api_name}")

    def _parse_api_identifier(self, identifier: str) -> Tuple[str, str]:
        """Parses 'collection.api' into a tuple."""
        parts = identifier.split(".", 1)
        if len(parts) != 2:
            raise ValueError(
                f"Invalid API identifier format: '{identifier}'. Expected 'collection.api_name'."
            )
        return parts[0], parts[1]

    def _get_api_collection(self, name: str):
        """Retrieves an API collection from the session."""
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)
        if not isinstance(self.session.apis, ApiData):
            raise ValueError("session instance does not have a valid 'apis' attribute.")
        collection = self.session.apis.collections.get(name)
        if not collection:
            raise ValueError(f"API collection '{name}' not found.")
        return collection

    def _get_api_definition(self, collection, name: str):
        """Retrieves a specific API definition from a collection."""
        api_def = collection.apis.get(name)
        if not api_def:
            raise ValueError(
                f"API '{name}' not found in collection '{collection.name}'."
            )
        return api_def

    def _prepare_request_details(
        self, collection, api_def
    ) -> Tuple[str, dict[str, str], Optional[Any]]:
        """Constructs the full request URL, headers, and body."""
        base_url = collection.base_url
        endpoint = self._resolve_placeholders(api_def.endpoint)
        if endpoint.startswith(("http://", "https://")):
            full_url = endpoint
        else:
            full_url = f"{base_url}{endpoint}"

        headers = {**collection.global_headers, **api_def.request.headers}
        resolved_headers = self._resolve_placeholders(headers)

        body = self._resolve_placeholders(api_def.request.body)
        return full_url, resolved_headers, body

    def _resolve_placeholders(self, data: Any) -> Any:
        """Recursively resolves ${...} placeholders in strings, dicts, or lists."""
        if isinstance(data, str):
            return re.sub(
                r"\$\{([^}]+)\}", lambda m: self._resolve_param(m.group(0)), data
            )
        if isinstance(data, dict):
            return {k: self._resolve_placeholders(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._resolve_placeholders(i) for i in data]
        return data

    def _execute_request(
    self, url: str, headers: dict, body: Optional[Any], method: str
    ) -> requests.Response:
        """Executes the HTTP request and returns the response."""
        try:
            config_handler = ConfigHandler.get_instance()
            execution_output_path = config_handler.get_execution_output_path()
            api_log_dir = execution_output_path

            api_log_file_path = None
            api_har_file_path = None
            if api_log_dir:
                os.makedirs(api_log_dir, exist_ok=True)
                api_log_file_path = os.path.join(api_log_dir, "api_details.log")
                api_har_file_path = os.path.join(api_log_dir, "api_details.har")

            start_time = datetime.now(timezone.utc)
            response = requests.request(
                method, url, headers=headers, json=body, timeout=30
            )
            time_taken = response.elapsed.total_seconds() * 1000

            if api_log_dir and api_log_file_path is not None:
                self._write_api_log(
                    api_log_file_path, method, url, headers, body, response
                )
                self._write_api_har(
                    api_har_file_path,
                    start_time,
                    time_taken,
                    method,
                    url,
                    headers,
                    body,
                    response,
                )

            return response
        except requests.RequestException as e:
            raise RuntimeError(f"API request to {url} failed: {e}") from e

    def _write_api_log(self, log_file_path, method, url, headers, body, response):
        """Writes API request/response details to a log file."""
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Method: {method}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Headers: {json.dumps(headers, indent=2)}\n")
            f.write(f"Body: {json.dumps(body, indent=2) if body else 'None'}\n")
            f.write(f"Response Status Code: {response.status_code}\n")
            try:
                f.write(f"Response Body: {json.dumps(response.json(), indent=2)}\n")
            except json.JSONDecodeError:
                f.write(f"Response Body: {response.text}\n")
            f.write("-" * 50 + "\n")

    def _write_api_har(
        self,
        har_file_path,
        start_time,
        time_taken,
        method,
        url,
        headers,
        body,
        response,
    ):
        """Writes API request/response details to a HAR file."""
        parsed_url = urlparse(url)
        query_string = [{"name": k, "value": v} for k, v in parse_qsl(parsed_url.query)]

        post_data = None
        request_body_size = 0
        if body:
            request_body_text = json.dumps(body)
            request_body_size = len(request_body_text.encode("utf-8"))
            post_data = {"mimeType": "application/json", "text": request_body_text}

        har_entry = {
            "startedDateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "time": time_taken,
            "request": {
                "method": method,
                "url": url,
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": [{"name": k, "value": v} for k, v in headers.items()],
                "queryString": query_string,
                "postData": post_data,
                "headersSize": -1,
                "bodySize": request_body_size,
            },
            "response": {
                "status": response.status_code,
                "statusText": response.reason,
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": [
                    {"name": k, "value": v} for k, v in response.headers.items()
                ],
                "content": {
                    "size": len(response.content),
                    "mimeType": response.headers.get("Content-Type", ""),
                    "text": response.text,
                },
                "redirectURL": response.headers.get("Location", ""),
                "headersSize": -1,
                "bodySize": len(response.content),
            },
            "cache": {},
            "timings": {
                "wait": response.elapsed.total_seconds() * 1000,
                "send": -1,
                "receive": -1,
            },
        }

        if har_file_path is not None and os.path.exists(har_file_path):
            with open(har_file_path, "r", encoding="utf-8") as f:
                try:
                    har_data = json.load(f)
                    if "log" not in har_data or "entries" not in har_data["log"]:
                        har_data = self._create_har_structure()
                except json.JSONDecodeError:
                    har_data = self._create_har_structure()
        else:
            har_data = self._create_har_structure()

        har_data["log"]["entries"].append(har_entry)

        if har_file_path is not None:
            with open(har_file_path, "w", encoding="utf-8") as f:
                json.dump(har_data, f, indent=2)

    def _create_har_structure(self) -> dict:
        """Creates a basic HAR file structure."""
        return {
            "log": {
                "version": "1.2",
                "creator": {"name": "Optics Framework", "version": "1.0"},
                "entries": [],
            }
        }

    def _process_response(self, response: requests.Response, api_def) -> None:
        """Extracts data from the response and saves it to session elements."""
        if not api_def.expected_result:
            internal_logger.debug("No expected_result defined in API definition.")
            return

        if not api_def.expected_result.extract:
            internal_logger.debug("No extraction paths defined in API definition.")
        else:
            internal_logger.debug(
                f"Attempting to extract values using paths: {api_def.expected_result.extract}"
            )
        if self.session is None:
            raise ValueError(NO_SESSION_PRESENT)

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            internal_logger.warning(
                "API response is not valid JSON; cannot extract values."
            )
            return

        if api_def.expected_result.extract:
            for element_name, path in api_def.expected_result.extract.items():
                value = self._extract_from_json(response_data, path)
                if value is not None:
                    self.session.elements.add_element(element_name, value)
                    internal_logger.debug(
                        f"Extracted '{element_name}' = '{value}' from response."
                    )
                else:
                    internal_logger.warning(
                        f"Could not extract '{element_name}' using path '{path}'."
                    )
            internal_logger.debug(
                f"Current session elements after extraction: {self.session.elements}"
            )

        if api_def.expected_result.jsonpath_assertions:
            self._evaluate_jsonpath_assertions(
                response_data, api_def.expected_result.jsonpath_assertions
            )

    def _evaluate_jsonpath_assertions(
    self, data: Any, assertions: list[dict[str, Any]]
    ) -> None:
        """Evaluates JSONPath assertions against the response data."""
        for assertion in assertions:
            path = assertion.get("path")
            condition = assertion.get("condition")
            if not path or not condition:
                internal_logger.warning(
                    f"Skipping malformed JSONPath assertion: {assertion}"
                )
                continue

            try:
                jsonpath_expr = jsonpath_parse(path)
                match = jsonpath_expr.find(data)

                if not match:
                    internal_logger.warning(f"[JSONPATH] JSONPath '{path}' found no match.")
                    raise AssertionError(f"JSONPath '{path}' found no match.")

                matched_value = match[0].value
                eval_condition = condition.replace("$", repr(matched_value))

                if not eval(eval_condition):  # nosec B307 # pylint: disable=eval-used
                    internal_logger.warning(f"[JSONPATH] JSONPath assertion failed: Path '{path}', Condition '{condition}', Matched value '{matched_value}'.")
                    raise AssertionError(
                        f"JSONPath assertion failed: Path '{path}', Condition '{condition}', Matched value '{matched_value}'."
                    )
                internal_logger.debug(
                    f"JSONPath assertion passed: Path '{path}', Condition '{condition}'."
                )
            except Exception as e:
                raise AssertionError(
                    f"Error evaluating JSONPath assertion {assertion}: {e}"
                ) from e

    def _extract_from_json(self, data: Any, path: str) -> Optional[Any]:
        """Extracts a value from a nested dictionary using a dot-separated path."""
        current_data = data
        for key in path.split("."):
            internal_logger.debug(
                f"_extract_from_json: Current data type: {type(current_data)}, Key: {key}"
            )
            if isinstance(current_data, dict):
                current_data = current_data.get(key)
                internal_logger.debug(
                    f"_extract_from_json: Value after get('{key}'): {current_data}"
                )
            else:
                internal_logger.warning(
                    f"_extract_from_json: Data is not a dictionary at key '{key}'. Current data: {current_data}"
                )
                return None
        return current_data
