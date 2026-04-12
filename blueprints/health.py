# coding=utf-8
# @Author  : Wodiao
# @Software: PyCharm
# @Time    : 2025/12/15 15:54
# @Project : nano_pj
# @File    : health.py
from flask import Blueprint, jsonify
from config.settings import ModelConfig

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Model service is running"})


@health_bp.route('/analysis/types', methods=['GET'])
def get_analysis_types():
    """
    返回当前系统支持的所有分析类型
    """
    svm_configs = ModelConfig.SVM_MODEL_CONFIGS
    quantitative_configs = ModelConfig.QUANTITATIVE_COMPOUND_CONFIGS
    tree_configs = ModelConfig.TREE_MODEL_CONFIGS

    data = {
        "svm_models": [
            {"id": k, "name": v["name"]}
            for k, v in svm_configs.items()
        ],
        "quantitative_compounds": [
            {"id": k, "name": v["name"], "unit": v["unit"]}
            for k, v in quantitative_configs.items()
        ],
        "tree_models": [
            {"id": k, "name": v["name"]}
            for k, v in tree_configs.items()
        ]
    }
    return jsonify({
        "status": "success",
        "data": data
    })
