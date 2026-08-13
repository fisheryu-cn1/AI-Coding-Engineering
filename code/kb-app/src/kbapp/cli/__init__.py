"""Typer command layer.

Each submodule owns one top-level subcommand group. Business logic lives in
``kbapp.core`` / ``kbapp.pipeline`` / ``kbapp.retrieve``; the CLI is a thin
adapter that parses arguments and delegates.
"""
