# coding=utf-8
"""SQLite-backed model configuration repository."""

import os
import sqlite3
from contextlib import contextmanager

from config.model_config_seed import (
    QUANTITATIVE_COMPOUNDS,
    SVM_MODELS,
    TREE_MODELS,
)


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def _connection(db_path: str):
    conn = _connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def ensure_database(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with _connection(db_path) as conn:
        _create_schema(conn)
        _migrate_schema(conn)
        _seed_if_empty(conn)


def _table_columns(conn: sqlite3.Connection, table_name: str):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _add_column_if_missing(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_sql: str,
):
    if column_name not in _table_columns(conn, table_name):
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}")


def _mark_builtin_rows(conn: sqlite3.Connection, table_name: str, key_column: str, keys):
    key_list = list(keys)
    if not key_list:
        return
    placeholders = ",".join(["?"] * len(key_list))
    conn.execute(
        f"UPDATE {table_name} SET is_builtin = 1 WHERE {key_column} IN ({placeholders})",
        key_list,
    )


def _migrate_schema(conn: sqlite3.Connection):
    # Keep seed file as source of truth for default models, but persist result in DB.
    _add_column_if_missing(conn, "svm_models", "is_builtin", "INTEGER NOT NULL DEFAULT 0")
    _add_column_if_missing(conn, "tree_models", "is_builtin", "INTEGER NOT NULL DEFAULT 0")
    _add_column_if_missing(conn, "quantitative_compounds", "is_builtin", "INTEGER NOT NULL DEFAULT 0")

    _add_column_if_missing(conn, "svm_models", "name_en", "TEXT")
    _add_column_if_missing(conn, "svm_models", "name_zh", "TEXT")
    _add_column_if_missing(conn, "tree_models", "name_en", "TEXT")
    _add_column_if_missing(conn, "tree_models", "name_zh", "TEXT")
    _add_column_if_missing(conn, "quantitative_compounds", "name_en", "TEXT")
    _add_column_if_missing(conn, "quantitative_compounds", "name_zh", "TEXT")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS probability_labels (
            label_key TEXT PRIMARY KEY,
            label_en TEXT NOT NULL,
            label_zh TEXT NOT NULL
        )
        """
    )

    _mark_builtin_rows(conn, "svm_models", "model_key", SVM_MODELS.keys())
    _mark_builtin_rows(conn, "tree_models", "model_key", TREE_MODELS.keys())
    _mark_builtin_rows(conn, "quantitative_compounds", "compound_key", QUANTITATIVE_COMPOUNDS.keys())

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS site_builtin_registry (
            site_key TEXT PRIMARY KEY,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (site_key)
                REFERENCES site_profiles(site_key)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
        """
    )

    # Migrate legacy built-in marker from site_profiles.is_builtin to dedicated registry table.
    conn.execute(
        """
        INSERT OR IGNORE INTO site_builtin_registry (site_key)
        SELECT site_key
        FROM site_profiles
        WHERE is_builtin = 1
        """
    )

    # site_allowed_methods is deprecated. Methods are derived from site_allowed_models.
    conn.execute("DROP TABLE IF EXISTS site_allowed_methods")


def _create_schema(conn: sqlite3.Connection):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS svm_models (
            model_key TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            name_en TEXT NOT NULL,
            name_zh TEXT NOT NULL,
            model_rel_path TEXT NOT NULL,
            scaler_rel_path TEXT NOT NULL,
            training_rel_path TEXT NOT NULL,
            default_txt_rel_path TEXT NOT NULL,
            is_builtin INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tree_models (
            model_key TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            model_rel_path TEXT NOT NULL,
            training_rel_path TEXT NOT NULL,
            default_txt_rel_path TEXT NOT NULL,
            is_builtin INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS quantitative_compounds (
            compound_key TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            required_rows INTEGER NOT NULL,
            formula_a REAL NOT NULL,
            formula_b REAL NOT NULL,
            formula_description TEXT NOT NULL,
            transform_type TEXT,
            is_builtin INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS quantitative_intensity_points (
            compound_key TEXT NOT NULL,
            point_no INTEGER NOT NULL CHECK (point_no IN (1, 2)),
            row_number INTEGER NOT NULL,
            row_index INTEGER NOT NULL,
            column_index INTEGER NOT NULL,
            PRIMARY KEY (compound_key, point_no),
            FOREIGN KEY (compound_key)
                REFERENCES quantitative_compounds(compound_key)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS site_profiles (
            site_key TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            is_builtin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS site_allowed_models (
            site_key TEXT NOT NULL,
            method_type TEXT NOT NULL CHECK (method_type IN ('svm', 'tree', 'quantitative')),
            model_key TEXT NOT NULL,
            PRIMARY KEY (site_key, method_type, model_key),
            FOREIGN KEY (site_key)
                REFERENCES site_profiles(site_key)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        );

            CREATE TABLE IF NOT EXISTS site_builtin_registry (
                site_key TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (site_key)
                REFERENCES site_profiles(site_key)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            );

        CREATE TABLE IF NOT EXISTS probability_labels (
            label_key TEXT PRIMARY KEY,
            label_en TEXT NOT NULL,
            label_zh TEXT NOT NULL
        );
        """
    )


def _table_has_data(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(f"SELECT 1 FROM {table_name} LIMIT 1").fetchone()
    return row is not None


def _seed_if_empty(conn: sqlite3.Connection):
    if not _table_has_data(conn, "svm_models"):
        for model_key, config in SVM_MODELS.items():
            conn.execute(
                """
                INSERT INTO svm_models (
                    model_key, name, name_en, name_zh, model_rel_path, scaler_rel_path,
                    training_rel_path, default_txt_rel_path, is_builtin, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
                """,
                (
                    model_key,
                    config["name"],
                    config.get("name_en", config["name"]),
                    config.get("name_zh", config["name"]),
                    config["model_rel_path"],
                    config["scaler_rel_path"],
                    config["training_rel_path"],
                    config["default_txt_rel_path"],
                ),
            )

    if not _table_has_data(conn, "tree_models"):
        for model_key, config in TREE_MODELS.items():
            conn.execute(
                """
                INSERT INTO tree_models (
                    model_key, name, model_rel_path,
                    training_rel_path, default_txt_rel_path, is_builtin, is_active
                ) VALUES (?, ?, ?, ?, ?, 1, 1)
                """,
                (
                    model_key,
                    config["name"],
                    config["model_rel_path"],
                    config["training_rel_path"],
                    config["default_txt_rel_path"],
                ),
            )

    if not _table_has_data(conn, "quantitative_compounds"):
        for compound_key, config in QUANTITATIVE_COMPOUNDS.items():
            formula = config["formula"]
            conn.execute(
                """
                INSERT INTO quantitative_compounds (
                    compound_key, name, unit, required_rows,
                    formula_a, formula_b, formula_description, transform_type, is_builtin, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
                """,
                (
                    compound_key,
                    config["name"],
                    config["unit"],
                    config["required_rows"],
                    formula["a"],
                    formula["b"],
                    formula["description"],
                    config.get("transform"),
                ),
            )

            intensity_1 = config["intensity_1"]
            intensity_2 = config["intensity_2"]
            conn.execute(
                """
                INSERT INTO quantitative_intensity_points (
                    compound_key, point_no, row_number, row_index, column_index
                ) VALUES (?, 1, ?, ?, ?)
                """,
                (
                    compound_key,
                    intensity_1["row"],
                    intensity_1["index"],
                    intensity_1["column"],
                ),
            )
            conn.execute(
                """
                INSERT INTO quantitative_intensity_points (
                    compound_key, point_no, row_number, row_index, column_index
                ) VALUES (?, 2, ?, ?, ?)
                """,
                (
                    compound_key,
                    intensity_2["row"],
                    intensity_2["index"],
                    intensity_2["column"],
                ),
            )

def _to_assets_path(assets_root: str, rel_path: str) -> str:
    return os.path.join(assets_root, rel_path.replace("/", os.sep))


def load_svm_configs(db_path: str, assets_root: str):
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT model_key, name, model_rel_path, scaler_rel_path, training_rel_path, default_txt_rel_path
            FROM svm_models
            WHERE is_active = 1
            ORDER BY model_key
            """
        ).fetchall()

    return {
        row["model_key"]: {
            "name": row["name"],
            "model_path": _to_assets_path(assets_root, row["model_rel_path"]),
            "scaler_path": _to_assets_path(assets_root, row["scaler_rel_path"]),
            "training_csv": _to_assets_path(assets_root, row["training_rel_path"]),
            "default_txt": _to_assets_path(assets_root, row["default_txt_rel_path"]),
        }
        for row in rows
    }


def load_tree_configs(db_path: str, assets_root: str):
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT model_key, name, model_rel_path, training_rel_path, default_txt_rel_path
            FROM tree_models
            WHERE is_active = 1
            ORDER BY model_key
            """
        ).fetchall()

    return {
        row["model_key"]: {
            "name": row["name"],
            "model_path": _to_assets_path(assets_root, row["model_rel_path"]),
            "training_csv": _to_assets_path(assets_root, row["training_rel_path"]),
            "default_txt": _to_assets_path(assets_root, row["default_txt_rel_path"]),
        }
        for row in rows
    }


def load_quantitative_configs(db_path: str):
    with _connection(db_path) as conn:
        compounds = conn.execute(
            """
            SELECT compound_key, name, unit, required_rows, formula_a, formula_b,
                   formula_description, transform_type
            FROM quantitative_compounds
            WHERE is_active = 1
            ORDER BY compound_key
            """
        ).fetchall()

        points = conn.execute(
            """
            SELECT compound_key, point_no, row_number, row_index, column_index
            FROM quantitative_intensity_points
            """
        ).fetchall()

    point_map = {}
    for row in points:
        point_map[(row["compound_key"], row["point_no"])] = {
            "row": row["row_number"],
            "index": row["row_index"],
            "column": row["column_index"],
        }

    result = {}
    for row in compounds:
        key = row["compound_key"]
        result[key] = {
            "name": row["name"],
            "unit": row["unit"],
            "required_rows": row["required_rows"],
            "intensity_1": point_map[(key, 1)],
            "intensity_2": point_map[(key, 2)],
            "formula": {
                "a": row["formula_a"],
                "b": row["formula_b"],
                "description": row["formula_description"],
            },
        }
        if row["transform_type"]:
            result[key]["transform"] = row["transform_type"]

    return result


def list_svm_models(db_path: str):
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT model_key, name_en, name_zh, model_rel_path, scaler_rel_path,
                     training_rel_path, default_txt_rel_path, is_builtin, is_active,
                   created_at, updated_at
            FROM svm_models
            ORDER BY updated_at DESC, model_key
            """
        ).fetchall()
    return [dict(row) for row in rows]


def svm_model_exists(db_path: str, model_key: str) -> bool:
    with _connection(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM svm_models WHERE model_key = ? LIMIT 1",
            (model_key,),
        ).fetchone()
    return row is not None


def create_svm_model(
    db_path: str,
    model_key: str,
    name_en: str,
    name_zh: str,
    model_rel_path: str,
    scaler_rel_path: str,
    training_rel_path: str,
    default_txt_rel_path: str,
):
    with _connection(db_path) as conn:
        auto_name = f"{model_key.upper()}_SVM"
        conn.execute(
            """
            INSERT INTO svm_models (
                model_key, name, name_en, name_zh, model_rel_path, scaler_rel_path,
                training_rel_path, default_txt_rel_path, is_builtin, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
            """,
            (
                model_key,
                auto_name,
                name_en,
                name_zh,
                model_rel_path,
                scaler_rel_path,
                training_rel_path,
                default_txt_rel_path,
            ),
        )


def get_svm_model(db_path: str, model_key: str):
    with _connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT model_key, name_en, name_zh, model_rel_path, scaler_rel_path,
                     training_rel_path, default_txt_rel_path, is_builtin, is_active,
                   created_at, updated_at
            FROM svm_models
            WHERE model_key = ?
            LIMIT 1
            """,
            (model_key,),
        ).fetchone()
    return dict(row) if row else None


def get_svm_model_usage_in_sites(db_path: str, model_key: str):
    """获取使用该SVM模型的所有站点"""
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT sp.site_key, sp.display_name
            FROM site_profiles sp
            INNER JOIN site_allowed_models sam ON sp.site_key = sam.site_key
            WHERE sam.method_type = 'svm' AND sam.model_key = ?
            ORDER BY sp.site_key
            """,
            (model_key,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_svm_model(db_path: str, model_key: str) -> int:
    with _connection(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM svm_models WHERE model_key = ?",
            (model_key,),
        )
    return cursor.rowcount


def set_svm_model_active(db_path: str, model_key: str, is_active: bool) -> int:
    with _connection(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE svm_models
            SET is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE model_key = ?
            """,
            (1 if is_active else 0, model_key),
        )
    return cursor.rowcount


def get_probability_labels(db_path: str, label_keys):
    keys = [str(k).strip() for k in label_keys if str(k).strip()]
    if not keys:
        return {}

    placeholders = ",".join(["?"] * len(keys))
    with _connection(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT label_key, label_en, label_zh
            FROM probability_labels
            WHERE label_key IN ({placeholders})
            """,
            keys,
        ).fetchall()

    return {row["label_key"]: {"label_en": row["label_en"], "label_zh": row["label_zh"]} for row in rows}


def upsert_probability_labels(db_path: str, labels):
    clean_rows = []
    for item in labels:
        label_key = str(item.get("label_key", "")).strip()
        label_en = str(item.get("label_en", "")).strip()
        label_zh = str(item.get("label_zh", "")).strip()
        if not label_key or not label_en or not label_zh:
            continue
        clean_rows.append((label_key, label_en, label_zh))

    if not clean_rows:
        return 0

    with _connection(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO probability_labels (label_key, label_en, label_zh)
            VALUES (?, ?, ?)
            ON CONFLICT(label_key) DO UPDATE SET
                label_en = excluded.label_en,
                label_zh = excluded.label_zh
            """,
            clean_rows,
        )

    return len(clean_rows)


def list_probability_labels(db_path: str):
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT label_key, label_en, label_zh
            FROM probability_labels
            ORDER BY label_key
            """
        ).fetchall()

    return [dict(row) for row in rows]


def list_tree_models(db_path: str):
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT model_key, name,
                   COALESCE(name_en, name) AS name_en,
                   COALESCE(name_zh, name) AS name_zh,
                   model_rel_path,
                   training_rel_path, default_txt_rel_path,
                     is_builtin, is_active, created_at, updated_at
            FROM tree_models
            ORDER BY updated_at DESC, model_key
            """
        ).fetchall()
    return [dict(row) for row in rows]


def create_tree_model(
    db_path: str,
    model_key: str,
    name_en: str,
    name_zh: str,
    model_rel_path: str,
    training_rel_path: str,
    default_txt_rel_path: str,
):
    with _connection(db_path) as conn:
        auto_name = f"{model_key.upper()}_TREE"
        conn.execute(
            """
            INSERT INTO tree_models (
                model_key, name, name_en, name_zh, model_rel_path,
                training_rel_path, default_txt_rel_path, is_builtin, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1)
            """,
            (
                model_key,
                auto_name,
                name_en,
                name_zh,
                model_rel_path,
                training_rel_path,
                default_txt_rel_path,
            ),
        )


def get_tree_model(db_path: str, model_key: str):
    with _connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT model_key, name,
                   COALESCE(name_en, name) AS name_en,
                   COALESCE(name_zh, name) AS name_zh,
                   model_rel_path,
                   training_rel_path, default_txt_rel_path,
                     is_builtin, is_active, created_at, updated_at
            FROM tree_models
            WHERE model_key = ?
            LIMIT 1
            """,
            (model_key,),
        ).fetchone()
    return dict(row) if row else None


def get_tree_model_usage_in_sites(db_path: str, model_key: str):
    """获取使用该决策树模型的所有站点"""
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT sp.site_key, sp.display_name
            FROM site_profiles sp
            INNER JOIN site_allowed_models sam ON sp.site_key = sam.site_key
            WHERE sam.method_type = 'tree' AND sam.model_key = ?
            ORDER BY sp.site_key
            """,
            (model_key,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_tree_model(db_path: str, model_key: str) -> int:
    with _connection(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM tree_models WHERE model_key = ?",
            (model_key,),
        )
    return cursor.rowcount


def list_quantitative_compounds(db_path: str):
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT qc.compound_key, qc.name, qc.name_en, qc.name_zh, qc.unit, qc.required_rows,
                   qc.formula_a, qc.formula_b, qc.formula_description,
                     qc.transform_type, qc.is_builtin, qc.is_active,
                   p1.row_number AS intensity1_row,
                   p1.row_index AS intensity1_index,
                   p1.column_index AS intensity1_col,
                   p2.row_number AS intensity2_row,
                   p2.row_index AS intensity2_index,
                   p2.column_index AS intensity2_col
            FROM quantitative_compounds qc
            LEFT JOIN quantitative_intensity_points p1
              ON qc.compound_key = p1.compound_key AND p1.point_no = 1
            LEFT JOIN quantitative_intensity_points p2
              ON qc.compound_key = p2.compound_key AND p2.point_no = 2
            ORDER BY qc.updated_at DESC, qc.compound_key
            """
        ).fetchall()
    return [dict(row) for row in rows]


def quantitative_compound_exists(db_path: str, compound_key: str) -> bool:
    with _connection(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM quantitative_compounds WHERE compound_key = ? LIMIT 1",
            (compound_key,),
        ).fetchone()
    return row is not None


def create_quantitative_compound(
    db_path: str,
    compound_key: str,
    name: str,
    unit: str,
    required_rows: int,
    formula_a: float,
    formula_b: float,
    formula_description: str,
    intensity_1_row: int,
    intensity_1_index: int,
    intensity_1_col: int,
    intensity_2_row: int,
    intensity_2_index: int,
    intensity_2_col: int,
    transform_type: str = None,
    name_en: str = None,
    name_zh: str = None,
):
    with _connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO quantitative_compounds (
                compound_key, name, name_en, name_zh, unit, required_rows,
                formula_a, formula_b, formula_description,
                transform_type, is_builtin, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1)
            """,
            (
                compound_key,
                name,
                name_en,
                name_zh,
                unit,
                required_rows,
                formula_a,
                formula_b,
                formula_description,
                transform_type,
            ),
        )
        conn.execute(
            """
            INSERT INTO quantitative_intensity_points (
                compound_key, point_no, row_number, row_index, column_index
            ) VALUES (?, 1, ?, ?, ?)
            """,
            (compound_key, intensity_1_row, intensity_1_index, intensity_1_col),
        )
        conn.execute(
            """
            INSERT INTO quantitative_intensity_points (
                compound_key, point_no, row_number, row_index, column_index
            ) VALUES (?, 2, ?, ?, ?)
            """,
            (compound_key, intensity_2_row, intensity_2_index, intensity_2_col),
        )


def get_quantitative_compound(db_path: str, compound_key: str):
    with _connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT compound_key, name, name_en, name_zh, unit, required_rows,
                   formula_a, formula_b, formula_description,
                     transform_type, is_builtin, is_active, created_at, updated_at
            FROM quantitative_compounds
            WHERE compound_key = ?
            LIMIT 1
            """,
            (compound_key,),
        ).fetchone()
    return dict(row) if row else None


def get_quantitative_model_usage_in_sites(db_path: str, compound_key: str):
    """获取使用该定量模型的所有站点"""
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT sp.site_key, sp.display_name
            FROM site_profiles sp
            INNER JOIN site_allowed_models sam ON sp.site_key = sam.site_key
            WHERE sam.method_type = 'quantitative' AND sam.model_key = ?
            ORDER BY sp.site_key
            """,
            (compound_key,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_quantitative_compound(db_path: str, compound_key: str) -> int:
    with _connection(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM quantitative_compounds WHERE compound_key = ?",
            (compound_key,),
        )
    return cursor.rowcount


def list_site_profiles(db_path: str):
    with _connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT sp.site_key, sp.display_name,
                   CASE WHEN sbr.site_key IS NULL THEN 0 ELSE 1 END AS is_builtin,
                   sp.created_at, sp.updated_at,
                   COUNT(DISTINCT sao.method_type) AS method_count,
                   COUNT(DISTINCT sao.model_key) AS model_count
            FROM site_profiles sp
            LEFT JOIN site_builtin_registry sbr ON sp.site_key = sbr.site_key
            LEFT JOIN site_allowed_models sao ON sp.site_key = sao.site_key
            GROUP BY sp.site_key, sp.display_name, sbr.site_key, sp.created_at, sp.updated_at
            ORDER BY sp.updated_at DESC, sp.created_at DESC, sp.site_key ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_site_profile(db_path: str, site_key: str):
    with _connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT sp.site_key, sp.display_name,
                   CASE WHEN sbr.site_key IS NULL THEN 0 ELSE 1 END AS is_builtin,
                   sp.created_at, sp.updated_at
            FROM site_profiles sp
            LEFT JOIN site_builtin_registry sbr ON sp.site_key = sbr.site_key
                 WHERE sp.site_key = ?
            LIMIT 1
            """,
            (site_key,),
        ).fetchone()
    return dict(row) if row else None


def site_profile_exists(db_path: str, site_key: str) -> bool:
    with _connection(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM site_profiles WHERE site_key = ? LIMIT 1",
            (site_key,),
        ).fetchone()
    return row is not None


def create_site_profile(db_path: str, site_key: str, display_name: str):
    with _connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO site_profiles (site_key, display_name)
            VALUES (?, ?)
            """,
            (site_key, display_name),
        )


def delete_site_profile(db_path: str, site_key: str) -> int:
    with _connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM site_profiles WHERE site_key = ?", (site_key,))
    return cursor.rowcount


def save_site_scope(
    db_path: str,
    site_key: str,
    svm_model_keys,
    tree_model_keys,
    quantitative_keys,
):
    with _connection(db_path) as conn:
        conn.execute("DELETE FROM site_allowed_models WHERE site_key = ?", (site_key,))

        for model_key in svm_model_keys:
            conn.execute(
                "INSERT INTO site_allowed_models (site_key, method_type, model_key) VALUES (?, 'svm', ?)",
                (site_key, model_key),
            )
        for model_key in tree_model_keys:
            conn.execute(
                "INSERT INTO site_allowed_models (site_key, method_type, model_key) VALUES (?, 'tree', ?)",
                (site_key, model_key),
            )
        for model_key in quantitative_keys:
            conn.execute(
                "INSERT INTO site_allowed_models (site_key, method_type, model_key) VALUES (?, 'quantitative', ?)",
                (site_key, model_key),
            )


def get_site_scope(db_path: str, site_key: str):
    with _connection(db_path) as conn:
        model_rows = conn.execute(
            """
            SELECT method_type, model_key
            FROM site_allowed_models
            WHERE site_key = ?
            ORDER BY method_type, model_key
            """,
            (site_key,),
        ).fetchall()

    model_map = {"svm": [], "tree": [], "quantitative": []}
    for row in model_rows:
        model_map[row["method_type"]].append(row["model_key"])

    methods = [k for k in ["svm", "tree", "quantitative"] if model_map[k]]

    return {
        "methods": methods,
        "svm": model_map["svm"],
        "tree": model_map["tree"],
        "quantitative": model_map["quantitative"],
    }


def get_all_lang_configs(db_path: str):
    """"""
    with _connection(db_path) as conn:
        svm_rows = conn.execute("SELECT model_key, name_en, name_zh FROM svm_models").fetchall()
        tree_rows = conn.execute("SELECT model_key, name_en, name_zh FROM tree_models").fetchall()
        q_rows = conn.execute("SELECT compound_key as model_key, name_en, name_zh FROM quantitative_compounds").fetchall()
        prob_rows = conn.execute("SELECT label_key, label_en, label_zh FROM probability_labels").fetchall()

    en_model = {"title": "Model"}
    zh_model = {"title": "模型选择"}
    en_prob = {"title": "Probability Distribution by Category"}
    zh_prob = {"title": "各类别概率分布"}

    for row in svm_rows + tree_rows + q_rows:
        k = row["model_key"]
        if row["name_en"] is not None:
            en_model[k] = row["name_en"]
        if row["name_zh"] is not None:
            zh_model[k] = row["name_zh"]

    for row in prob_rows:
        k = row["label_key"]
        if row["label_en"] is not None:
            en_prob[k] = row["label_en"]
        if row["label_zh"] is not None:
            zh_prob[k] = row["label_zh"]

    return {
        "en": {
            "model": en_model,
            "probability": en_prob
        },
        "zh-CN": {
            "model": zh_model,
            "probability": zh_prob
        }
    }


def get_site_runtime_config(db_path: str, site_key: str):
    profile = get_site_profile(db_path, site_key)
    if not profile:
        return None

    scope = get_site_scope(db_path, site_key)
    methods = scope["methods"]

    with _connection(db_path) as conn:
        svm_rows = conn.execute(
            """
            SELECT model_key, name
            FROM svm_models
            WHERE model_key IN (
                SELECT model_key FROM site_allowed_models
                WHERE site_key = ? AND method_type = 'svm'
            )
            ORDER BY model_key
            """,
            (site_key,),
        ).fetchall()

        tree_rows = conn.execute(
            """
            SELECT model_key, name
            FROM tree_models
            WHERE model_key IN (
                SELECT model_key FROM site_allowed_models
                WHERE site_key = ? AND method_type = 'tree'
            )
            ORDER BY model_key
            """,
            (site_key,),
        ).fetchall()

        q_rows = conn.execute(
            """
            SELECT compound_key, name
            FROM quantitative_compounds
            WHERE compound_key IN (
                SELECT model_key FROM site_allowed_models
                WHERE site_key = ? AND method_type = 'quantitative'
            )
            ORDER BY compound_key
            """,
            (site_key,),
        ).fetchall()

    calc_types = []
    if "svm" in methods:
        calc_types.append({"value": "svm", "label": "method.type.svm"})
    if "tree" in methods:
        calc_types.append({"value": "tree", "label": "method.type.tree"})
    if "quantitative" in methods:
        calc_types.append({"value": "quantitative", "label": "method.type.quantitative"})

    return {
        "site": {
            "site_key": profile["site_key"],
            "display_name": profile["display_name"],
            "is_builtin": profile["is_builtin"],
        },
        "calculation_types": calc_types,
        "models": {
            "svm": [{"key": row["model_key"], "name": row["name"]} for row in svm_rows],
            "tree": [{"key": row["model_key"], "name": row["name"]} for row in tree_rows],
            "quantitative": [{"key": row["compound_key"], "name": row["name"]} for row in q_rows],
        },
    }
