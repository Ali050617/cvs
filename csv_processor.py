import argparse
import csv
from typing import List, Dict, Union, Callable
from tabulate import tabulate


def read_csv(file_path: str) -> List[Dict[str, str]]:
    """Read CSV file and return list of dictionaries."""
    with open(file_path, mode='r') as file:
        return list(csv.DictReader(file))


def apply_filter(
        rows: List[Dict[str, str]],
        column: str,
        operator: str,
        value: str
) -> List[Dict[str, str]]:
    """Filter rows based on column, operator and value."""

    def try_convert(val: str) -> Union[float, str]:
        """Try to convert string to float if possible."""
        try:
            return float(val)
        except ValueError:
            return val

    operators: Dict[str, Callable[[Union[float, str], Union[float, str]], bool]] = {
        '=': lambda x, y: x == y,
        '>': lambda x, y: x > y,
        '<': lambda x, y: x < y,
    }

    if operator not in operators:
        raise ValueError(f"Unsupported operator: {operator}")

    op_func = operators[operator]
    filtered_rows = []

    for row in rows:
        row_val = try_convert(row[column])
        cmp_val = try_convert(value)

        if op_func(row_val, cmp_val):
            filtered_rows.append(row)

    return filtered_rows


def apply_aggregation(
        rows: List[Dict[str, str]],
        column: str,
        operation: str
) -> Dict[str, Union[str, float]]:
    """Apply aggregation to column and return result."""
    operations: Dict[str, Callable[[List[float]], float]] = {
        'avg': lambda x: sum(x) / len(x),
        'min': min,
        'max': max,
    }

    if operation not in operations:
        raise ValueError(f"Unsupported operation: {operation}")

    try:
        values = [float(row[column]) for row in rows]
    except ValueError:
        raise ValueError(f"Cannot aggregate non-numeric column: {column}")

    result = operations[operation](values)

    return {
        'operation': operation,
        'column': column,
        'value': round(result, 2)
    }


def parse_condition(condition: str) -> tuple[str, str, str]:
    """Parse condition string into column, operator and value."""
    operators = ['>=', '<=', '!=', '=', '>', '<']
    for op in operators:
        if op in condition:
            parts = condition.split(op, 1)
            if len(parts) == 2:
                return parts[0], op, parts[1]
    raise ValueError(f"Invalid condition format: {condition}")


def main():
    parser = argparse.ArgumentParser(
        description='Process CSV files with filtering and aggregation.'
    )
    parser.add_argument('file', help='Path to CSV file')
    parser.add_argument(
        '--where',
        help='Filter condition (e.g., "price>300")',
        required=False
    )
    parser.add_argument(
        '--aggregate',
        help='Aggregation operation (e.g., "rating=avg")',
        required=False
    )

    args = parser.parse_args()

    try:
        rows = read_csv(args.file)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        return

    if args.where:
        try:
            column, operator, value = parse_condition(args.where)
            rows = apply_filter(rows, column, operator, value)
        except ValueError as e:
            print(f"Filter error: {e}")
            return

    if args.aggregate:
        try:
            column, operation = args.aggregate.split('=', 1)
            result = apply_aggregation(rows, column, operation)
            print(tabulate([result.values()], headers=result.keys(), tablefmt='grid'))
        except ValueError as e:
            print(f"Aggregation error: {e}")
    else:
        if rows:
            print(tabulate(rows, headers='keys', tablefmt='grid'))
        else:
            print("No data to display")


if __name__ == '__main__':
    main()