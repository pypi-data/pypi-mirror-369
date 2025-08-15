# pandas-timeinterval

A package to trim datetime-indexed DataFrames and Series in pandas. This package is useful for analyzing sparse DataFrames. It provides functionalities to generate Intervals objects using boolean Series, modify these Intervals using various methods (such as expand, contract), and combine them via set operations. The resulting Intervals can be used to trim any DataFrame using the `.trim` method.

## Features

- **Union and Intersection**: Perform union and intersection operations on interval objects.
- **Trim**: Trim DataFrame/Series to only include data within specified intervals.
- **Adjust**: Adjust intervals by a specified timedelta.
- **Normalize**: Merge overlapping intervals into a single interval.
- **Flexible Interval Creation**: Create intervals from boolean Series.

## Installation

```bash
pip install pandas-timeinterval
```

## Usage

## Union and Intersection Example
```python
import pandas as pd
from pandas_timeinterval import Intervals

# Create two Intervals objects with datetime ranges
intervals1 = Intervals([(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"))])
intervals2 = Intervals([(pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-04"))])

# Perform union operation
union_intervals = intervals1.union(intervals2)
print(union_intervals)

# Perform intersection operation
intersection_intervals = intervals1.intersection(intervals2)
print(intersection_intervals)
```

### Trim Example

```python
import pandas as pd
from pandas_timeinterval import Intervals, Interval

# Create a sample DataFrame
sample_data = pd.Series(
    [1, 2, 3, 4, 5], index=pd.date_range(start="2021-01-01", periods=5, freq="D")
)

# Create an Intervals object
intervals = Intervals([(pd.Timestamp("2021-01-02"), pd.Timestamp("2021-01-03"))])

# Trim the data
trimmed_data = intervals.trim(sample_data)

print(trimmed_data)
```

### Adjust Example

```python
import pandas as pd
from pandas_timeinterval import Intervals, Interval

# Create Intervals object
intervals = Intervals(
    [Interval(pd.Timestamp("2021-01-01"), pd.Timestamp("2021-01-03")),
     Interval(pd.Timestamp("2021-01-02"), pd.Timestamp("2021-01-04"))]
)

# Adjust intervals by adding one day
adjusted_intervals = intervals.adjust(pd.Timedelta(days=1))
print(adjusted_intervals)

# Normalize intervals to merge overlapping intervals
normalized_intervals = intervals.normalize()
print(normalized_intervals)
```
