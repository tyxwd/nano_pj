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
        },
        "brca": {
            "name": "BRCA_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/brca/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/brca/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/brca/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/brca/newdata.txt")
        },
        "brca_mix": {
            "name": "BRCA_MIX_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/brca_mix/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/brca_mix/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/brca_mix/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/brca_mix/newdata.txt")
        },
        "p": {
            "name": "P_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/p/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/p/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/p/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/p/newdata.txt")
        },
        "p_mix": {
            "name": "PMIX_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/p_mix/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/p_mix/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/p_mix/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/p_mix/newdata.txt")
        },
        "hpv": {
            "name": "HPV_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/hpv/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/hpv/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/hpv/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/hpv/newdata.txt")
        },
        "gzb": {
            "name": "GZB_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/gzb/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/gzb/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/gzb/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/gzb/newdata.txt")
        }
    }
    QUANTITATIVE_COMPOUND_CONFIGS = {
        'retinol': {
            'name': 'Retinol',
            'unit': 'ug/ml',
            'required_rows': 796,
            'intensity_1': {'row': 468, 'index': 467, 'column': 1},
            'intensity_2': {'row': 796, 'index': 795, 'column': 1},
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
            'intensity_1': {'row': 468, 'index': 467, 'column': 1},
            'intensity_2': {'row': 796, 'index': 795, 'column': 1},
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
            'intensity_1': {'row': 468, 'index': 467, 'column': 1},
            'intensity_2': {'row': 699, 'index': 698, 'column': 1},
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
            'intensity_1': {'row': 468, 'index': 467, 'column': 1},
            'intensity_2': {'row': 796, 'index': 795, 'column': 1},
            'formula': {
                'a': 0.008,
                'b': 0.2946,
                'description': 'x = (y - 0.2946) / 0.008'
            }
        },
        'brca1_mt': {
            'name': 'BRCA1_MT',
            'unit': 'nM',
            'required_rows': 817,
            'intensity_1': {'row': 135, 'index': 134, 'column': 1},
            'intensity_2': {'row': 712, 'index': 711, 'column': 1},
            'formula': {
                'a': 0.0053,
                'b': 1.1221,
                'description': 'x = (y - 1.1221) / 0.0053'
            }
        },
        'brca1_wt': {
            'name': 'BRCA1_WT',
            'unit': 'nM',
            'required_rows': 817,
            'intensity_1': {'row': 135, 'index': 134, 'column': 1},
            'intensity_2': {'row': 712, 'index': 711, 'column': 1},
            'formula': {
                'a': 0.0054,
                'b': 0.705,
                'description': 'x = (y - 0.705) / 0.0054'
            }
        },
        'p16': {
            'name': 'p16',
            'unit': 'nM',
            'required_rows': 817,
            'intensity_1': {'row': 135, 'index': 134, 'column': 1},
            'intensity_2': {'row': 712, 'index': 711, 'column': 1},
            'formula': {
                'a': 0.0031,
                'b': 1.345,
                'description': 'x = (y - 1.345) / 0.0031'
            }
        },
        'p21': {
            'name': 'p21',
            'unit': 'nM',
            'required_rows': 817,
            'intensity_1': {'row': 135, 'index': 134, 'column': 1},
            'intensity_2': {'row': 712, 'index': 711, 'column': 1},
            'formula': {
                'a': 0.0066,
                'b': -1.0112,  # b是负数，因为公式是 (y + 1.0112) / 0.0066
                'description': 'x = (y + 1.0112) / 0.0066'
            }
        },
        'p53': {
            'name': 'p53',
            'unit': 'nM',
            'required_rows': 817,
            'intensity_1': {'row': 135, 'index': 134, 'column': 1},
            'intensity_2': {'row': 712, 'index': 711, 'column': 1},
            'formula': {
                'a': 0.0076,
                'b': 0.8041,
                'description': 'x = (y - 0.8041) / 0.0076'
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
