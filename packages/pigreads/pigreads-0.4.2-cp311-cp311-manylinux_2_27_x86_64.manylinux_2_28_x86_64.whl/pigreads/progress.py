"""
Progress bars
-------------
"""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Callable, Iterable, Iterator, Sized
from typing import Any, TextIO, TypeVar

from tqdm import tqdm

T = TypeVar("T")
"abstract type variable for generic types"


class BaseProgressIterator(Iterator[T]):
    """
    Base class for progress iterators.

    :param iterable: An iterable object.
    """

    def __init__(self, iterable: Iterable[T]) -> None:
        self._iterator = iter(iterable)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self._iterator)


class PlainProgressIterator(BaseProgressIterator[T]):
    """
    Plain progress iterator.

    This progress indicator simply prints the current index and total number of
    items.

    :param iterable: An iterable object.
    :param file: File object to write progress to.

    :ivar total: Total number of items.
    :ivar file: File object to write progress to.
    :ivar index: The current index.
    """

    def __init__(self, iterable: Iterable[T], file: TextIO = sys.stderr) -> None:
        super().__init__(iterable)
        self.total: int | None = len(iterable) if isinstance(iterable, Sized) else None
        self.file = file
        self.index = 0

    def __next__(self) -> T:
        self.index += 1
        item = next(self._iterator)
        print(f"{self.index}/{self.total}", file=self.file)
        return item


class JSONProgressIterator(BaseProgressIterator[T]):
    """
    JSON progress iterator.

    This progress indicator prints the current index, total number of items, time
    elapsed, time remaining, and time per iteration in JSON format.

    :param iterable: An iterable object.
    :param file: File object to write progress to.

    :ivar total: Total number of items.
    :ivar file: File object to write progress to.
    :ivar index: The current index.
    :ivar start: Start time.
    """

    def __init__(self, iterable: Iterable[T], file: TextIO = sys.stderr) -> None:
        super().__init__(iterable)
        self.total: int | None = len(iterable) if isinstance(iterable, Sized) else None
        self.file = file
        self.index = 0
        self.start = time.time()

    def __next__(self) -> T:
        self.index += 1
        item = next(self._iterator)
        elapsed = time.time() - self.start
        avg = elapsed / self.index
        print(
            json.dumps(
                {
                    "iteration_index": self.index,
                    "total_iterations": self.total,
                    "time_remaining": avg * (self.total - self.index)
                    if self.total is not None
                    else None,
                    "time_elapsed": elapsed,
                    "time_per_iteration": avg,
                }
            ),
            file=self.file,
        )
        return item


PROGRESS_ITERS: dict[str, Callable[[Any], Any]] = {
    "bar": tqdm,
    "json": JSONProgressIterator,
    "plain": PlainProgressIterator,
    "none": iter,
}
"""
Mapping of progress bar types to progress indicators.

Options:

- "bar": a bar with detailed progress information
- "json": JSON progress information
- "plain": plain text progress information
- "none": no progress information
"""
