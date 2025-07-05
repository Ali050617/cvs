import pytest
import csv
import os
from csv_processor import (
    read_csv,
    apply_filter,
    apply_aggregation,
    parse_condition
)


@pytest.fixture
def sample_csv(tmp_path):
    data = [
        {"name": "Product1", "price": "100", "rating": "4.5"},
        {"name": "Product2", "price": "200", "rating": "4.8"},
        {"name": "Product3", "price": "300", "rating": "4.2"}
    ]
    file_path = tmp_path / "test.csv"
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "rating"])
        writer.writeheader()
        writer.writerows(data)
    return str(file_path)


def test_read_csv(sample_csv):
    data = read_csv(sample_csv)
    assert len(data) == 3
    assert data[0]["name"] == "Product1"
    assert data[1]["price"] == "200"


def test_apply_filter_equal(sample_csv):
    data = read_csv(sample_csv)
    filtered = apply_filter(data, "name", "=", "Product2")
    assert len(filtered) == 1
    assert filtered[0]["price"] == "200"


def test_apply_aggregation_avg(sample_csv):
    data = read_csv(sample_csv)
    result = apply_aggregation(data, "rating", "avg")
    assert result["value"] == pytest.approx(4.5, 0.1)


def test_parse_condition():
    col, op, val = parse_condition("price>300")
    assert col == "price"
    assert op == ">"
    assert val == "300"


def test_invalid_condition():
    with pytest.raises(ValueError):
        parse_condition("invalid_condition")


def test_non_numeric_aggregation(sample_csv):
    data = read_csv(sample_csv)
    with pytest.raises(ValueError):
        apply_aggregation(data, "name", "avg")
