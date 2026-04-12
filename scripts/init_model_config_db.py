# coding=utf-8
"""Initialize and inspect model configuration SQLite database."""

import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.model_config_repository import ensure_database
from config.settings import ModelConfig


def _count(conn, table_name: str) -> int:
    row = conn.execute(f"SELECT COUNT(1) AS cnt FROM {table_name}").fetchone()
    return int(row[0])


def main():
    ensure_database(ModelConfig.DB_PATH)

    conn = sqlite3.connect(ModelConfig.DB_PATH)
    try:
        svm_count = _count(conn, "svm_models")
        tree_count = _count(conn, "tree_models")
        compound_count = _count(conn, "quantitative_compounds")
        point_count = _count(conn, "quantitative_intensity_points")
    finally:
        conn.close()

    print(f"DB Path: {ModelConfig.DB_PATH}")
    print(f"svm_models: {svm_count}")
    print(f"tree_models: {tree_count}")
    print(f"quantitative_compounds: {compound_count}")
    print(f"quantitative_intensity_points: {point_count}")


if __name__ == "__main__":
    main()
