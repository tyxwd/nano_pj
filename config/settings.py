# coding=utf-8
# @Author  : Wodiao
# @Software: PyCharm
# @Time    : 2025/12/15 15:47
# @Project : nano_pj
# @File    : settings.py
import os

from config.model_config_repository import (
    ensure_database,
    load_quantitative_configs,
    load_svm_configs,
    load_tree_configs,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_ROOT = os.path.join(PROJECT_ROOT, 'public_storage')
ASSETS_ROOT = os.path.join(PROJECT_ROOT, 'assets')

ALLOWED_EXTENSIONS = {'txt'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
MODEL_CONFIG_DB_PATH = os.path.join(PROJECT_ROOT, 'config', 'model_configs.sqlite3')


class _DynamicConfigAccessor:
    def __init__(self, loader):
        self._loader = loader

    def __get__(self, instance, owner):
        owner._ensure_db()
        return self._loader(owner)


class ModelConfig:
    DB_PATH = MODEL_CONFIG_DB_PATH
    SVM_MODEL_CONFIGS = _DynamicConfigAccessor(
        lambda cls: load_svm_configs(cls.DB_PATH, ASSETS_ROOT)
    )
    QUANTITATIVE_COMPOUND_CONFIGS = _DynamicConfigAccessor(
        lambda cls: load_quantitative_configs(cls.DB_PATH)
    )
    TREE_MODEL_CONFIGS = _DynamicConfigAccessor(
        lambda cls: load_tree_configs(cls.DB_PATH, ASSETS_ROOT)
    )

    @classmethod
    def _ensure_db(cls):
        ensure_database(cls.DB_PATH)
