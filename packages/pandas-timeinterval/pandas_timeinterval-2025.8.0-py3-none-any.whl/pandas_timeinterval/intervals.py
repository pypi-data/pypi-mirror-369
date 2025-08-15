from __future__ import annotations

import typing
from collections import deque
from dataclasses import dataclass
from typing import (
    Iterable,
    NamedTuple,
    Optional,
    Tuple,
    List,
    Union,
    Sequence,
    overload,
)

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

dt = pd.Timedelta
Data = typing.TypeVar("Data", pd.DataFrame, pd.Series)
Time = Union[pd.Timestamp, pd._libs.tslibs.nattype.NaTType]


class Interval(NamedTuple):
    start: Time
    end: Time

    @overload
    def trim(self, data: pd.DataFrame) -> pd.DataFrame: ...
    @overload
    def trim(self, data: pd.Series) -> pd.Series: ...
    def trim(self, data: Data) -> Data:
        f"""
        Trim a DataFrame or Series to only include rows within the intervals specified in a {self.__class__.__name__} object.

        Parameters:
        data (pd.DataFrame or pd.Series): The DataFrame or Series to be trimmed.
        datetime_pairs ({self.__class__.__name__}): The {self.__class__.__name__} object specifying the intervals.

        Returns:
        pd.DataFrame or pd.Series: The trimmed DataFrame or Series.
        """
        start = None if pd.isnull(self.start) else self.start
        end = None if pd.isnull(self.end) else self.end
        data_truncated = data.truncate(before=start, after=end)
        return data_truncated

    def adjust_start(self, delta: dt) -> Interval:
        return Interval(start=self.start + delta, end=self.end)

    def adjust_end(self, delta: dt) -> Interval:
        return Interval(start=self.start, end=self.end + delta)

    def adjust_both(self, delta: dt, direction: str = "opposite") -> Interval:
        if direction not in ["same", "opposite"]:
            raise ValueError("direction must be either 'same' or 'opposite'")

        direction_int: int = 1 if direction == "same" else -1

        new_start = self.start + delta
        new_end = self.end + (direction_int * delta)

        return Interval(start=new_start, end=new_end)

    def contract(self, delta: dt) -> Interval:
        return self.adjust_both(delta, direction="opposite")

    def expand(self, delta: dt) -> Interval:
        return self.adjust_both(-delta, direction="opposite")

    def duration(self):
        return self.end - self.start

    def repr_start_duration(self):
        return """{}('{}', -> '{}')""".format(
            self.__class__.__name__, self.start, self.end - self.start
        )

    def to_intervals(self) -> Intervals:
        return Intervals(intervals=[self])

    @classmethod
    def from_bool_series(
        cls,
        bool_series: pd.Series,
        boundary_handling: str = "open",
    ) -> Interval:
        """
        Create an Interval object from a boolean series, where the first contiguous group of 'True' values
        is converted into a datetime pair.

        Parameters:
        - bool_series: A pandas Series containing boolean values.
        - boundary_handling: Specifies how to handle the boundaries. 'open' uses pd.NaT to represent open intervals,
          'closed' uses the actual time boundaries of the group.

        Returns:
        - An Interval object representing the first contiguous group of 'True' values.

        Raises:
        - ValueError: If no contiguous 'True' values are found.
        """
        cumsum = bool_series.ne(bool_series.shift()).cumsum()
        grouped = bool_series.groupby(cumsum)
        true_groups = grouped.filter(lambda x: x.any())

        if true_groups.empty:
            raise ValueError("No contiguous 'True' values found.")

        first_group = next(iter(true_groups.groupby(cumsum)))

        _, group = first_group
        start = group.index[0]
        end = group.index[-1]

        if boundary_handling == "open":
            if start == bool_series.index[0]:
                start = pd.NaT
            if end == bool_series.index[-1]:
                end = pd.NaT

        return cls(start, end)


@dataclass
class Intervals:
    intervals: Tuple[Interval]

    def __init__(self, intervals: Optional[Iterable[Sequence[Time]]] = None):
        """
        Initialize the Intervals object with a sequence of iterables, each containing two pandas Timestamps.
        Timestamps can be None or pandas NaT to represent open-ended intervals.

        Parameters:
        intervals (Sequence[Iterable[Timestamp]], optional):
            A sequence of iterables, each containing two pandas Timestamp objects.
            Default is an iterable with two NaT values, representing an open-ended interval.

        Raises:
        ValueError: If the input does not implement an iterable interface, if any interval
                    does not contain exactly 2 elements, or if the elements are not Timestamps.
        """

        intervals: Iterable[Sequence[Time]] = (
            intervals if intervals is not None else [(pd.NaT, pd.NaT)]
        )

        if not isinstance(intervals, Iterable):
            raise ValueError(
                "Intervals must be an iterable of pairs of timestamps. ({})".format(
                    "intervals={}".format(intervals)
                )
            )

        _intervals: List[Interval] = []
        for interval in intervals:
            if not isinstance(interval, Sequence) or len(interval) != 2:
                raise ValueError(
                    "Each interval must be an iterable containing exactly two elements. ({})".format(
                        "interval={}".format(interval)
                    )
                )

            start, end = interval
            if not (isinstance(start, pd.Timestamp) or isinstance(start, NaTType)):
                raise ValueError(
                    "Both elements of each interval must be pandas Timestamps or NaT. ({}, {})".format(
                        "start={}".format(start), "end={}".format(end)
                    )
                )

            if not (isinstance(end, pd.Timestamp) or isinstance(end, NaTType)):
                raise ValueError(
                    "Both elements of each interval must be pandas Timestamps or NaT. ({}, {})".format(
                        "start={}".format(start), "end={}".format(end)
                    )
                )

            _intervals.append(Interval(start, end))

        self.intervals = tuple(_intervals)

    def add_interval(self, start: Time, end: Time) -> Intervals:
        """
        Add a new datetime pair to the list.

        :param start: The start timestamp of the interval.
        :param end: The end timestamp of the interval.
        """
        new_pairs = list(self.intervals)
        new_pairs.append(Interval(start, end))
        return Intervals(new_pairs).normalize()

    def get_interval(self) -> Tuple[Interval]:
        """
        Get the tuple of datetime pairs.

        :return: tuple of datetime pairs.
        """
        return self.intervals

    @property
    def start(self):
        return self.intervals[0].start

    @property
    def end(self):
        return self.intervals[0].end

    @classmethod
    def from_bool_series(
        cls,
        bool_series: pd.Series,
        boundary_handling: str = "open",
    ) -> Intervals:
        """
        Create a {} object from a boolean series, where contiguous 'True' values
        are converted into datetime pairs.

        Parameters:
        - bool_series: A pandas Series containing boolean values.
        - boundary_handling: How to handle the boundary's ('open' or 'closed'). Open uses pd.NaT to represent open intervals. 'closed' uses the time boundary of the dataframe to close the interval.

        :param bool_series: A pandas Series containing boolean values.
        :param boundary_handling: How to handle the boundary's ('open' or 'closed').
        :return: {} object.
        """.format(cls.__name__, cls.__name__)
        cumsum = bool_series.ne(bool_series.shift()).cumsum()
        grouped = bool_series[bool_series].groupby(cumsum)

        pairs = []
        for _, group in grouped:
            start = group.index[0]
            end = group.index[-1]

            if boundary_handling == "open":
                if start == bool_series.index[0]:
                    start = pd.NaT
                if end == bool_series.index[-1]:
                    end = pd.NaT

            pairs.append(Interval(start, end))

        return cls(pairs)

    def union(self, *args: Intervals) -> Intervals:
        """
        Union the datetime pairs of this instance with one or more other {} instances.

        :param args: A variable number of {} instances.
        :return: A new {} instance representing the union of all sets of datetime pairs.
        """.format(
            self.__class__.__name__, self.__class__.__name__, self.__class__.__name__
        )
        all_pairs = list(self.intervals)

        for dt_pairs in args:
            all_pairs.extend(dt_pairs.intervals)

        return Intervals(all_pairs).normalize()

    def intersection(self, *args: Intervals) -> Intervals:
        """
        Find the intersection of datetime pairs among this and other {} instances.

        :param args: A variable number of {} instances.
        :return: A new {} instance representing the intersection of all sets of datetime pairs.
        """.format(
            self.__class__.__name__, self.__class__.__name__, self.__class__.__name__
        )
        # Start with the pairs from the current instance
        intersected_pairs = list(self.intervals)

        # Iterate over each additional DateTimePairs instance
        for dt_pairs in args:
            new_intersected_pairs = []
            for pair1 in intersected_pairs:
                for pair2 in dt_pairs.intervals:
                    start = max(pair1.start, pair2.start)
                    end = min(pair1.end, pair2.end)

                    if start <= end:
                        new_intersected_pairs.append(Interval(start, end))

            intersected_pairs = new_intersected_pairs
            if not intersected_pairs:
                break

        return Intervals(intersected_pairs).normalize()

    def difference(self, other: Intervals) -> Intervals:
        """
        Compute the difference of two sets of intervals.
        This method returns the intervals in self that are not overlapped by any interval in other.

        :param other: Another Intervals instance to subtract from this one.
        :return: A new Intervals instance representing the difference.
        """
        result_intervals = []

        for self_interval in self.intervals:
            current_intervals = [self_interval]

            for other_interval in other.intervals:
                new_intervals = []

                for interval in current_intervals:
                    if (
                        interval.end <= other_interval.start
                        or interval.start >= other_interval.end
                    ):
                        # No overlap
                        new_intervals.append(interval)
                    else:
                        # There is some overlap, potentially split the interval
                        if interval.start < other_interval.start:
                            new_intervals.append(
                                Interval(interval.start, other_interval.start)
                            )

                        if interval.end > other_interval.end:
                            new_intervals.append(
                                Interval(other_interval.end, interval.end)
                            )

                current_intervals = new_intervals

            result_intervals.extend(current_intervals)

        return Intervals(result_intervals).normalize()

    def symmetric_difference(self, other):
        raise NotImplementedError

    @overload
    def trim(self, data: pd.DataFrame) -> pd.DataFrame: ...
    @overload
    def trim(self, data: pd.Series) -> pd.Series: ...
    def trim(self, data: Data) -> Data:
        """
        Trim a DataFrame or Series to only include rows within the intervals specified in a {self.__class__.__name__} object.

        Parameters:
        df_or_series (pd.DataFrame or pd.Series): The DataFrame or Series to be trimmed.
        datetime_pairs ({self.__class__.__name__}): The {self.__class__.__name__} object specifying the intervals.

        Returns:
        pd.DataFrame or pd.Series: The trimmed DataFrame or Series.
        """
        interval_data = [
            data[pair.start : pair.end] for pair in self.normalize().intervals
        ]
        return pd.concat(interval_data)

    def adjust(self, delta: pd.Timedelta) -> Intervals:
        """
        Expand or contract each interval,
        + delta means expand,
        - delta means contract
        """
        pairs = []
        for pair in self.intervals:
            new_pair = Interval(pair.start - delta, pair.end + delta)

            if new_pair.start < new_pair.end:
                pairs.append(new_pair)

        return Intervals(pairs)

    def adjust_both(self, delta: dt, direction: str = "opposite") -> Interval:
        if direction not in ["same", "opposite"]:
            raise ValueError("direction must be either 'same' or 'opposite'")

        # direction = 1 if direction == "same" else -1

        new_intervals = []
        for interval in self.intervals:
            new_interval = interval.adjust_both(delta, direction)

            if new_interval.start < new_interval.end:
                new_intervals.append(new_interval)

        return Intervals(new_intervals).normalize()

    def adjust_start(self, delta: pd.Timedelta) -> Intervals:
        """
        Adjust only the start of each interval.
        """
        intervals = []
        for interval in self.intervals:
            new_pair = interval.adjust_start(delta)

            if new_pair.start < new_pair.end:
                intervals.append(new_pair)

        return Intervals(intervals).normalize()

    def adjust_end(self, delta: pd.Timedelta) -> Intervals:
        """
        Adjust only the end of each interval.
        """
        intervals = []
        for interval in self.intervals:
            new_pair = interval.adjust_end(delta)

            if new_pair.start < new_pair.end:
                intervals.append(new_pair)

        return Intervals(intervals).normalize()

    def contract(self, delta: pd.Timedelta) -> Intervals:
        new_intervals = []
        for interval in self.intervals:
            new_interval = interval.contract(delta)

            if new_interval.start < new_interval.end:
                new_intervals.append(new_interval)

        return Intervals(new_intervals).normalize()

    def expand(self, delta: pd.Timedelta) -> Intervals:
        new_intervals = []
        for interval in self.intervals:
            new_interval = interval.expand(delta)

            if new_interval.start < new_interval.end:
                new_intervals.append(new_interval)

        return Intervals(new_intervals).normalize()

    def normalize(self) -> Intervals:
        """
        Sort the datetime pairs and merge any overlapping intervals.
        """
        all_pairs = deque(sorted(self.intervals))

        # Merge overlapping intervals
        merged_pairs: list[Interval] = []

        while all_pairs:
            next_pair = all_pairs.popleft()

            if isinstance(next_pair[0], NaTType) and isinstance(next_pair[1], NaTType):
                continue

            # Drop reversed pairs where end is earlier than begin
            if next_pair.end < next_pair.start:
                continue

            if not merged_pairs:
                # If merged_pairs is empty, add the pair
                merged_pairs.append(next_pair)
            else:
                last = merged_pairs[-1]

                if last.end >= next_pair.start:
                    # If intervals overlap, merge them
                    new_end = max(last.end, next_pair.end)
                    merged_pairs[-1] = Interval(start=last.start, end=new_end)
                else:
                    # If no overlap, add as a new interval
                    merged_pairs.append(next_pair)

        if len(merged_pairs) == 0:
            return Intervals()

        return Intervals(merged_pairs)

    def __eq__(self, right: Intervals) -> bool:
        if not isinstance(right, Intervals):
            raise ValueError(
                "Cannot compare {} with <{}> {}".format(
                    self.__class__.__name__, type(right), repr(right)
                )
            )
        return self.intervals == right.intervals

    def __sub__(self, right: Intervals) -> Intervals:
        if not isinstance(right, Intervals):
            raise ValueError(
                "Cannot perform Subtraction of {} with <{}> {}".format(
                    self.__class__.__name__, type(right), repr(right)
                )
            )
        return self.difference(right)

    def __or__(self, right: Intervals) -> bool:
        if not isinstance(right, Intervals):
            raise ValueError(
                "Cannot perform union of {} with <{}> {}".format(
                    self.__class__.__name__, type(right), repr(right)
                )
            )
        return self.union(right)

    def __and__(self, right: Intervals) -> bool:
        if not isinstance(right, Intervals):
            raise ValueError(
                "Cannot perform intersection of {} with <{}> {}".format(
                    self.__class__.__name__, type(right), repr(right)
                )
            )
        return self.intersection(right)

    def __getitem__(self, a: int):
        return self.intervals[a]

    def __iter__(self):
        return iter(self.intervals)

    # def __repr__(self):
    #     """
    #     Return a string representation of the {self.__class__.__name__} instance.
    #     """
    #     return f"{self.__class__.__name__}({self.intervals})"

    #     def __rich__(self):
    #         return f"""\
    # {self.__class__.__name__}(
    #     {pformat(self.intervals)}
    # )"""

    def repr_start_duration(self):
        intervals = "\n    ".join(
            "('{}' -> '{}')".format(i.start, i.end - i.start) for i in self.intervals
        )
        return """\
{}(
    {}
)""".format(self.__class__.__name__, intervals)

    def len(self):
        return len(self.intervals)

    def __len__(self):
        return self.len()
