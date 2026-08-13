"""Core building blocks shared by CLI, MCP, and Web entrypoints.

Submodules:
    config      — config.yaml load/dump/atomic-write + audit
    paths       — data directory layout
    fingerprint — SHA-256 + mtime
    lock        — write lock with PID liveness + stale recovery
    registry    — SQLite 五张表 (files / tasks / inbox / config_audit / llm_usage)
    task        — task state machine + 30s→1m→5m backoff + crash recovery
"""
