import pandas as pd
from pandas_timeinterval import Intervals, Interval


def test_union_no_overlap():
    dt_pairs1 = Intervals([(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"))])
    dt_pairs2 = Intervals([(pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-04"))])
    union_pairs = dt_pairs1.union(dt_pairs2)
    assert union_pairs == Intervals(
        [
            (pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")),
            (pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-04")),
        ]
    )


def test_union_with_overlap():
    dt_pairs1 = Intervals([(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))])
    dt_pairs2 = Intervals([(pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-04"))])
    union_pairs = dt_pairs1.union(dt_pairs2)
    assert union_pairs == Intervals(
        [(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-04"))]
    )


def test_union_star_args():
    # Example usage:
    dt_pairs1 = Intervals([(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"))])
    dt_pairs2 = Intervals([(pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-06"))])
    dt_pairs3 = Intervals([(pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-07"))])

    # Union of multiple DateTimePairs instances
    union_pairs = dt_pairs1.union(dt_pairs2, dt_pairs3)
    assert union_pairs == Intervals(
        [
            (pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")),
            (pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-07")),
        ]
    )


def test_intersection():
    dt_pairs1 = Intervals([(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))])
    dt_pairs2 = Intervals([(pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-04"))])
    intersection_pairs = dt_pairs1.intersection(dt_pairs2)
    assert intersection_pairs == Intervals(
        [(pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03"))]
    )


def test_intersection_star_args_overlap():
    dt_pairs1 = Intervals([(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-05"))])
    dt_pairs2 = Intervals([(pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-04"))])
    dt_pairs3 = Intervals([(pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-05"))])

    # Intersection of multiple DateTimePairs instances
    intersection_pairs = dt_pairs1.intersection(dt_pairs2, dt_pairs3)
    assert intersection_pairs == Intervals(
        [(pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-04"))]
    )


def test_intersection_star_args_no_overlap():
    dt_pairs1 = Intervals([(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-03"))])
    dt_pairs2 = Intervals([(pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-04"))])
    dt_pairs3 = Intervals([(pd.Timestamp("2024-01-04"), pd.Timestamp("2024-01-05"))])

    # Intersection of multiple DateTimePairs instances
    intersection_pairs = dt_pairs1.intersection(dt_pairs2, dt_pairs3)
    assert intersection_pairs == Intervals()


# Test for trim method
def test_trim_method():
    # Create a sample DataFrame/Series
    sample_data = pd.Series(
        [1, 2, 3, 4, 5], index=pd.date_range(start="2021-01-01", periods=5, freq="D")
    )

    # Create a DateTimePairs instance with specific intervals
    dt_pairs = Intervals(
        [Interval(pd.Timestamp("2021-01-02"), pd.Timestamp("2021-01-03"))]
    )

    # Trim the data
    trimmed_data = dt_pairs.trim(sample_data)

    # Check if the trimmed data is as expected
    assert trimmed_data.equals(sample_data["2021-01-02":"2021-01-03"])


# Test for adjust method
def test_adjust_method():
    # Create a DateTimePairs instance
    dt_pairs = Intervals(
        [Interval(pd.Timestamp("2021-01-01"), pd.Timestamp("2021-01-02"))]
    )

    # Adjust the intervals
    adjusted_dt_pairs = dt_pairs.adjust(pd.Timedelta(days=1))

    # Expected result
    expected = Intervals(
        [Interval(pd.Timestamp("2020-12-31"), pd.Timestamp("2021-01-03"))]
    )

    # Check if the adjusted intervals are as expected
    assert adjusted_dt_pairs.intervals == expected.intervals


# Test for normalize method
def test_normalize_method():
    # Create a DateTimePairs instance with overlapping intervals
    dt_pairs = Intervals(
        [
            Interval(pd.Timestamp("2021-01-01"), pd.Timestamp("2021-01-03")),
            Interval(pd.Timestamp("2021-01-02"), pd.Timestamp("2021-01-04")),
        ]
    )

    # Normalize the intervals
    normalized_dt_pairs = dt_pairs.normalize()

    # Expected result
    expected = Intervals(
        [Interval(pd.Timestamp("2021-01-01"), pd.Timestamp("2021-01-04"))]
    )

    # Check if the normalized intervals are as expected
    assert normalized_dt_pairs.intervals == expected.intervals


if __name__ == "__main__":
    test_intersection_star_args_no_overlap()
