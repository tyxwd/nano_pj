# coding=utf-8
# @Author  : Wodiao
# @Software: PyCharm
# @Time    : 2025/12/15 15:47
# @Project : nano_pj
# @File    : settings.py
from ast import main
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
        },
        "han": {
            "name": "HAN_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/han/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/han/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/han/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/han/newdata.txt")
        },
        "lei": {
            "name": "LEI_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/lei/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/lei/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/lei/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/lei/newdata.txt")
        },
        "niao": {
            "name": "NIAO_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/niao/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/niao/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/niao/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/niao/newdata.txt")
        },
        "shui": {
            "name": "SHUI_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/shui/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/shui/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/shui/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/shui/newdata.txt")
        },
        "xueqing": {
            "name": "XUEQING_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/xueqing/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/xueqing/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/xueqing/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/xueqing/newdata.txt")
        },
        "pesticide": {
            "name": "PESTICIDE_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/pesticide/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/pesticide/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/pesticide/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/pesticide/newdata.txt")
        },
        "osteoporosis": {
            "name": "Osteoporosis_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/osteoporosis/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/osteoporosis/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/osteoporosis/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/osteoporosis/newdata.txt")
        },
        "quino":{
            "name": "Quino_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/quino/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/quino/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/quino/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/quino/newdata.txt")
        },
        "ciplvfx":{
            "name": "CIPLVFX_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/ciplvfx/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/ciplvfx/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/ciplvfx/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/ciplvfx/newdata.txt")
        },
        "cippef":{
            "name": "CIPPEF_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/cippef/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/cippef/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/cippef/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/cippef/newdata.txt")
        },
        "cippeflvfx":{
            "name": "CIPPEFLVFX_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/cippeflvfx/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/cippeflvfx/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/cippeflvfx/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/cippeflvfx/newdata.txt")
        },
        "peflvfx":{
            "name": "PEFLVFX_SVM",
            "model_path": os.path.join(ASSETS_ROOT, "svm/peflvfx/svm_model_tuned.pkl"),
            "scaler_path": os.path.join(ASSETS_ROOT, "svm/peflvfx/scaler.pkl"),
            "training_csv": os.path.join(ASSETS_ROOT, "svm/peflvfx/training.csv"),
            "default_txt": os.path.join(ASSETS_ROOT, "svm/peflvfx/newdata.txt")
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
        },
        'crp': {
            'name': 'C-Reactive Protein',
            'unit': 'μg/ml',
            'required_rows': 1209,
            'intensity_1': {'row': 343, 'index': 342, 'column': 1},
            'intensity_2': {'row': 1177, 'index': 1176, 'column': 1},
            'formula': {
                'a': 0.035,
                'b': 0.0162,
                'description': 'x = (y - 0.0162) / 0.035'
            }
        },
        'il': {
            'name': 'Interleukin',
            'unit': 'ng/ml',
            'required_rows': 1280,
            'intensity_1': {'row': 346, 'index': 345, 'column': 1},
            'intensity_2': {'row': 1177, 'index': 1176, 'column': 1},
            'formula': {
                'a': 0.0025,
                'b': 0.1159,
                'description': 'x = (y - 0.1159) / 0.0025'
            }
        },
        'ua': {
            'name': 'Uric Acid',
            'unit': 'μg/ml',
            'required_rows': 1280,
            'intensity_1': {'row': 639, 'index': 638, 'column': 1},
            'intensity_2': {'row': 1177, 'index': 1176, 'column': 1},
            'formula': {
                'a': 0.099,
                'b': 3.7192,
                'description': 'x = (y - 3.7192) / 0.099'
            }
        },

        'sjl': {
            'name': 'Thiabendazole',
            'unit': 'ng/ml',
            'required_rows': 850,
            'intensity_1': {'row': 215, 'index': 214, 'column': 1},
            'intensity_2': {'row': 298, 'index': 297, 'column': 1},
            'formula': {
                'a': 0.528,
                'b': 0.227,
                'description': 'x = (y - 0.227) / 0.528'
            },
            'transform': '10^x'
        },
        'fms': {
            'name': 'Thiram',
            'unit': 'ng/ml',
            'required_rows': 850,
            'intensity_1': {'row': 579, 'index': 578, 'column': 1},
            'intensity_2': {'row': 298, 'index': 297, 'column': 1},
            'formula': {
                'a': 1.058,
                'b': -1.295,
                'description': 'x = (y - (-1.295)) / 1.058'  # 或 'x = (y + 1.295) / 1.058'
            },
            'transform': '10^x'
        },
        
        'cip': {
            'name': 'CIP',
            'unit': 'ug/ml',
            'required_rows': 850,
            'intensity_1': {'row': 579, 'index': 578, 'column': 1},
            'intensity_2': {'row': 301, 'index': 300, 'column': 1},
            'formula': {
                # "slope": 0.9835,
                # "intercept": 0.6464,
                'a': 0.9835,
                'b': 0.6464,
                'description': 'x = (y - 0.6464) / 0.9835'
            }
        },
        'norf': {
            'name': 'NORF',
            'unit': 'ug/ml',
            'required_rows': 850,
            'intensity_1': {'row': 402, 'index': 401, 'column': 1},
            'intensity_2': {'row': 798, 'index': 797, 'column': 1},
            'formula': {
                'a': 0.991,
                'b': 1.8743,
                'description': 'x = (y - 1.8743) / 0.991'
            }
        },
        'pef': {
            'name': 'PEF',
            'unit': 'ug/ml',
            'required_rows': 850,
            'intensity_1': {'row': 404, 'index': 403, 'column': 1},
            'intensity_2': {'row': 795, 'index': 794, 'column': 1},
            'formula': {
                'a': 0.0451,
                'b': 0.7205,
                'description': 'x = (y - 0.7205) / 0.0451'
            }
        },
        'cip_rengonghu':{
            'name': 'CIP', # (Artificial Lake)
            'unit': 'umol/ml',
            'required_rows': 850,
            'intensity_1': {'row': 588, 'index': 587, 'column': 1},
            'intensity_2': {'row': 1122, 'index': 1121, 'column': 1},
            'formula': {
                'a': 0.9934,
                'b': 10.509,
                'description': 'x = (y - 10.509) / 0.9934'
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
