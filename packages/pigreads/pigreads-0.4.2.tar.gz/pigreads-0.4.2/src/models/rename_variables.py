#!/usr/bin/env python3
"""
Manually clean up code by renaming variables
--------------------------------------------
"""

from __future__ import annotations

import re
from pathlib import Path

import click


def parse_rules(rule_lines: list[str]) -> list[tuple[re.Pattern[str], str]]:
    """
    Parse regex renaming rules from lines in a file.

    :param rule_lines: list of lines of the form '<pattern> -> <replacement>'
    :return: list of compiled regex patterns and their replacements
    """
    rules = []
    for line in rule_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            pattern_str, repl = map(str.strip, stripped.split("->", 1))
            pattern = re.compile(pattern_str)
            rules.append((pattern, repl))
        except Exception as e:
            message = f"Invalid rule line: {line!r}"
            raise ValueError(message) from e
    return rules


def extract_identifiers(code: str) -> set[str]:
    """
    Extract variable-like identifiers from C source code.

    :param code: C code string
    :return: set of variable names
    """
    # This is a heuristic and not a full parser.
    return set(re.findall(r"\b[_a-zA-Z][_a-zA-Z0-9]*\b", code))


def apply_rules(
    identifiers: set[str], rules: list[tuple[re.Pattern[str], str]]
) -> tuple[dict[str, str], set[str]]:
    """
    Apply renaming rules to a set of identifiers.

    :param identifiers: Original variable names
    :param rules: list of (regex, replacement)
    :return: tuple of (mapping of renamed vars, unchanged vars)
    """
    mapping: dict[str, str] = {}
    seen_new_names: dict[str, str] = {}
    unchanged: set[str] = set()

    for ident in identifiers:
        new = ident
        for pattern, repl in rules:
            new_candidate = pattern.sub(repl, new)
            if new_candidate != new:
                new = new_candidate
        if new != ident:
            if new in seen_new_names and seen_new_names[new] != ident:
                message = (
                    f"Conflict: {ident} and {seen_new_names[new]} both map to {new}"
                )
                raise ValueError(message)
            mapping[ident] = new
            seen_new_names[new] = ident
        else:
            unchanged.add(ident)
    return mapping, unchanged


def replace_in_code(code: str, mapping: dict[str, str]) -> str:
    """
    Replace variable names in code using word boundaries.

    :param code: Original code
    :param mapping: dict of old name to new name
    :return: Modified code
    """
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    for old in sorted_keys:
        code = re.sub(rf"\b{re.escape(old)}\b", mapping[old], code)
    return code


@click.command()
@click.argument("c_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument(
    "rule_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output file path.",
)
def main(c_file: Path, rule_file: Path, output: Path | None) -> None:
    """
    Rename variables in a C_FILE using regex RULE_FILE.
    """
    code = c_file.read_text()
    rules = parse_rules(rule_file.read_text().splitlines())
    identifiers = extract_identifiers(code)
    mapping, unchanged = apply_rules(identifiers, rules)
    new_code = replace_in_code(code, mapping)

    click.echo("\nRenamed variables:")
    for old, new in sorted(mapping.items()):
        click.echo(f"  {old} -> {new}")

    click.echo("\n✅ Unchanged variables:")
    for name in sorted(unchanged):
        click.echo(f"  {name}")

    out_path = output or c_file.with_suffix(".new")
    out_path.write_text(new_code)
    click.echo(f"\nModified code written to: {out_path}")


if __name__ == "__main__":
    main()
