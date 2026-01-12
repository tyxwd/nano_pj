# coding=utf-8
# @Author  : Wodiao
# @Software: PyCharm
# @Time    : 2025/12/15 15:47
# @Project : nano_pj
# @File    : settings.py
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_ROOT = os.path.join(PROJECT_ROOT, 'public_storage')
ASSETS_ROOT = os.path.join(PROJECT_ROOT, 'assets')

ALLOWED_EXTENSIONS = {'txt'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB


class ModelConfig:
    SVM_MODEL_CONFIGS = {
        "default": {
            "name": "default",
            "model_path": os.path.join(ASSETS_ROOT, "svm/default/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/default/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/default/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/default/newdata.txt")
        }
    }
    QUANTITATIVE_COMPOUND_CONFIGS = {
        'retinol': {
            'name': 'Retinol',
            'unit': 'ug/ml',
            'required_rows': 796,
            'intensity_1': {'row': 468, 'index': 467, 'column': 1},  # 第468行，第2列
            'intensity_2': {'row': 796, 'index': 795, 'column': 1},  # 第796行，第2列
            'formula': {
                'a': 0.0242,
                'b': 0.8753,
                'description': 'x = (y - 0.8753) / 0.0242'
            }
        },
        'vitamin_k': {
            'name': 'Vitamin K',
            'unit': 'ug/ml',
            'required_rows': 796,
            'intensity_1': {'row': 468, 'index': 467, 'column': 1},  # 第468行，第2列
            'intensity_2': {'row': 796, 'index': 795, 'column': 1},  # 第796行，第2列
            'formula': {
                'a': 0.0018,
                'b': 0.4411,
                'description': 'x = (y - 0.4411) / 0.0018'
            }
        },
        'vitamin_d': {
            'name': 'Vitamin D',
            'unit': 'ug/ml',
            'required_rows': 699,
            'intensity_1': {'row': 468, 'index': 467, 'column': 1},  # 第468行，第2列
            'intensity_2': {'row': 699, 'index': 698, 'column': 1},  # 第699行，第2列
            'formula': {
                'a': 0.0096,
                'b': 0.0792,
                'description': 'x = (y - 0.0792) / 0.0096'
            }
        },
        'carotene': {
            'name': 'Carotene',
            'unit': 'ng/ml',
            'required_rows': 796,
            'intensity_1': {'row': 468, 'index': 467, 'column': 1},  # 第468行，第2列
            'intensity_2': {'row': 796, 'index': 795, 'column': 1},  # 第796行，第2列
            'formula': {
                'a': 0.008,
                'b': 0.2946,
                'description': 'x = (y - 0.2946) / 0.008'
            }
        }
    }
    TREE_MODEL_CONFIGS = {
        "hu_r": {
            "name": "胡萝卜素和视黄醇混合",
            "model_path": os.path.join(ASSETS_ROOT, "tree/HU_R/tree_model.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "tree/HU_R/HU_R.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "tree/HU_R/new_data_hu_r.txt")
        },
        "hu_vd": {
            "name": "胡萝卜素和VD混合",
            "model_path": os.path.join(ASSETS_ROOT, "tree/HUVD/tree_model.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "tree/HUVD/hu_vd2.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "tree/HUVD/new_data_hu_vd.txt")
        },
        "hu_vd_vk": {
            "name": "胡萝卜素和VD、VK混合",
            "model_path": os.path.join(ASSETS_ROOT, "tree/HUVDVK/tree_model.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "tree/HUVDVK/HU_VD_VK.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "tree/HUVDVK/new_data_HU_VD_VK.txt")
        },
        "hu_vk": {
            "name": "胡萝卜素和VK混合",
            "model_path": os.path.join(ASSETS_ROOT, "tree/huvk/tree_model.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "tree/huvk/hu_vk.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "tree/huvk/new_data_hu_vk.txt")
        },
        "vk_r_vd": {
            "name": "视黄醇和VK、VD混合",
            "model_path": os.path.join(ASSETS_ROOT, "tree/VKRVD/tree_model.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "tree/VKRVD/VK_R_VD.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "tree/VKRVD/new_data_VK_R_VD.txt")
        }
    }
