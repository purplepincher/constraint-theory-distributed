"""CLI entry-point: ``python -m constraint_theory_core <subcommand>``."""

from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m constraint_theory_core <subcommand> [options]")
        print("Subcommands: exercise")
        sys.exit(1)

    subcommand = sys.argv[1]
    rest = sys.argv[2:]

    if subcommand == "exercise":
        from .exercises import _cli_exercise
        _cli_exercise(rest)
    else:
        print(f"Unknown subcommand: {subcommand!r}")
        print("Available: exercise")
        sys.exit(1)


if __name__ == "__main__":
    main()
