#!/usr/bin/env python3
"""
Manually clean up code by removing unneeded divisions by zero
-------------------------------------------------------------

Usage: replace_safe_division.py before.yaml after.yaml
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

OK_TO_REPLACE: dict[str, bool] = {}


def ok_to_replace(term: str) -> bool:
    """
    If a term may be replaced, return True.

    :param term: String representation of a mathematical term.
    :return: Boolean.
    """
    if term not in OK_TO_REPLACE:
        OK_TO_REPLACE[term] = input(
            f"{term}\nCan this term be zero? [y/N] "
        ).strip().lower() in ["", "n", "N"]
    return OK_TO_REPLACE[term]


def find_matching_parentheses(text: str) -> int:
    """
    Find the index of the first ``)`` ignoring all matching pairs of ``()`` until
    then.

    :param text: A string.
    :return: Index of the first matching ``)``.
    """
    stack = []
    for i, char in enumerate(text):
        if char == "(":
            stack.append(i)
        elif char == ")":
            if stack:
                stack.pop()
            else:
                return i
    return -1


def process(text: str) -> str:
    """
    Replace occurrences of safe division with un-safe division if the user gives
    their ok to replace it.

    :param text: String to process.
    :return: Modified string.
    """
    match = re.search(r"/\s*\(\(\s*fabs\s*\(", text)  # )))
    if match:
        i0 = match.start()
        i1 = i0 + text[i0:].find("(")  # )
        i2 = match.end()
        i3 = i2 + find_matching_parentheses(text[i2:])
        if i3 < i2:
            message = "Unmatched parentheses!"
            raise ValueError(message)
        i4 = i1 + 1 + find_matching_parentheses(text[i1 + 1 :])
        if i4 < i1:
            message = "Unmatched parentheses!"
            raise ValueError(message)

        term = text[i2:i3]

        code = text[i1 : i4 + 1].replace(" ", "")
        code_ref = f"((fabs({term})<VERY_SMALL_NUMBER)?(({term}<0.0)?-VERY_SMALL_NUMBER:VERY_SMALL_NUMBER):{term})".replace(
            " ", ""
        )
        if code != code_ref:
            message = "Code:\n"
            message += code
            message = "\nExpected:\n"
            message += code_ref
            message += "\nCode does not have the expected format!"
            raise ValueError(message)

        term = process(term)
        rest = process(text[i4:])

        if ok_to_replace(term):
            text = f"{text[: i1 + 1]}{term}{rest}"
        else:
            text = f"{text[:i0]}* safe_divide(1.0, {term}{rest}"
            # text = f"{text[:i4]}BLUB{rest}"
    return text


if __name__ == "__main__":
    with Path(sys.argv[1]).open() as fr, Path(sys.argv[2]).open("w") as fw:
        fw.write(process(fr.read()))
