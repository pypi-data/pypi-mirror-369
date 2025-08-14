import copy
import logging
from typing import Any, Dict, Optional
import json

from fastpluggy.core.widgets import AbstractWidget
from fastpluggy.core.database import session_scope
from ..models import ScheduledQuery, ScheduledQueryResultHistory


class ScheduledQueryResultWidget(AbstractWidget):
    """
    A widget to display scheduled query results with rich formatting.
    Supports various result formats including JSON, metrics, tables, and raw text.
    """

    widget_type = "scheduled_query_result"
    template_name = "scheduled_query/widgets/scheduled_query_result.html.j2"
    category = "scheduled_query"
    description = "Display scheduled query results with rich formatting"
    icon = "database"

    def __init__(
        self,
        id_scheduled_query: Optional[int] = None,
        scheduled_query: Optional[ScheduledQuery] = None,
        show_query_info: bool = True,
        show_execution_details: bool = True,
        max_table_rows: int = 10,
        **kwargs
    ):
        """
        Initialize the ScheduledQueryResultWidget.

        Args:
            id_scheduled_query: The ID of the ScheduledQuery to fetch from database
            scheduled_query: The ScheduledQuery model instance (if already available)
            show_query_info: Whether to show query information (name, schedule, etc.)
            show_execution_details: Whether to show execution details (time, duration, etc.)
            max_table_rows: Maximum number of rows to display in table format
            **kwargs: Additional widget parameters
        """
        super().__init__(**kwargs)

        # Get the ScheduledQuery object
        if scheduled_query is not None:
            self.scheduled_query = scheduled_query
        elif id_scheduled_query is not None:
            # Fetch ScheduledQuery from database using the ID
            with session_scope() as db:
                self.scheduled_query = db.query(ScheduledQuery).filter(
                    ScheduledQuery.id == id_scheduled_query
                ).first()
                if self.scheduled_query is None:
                    raise ValueError(f"ScheduledQuery with id {id_scheduled_query} not found")

                if  self.scheduled_query:
                    self.execution_result = self._get_latest_execution_result(db=db)
                    self.execution_result = copy.deepcopy( self.execution_result)
        else:
            raise ValueError("Either id_scheduled_query or scheduled_query must be provided")

        if self.scheduled_query is None:
            raise ValueError(f"ScheduledQuery with id {id_scheduled_query} not found")

        self.show_query_info = show_query_info
        self.show_execution_details = show_execution_details
        self.max_table_rows = max_table_rows

        # Get the latest execution result from the ScheduledQuery

        # Process the result data
        self.processed_result = None
        self.result_type = "unknown"
        self.error_message = None

    def _get_latest_execution_result(self, db) -> Optional[ScheduledQueryResultHistory]:
        """
        Get the latest execution result for the scheduled query.
        
        Returns:
            The latest ScheduledQueryResultHistory object, or None if no results exist
        """
        if not self.scheduled_query:
            return None
            
        # Try to get the latest result from execution_history
        latest_result = db.query(ScheduledQueryResultHistory).filter(
            ScheduledQueryResultHistory.scheduled_query_id == self.scheduled_query.id
        ).order_by(ScheduledQueryResultHistory.executed_at.desc()).first()

        if latest_result:
            return latest_result

        return None

    def process(self, **kwargs) -> None:
        """Process the widget data and prepare for rendering."""
        self._process_result()

    def _process_result(self) -> None:
        """Process the execution result and determine how to display it."""
        if not self.execution_result:
            self.result_type = "no_result"
            return

        # Handle different input types
        if hasattr(self.execution_result, 'result'):
            # ScheduledQueryResultHistory object
            result_data = self.execution_result.result
            status = getattr(self.execution_result, 'status', 'unknown')
            error_message = getattr(self.execution_result, 'error_message', None)
        else:
            # Direct result data
            result_data = self.execution_result
            status = "success"
            error_message = None

        # Handle failed executions
        if status != "success" or not result_data:
            if error_message:
                self.result_type = "error"
                self.error_message = error_message
            else:
                self.result_type = "no_result"
            return

        # Process the result data
        result_str = str(result_data).strip()

        # Check for status messages
        if self._is_status_message(result_str):
            self.result_type = "status_message"
            self.processed_result = result_str
            return

        # Try to parse as JSON
        try:
            parsed_json = json.loads(result_str)
            self._process_json_result(parsed_json)
            return
        except (json.JSONDecodeError, TypeError):
            pass

        # Try to parse as Python tuple/list representation
        if self._try_parse_python_tuple(result_str):
            return

        # Fallback to raw text
        self.result_type = "raw_text"
        self.processed_result = result_str

    def _is_status_message(self, result_str: str) -> bool:
        """Check if the result is a status message."""
        import re
        return bool(re.match(r'^(Rows affected|Query rejected|Error):', result_str, re.IGNORECASE))

    def _process_json_result(self, parsed_json: Any) -> None:
        """Process JSON result and determine display format."""
        if isinstance(parsed_json, list) and len(parsed_json) == 1:
            # Single result - check if it's a metric
            result = parsed_json[0]
            if isinstance(result, dict) and len(result) == 1:
                key, value = next(iter(result.items()))
                if isinstance(value, (int, float)):
                    self.result_type = "metric"
                    self.processed_result = {
                        "metric_name": key,
                        "metric_value": value
                    }
                    return

        if isinstance(parsed_json, list) and len(parsed_json) > 0:
            # Multiple results - display as table
            self.result_type = "table"
            self.processed_result = {
                "data": parsed_json[:self.max_table_rows],
                "total_rows": len(parsed_json),
                "columns": list(parsed_json[0].keys()) if parsed_json and isinstance(parsed_json[0], dict) else []
            }
            return

        # Other JSON formats
        self.result_type = "json"
        self.processed_result = parsed_json

    def _try_parse_python_tuple(self, result_str: str) -> bool:
        """Try to parse Python tuple/list string representation with improved handling."""
        if not (result_str.startswith('[') and result_str.endswith(']')):
            return False

        try:
            # Use ast.literal_eval for safer parsing of Python literals
            import ast
            try:
                # Try to evaluate the string as a Python literal
                parsed_data = ast.literal_eval(result_str)
                if isinstance(parsed_data, list) and all(isinstance(item, tuple) for item in parsed_data):
                    return self._process_parsed_tuples(parsed_data)
            except (ValueError, SyntaxError):
                # If ast.literal_eval fails, fall back to manual parsing
                logging.warning(f"Error on parsing : {result_str}")
                pass

            # Fallback to improved manual parsing for complex cases like datetime objects
            return self._manual_tuple_parsing(result_str)

        except Exception:
            pass

        return False

    def _process_parsed_tuples(self, parsed_data: list) -> bool:
        """Process successfully parsed tuple data."""
        if not parsed_data:
            return False

        processed_rows = []
        for tuple_item in parsed_data:
            row_values = []
            for value in tuple_item:
                formatted_value = self._format_tuple_value(value)
                row_values.append(formatted_value)
            processed_rows.append(row_values)

        if processed_rows:
            self.result_type = "tuple_table"
            self.processed_result = {
                "data": processed_rows[:self.max_table_rows],
                "total_rows": len(processed_rows),
                "columns": [f"Column {i+1}" for i in range(len(processed_rows[0]))] if processed_rows else []
            }
            return True

        return False

    def _manual_tuple_parsing(self, result_str: str) -> bool:
        """Manual parsing for complex tuple formats that ast.literal_eval can't handle."""
        # Remove outer brackets
        inner_content = result_str[1:-1].strip()

        if not inner_content:
            return False

        # Split tuples more carefully, considering nested parentheses
        tuple_strings = self._split_tuples_carefully(inner_content)

        parsed_rows = []
        processed_rows = []
        for tuple_str in tuple_strings:
            # Clean up the tuple string
            clean_tuple = tuple_str.strip()
            if clean_tuple.startswith('('):
                clean_tuple = clean_tuple[1:]
            if clean_tuple.endswith(')'):
                clean_tuple = clean_tuple[:-1]

            # Parse values within the tuple more carefully
            if clean_tuple.strip():
                row_values = self._parse_tuple_values(clean_tuple)
                if row_values:
                    processed_rows.append(row_values)

        if parsed_rows:
            self.result_type = "tuple_table"
            self.processed_result = {
                "data": processed_rows[:self.max_table_rows],
                "total_rows": len(parsed_rows),
                "columns": [f"Column {i+1}" for i in range(len(parsed_rows[0]))] if parsed_rows else []
            }
            return True

        return False

    def _split_tuples_carefully(self, content: str) -> list:
        """Split tuple strings while respecting nested parentheses."""
        tuples = []
        current_tuple = ""
        paren_depth = 0
        i = 0

        while i < len(content):
            char = content[i]

            if char == '(':
                paren_depth += 1
                current_tuple += char
            elif char == ')':
                paren_depth -= 1
                current_tuple += char

                # If we're back to depth 0 and this closes a tuple
                if paren_depth == 0:
                    # Look ahead to see if there's a comma and space indicating another tuple
                    if i + 2 < len(content) and content[i+1:i+3] == ', ':
                        tuples.append(current_tuple)
                        current_tuple = ""
                        i += 2  # Skip the ', ' separator
                    elif i == len(content) - 1:  # End of string
                        tuples.append(current_tuple)
                        current_tuple = ""
            else:
                current_tuple += char

            i += 1

        # Add any remaining content
        if current_tuple.strip():
            tuples.append(current_tuple)

        return tuples

    def _parse_tuple_values(self, tuple_content: str) -> list:
        """Parse individual values within a tuple, handling complex types."""
        values = []
        current_value = ""
        paren_depth = 0
        in_quotes = False
        quote_char = None
        i = 0

        while i < len(tuple_content):
            char = tuple_content[i]

            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current_value += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_value += char
            elif char == '(' and not in_quotes:
                paren_depth += 1
                current_value += char
            elif char == ')' and not in_quotes:
                paren_depth -= 1
                current_value += char
            elif char == ',' and paren_depth == 0 and not in_quotes:
                # This is a value separator
                if current_value.strip():
                    formatted_value = self._format_parsed_value(current_value.strip())
                    values.append(formatted_value)
                current_value = ""
            else:
                current_value += char

            i += 1

        # Add the last value
        if current_value.strip():
            # Handle trailing comma case
            clean_value = current_value.strip().rstrip(',')
            if clean_value:
                formatted_value = self._format_parsed_value(clean_value)
                values.append(formatted_value)

        return values

    def _format_tuple_value(self, value: Any) -> str:
        """Format a value from a successfully parsed tuple."""
        if value is None:
            return "None"
        elif isinstance(value, bool):
            return str(value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif hasattr(value, 'strftime'):  # datetime-like objects
            return value.strftime('%Y-%m-%d') if hasattr(value, 'date') else str(value)
        else:
            return str(value)

    def _format_parsed_value(self, value_str: str) -> str:
        """Format a manually parsed value string."""
        value_str = value_str.strip()

        # Handle None
        if value_str == 'None':
            return "None"

        # Handle booleans
        if value_str == 'True':
            return "True"
        elif value_str == 'False':
            return "False"

        # Handle quoted strings
        if ((value_str.startswith('"') and value_str.endswith('"')) or 
            (value_str.startswith("'") and value_str.endswith("'"))):
            return value_str[1:-1]  # Remove quotes

        # Handle datetime objects
        if value_str.startswith('datetime.date(') and value_str.endswith(')'):
            # Extract the date components
            import re
            match = re.match(r'datetime\.date\((\d+),\s*(\d+),\s*(\d+)\)', value_str)
            if match:
                year, month, day = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Handle other datetime-like objects
        if 'datetime.' in value_str and '(' in value_str:
            # For other datetime objects, try to extract a readable format
            return value_str.replace('datetime.', '').replace('(', ' (')

        # Return as-is for numbers and other simple types
        return value_str

    def get_context(self) -> Dict[str, Any]:
        """Get the template context."""
        context = super().get_context()

        # Add formatted execution time if available
        if hasattr(self.execution_result, 'executed_at') and self.execution_result.executed_at:
            context['formatted_execution_time'] = self.execution_result.executed_at.strftime('%Y-%m-%d %H:%M:%S')

        # Add formatted duration if available
        if hasattr(self.execution_result, 'duration_ms') and self.execution_result.duration_ms:
            duration_ms = self.execution_result.duration_ms
            if duration_ms < 1000:
                context['formatted_duration'] = f"{duration_ms}ms"
            else:
                context['formatted_duration'] = f"{duration_ms / 1000:.2f}s"

        return context

    def format_number(self, value: Any) -> str:
        """Format numbers for display."""
        if isinstance(value, (int, float)) and value > 1000:
            return f"{value:,}"
        return str(value)
