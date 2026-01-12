# coding=utf-8
# @Author  : Wodiao
# @Software: PyCharm
# @Time    : 2025/12/15 15:49
# @Project : nano_pj
# @File    : predictor.py
import os
import random
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from config.settings import ModelConfig
import warnings

warnings.filterwarnings('ignore')

# 加载模型和特征信息
try:
    svm_model = joblib.load(ModelConfig.SVM_MODEL_CONFIGS["default"]["model_path"])
    svm_scaler = joblib.load(ModelConfig.SVM_MODEL_CONFIGS["default"]["scaler_path"])
    svm_train_data = pd.read_csv(ModelConfig.SVM_MODEL_CONFIGS["default"]["training_csv"])
    svm_feature_names = svm_train_data.columns[:-1].tolist()
    svm_n_features = len(svm_feature_names)
    print("模型和特征信息加载成功")
except Exception as e:
    print(f"加载模型失败: {e}")
    raise


def allowed_file(filename, allowed_ext=None):
    allowed_ext = allowed_ext or {'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


def get_month_folder():
    from datetime import datetime
    return datetime.now().strftime("%Y%m")


def svm_predict(custom_file_path=None):
    result_dict = {}
    try:
        default_txt = ModelConfig.SVM_MODEL_CONFIGS["default"]["default_txt"]
        target_file = custom_file_path if custom_file_path else default_txt

        # 安全检查
        if custom_file_path:
            normalized_path = os.path.abspath(os.path.realpath(custom_file_path))
            if not os.path.exists(normalized_path):
                return {"status": "error", "message": f"自定义文件不存在 → {custom_file_path}"}
            if not normalized_path.endswith('.txt'):
                return {"status": "error", "message": "自定义文件必须是txt格式"}

        # 读取文件
        with open(target_file, 'r') as f:
            lines = f.readlines()

        second_column = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    second_column.append(float(parts[1]))
                except ValueError:
                    print(f"警告：跳过无效值 '{parts[1]}'")

        if not second_column:
            return {"status": "error", "message": f"文件 {os.path.basename(target_file)} 中未提取到有效数据"}

        # 归一化
        second_column = MinMaxScaler().fit_transform(np.array(second_column).reshape(-1, 1)).flatten()
        data_length = len(second_column)

        # 调整长度
        if data_length > svm_n_features:
            indices = np.linspace(0, data_length - 1, svm_n_features, dtype=int)
            processed_data = [second_column[i] for i in indices]
        elif data_length < svm_n_features:
            processed_data = second_column.tolist()
            while len(processed_data) < svm_n_features:
                pos = random.randint(1, len(processed_data) - 1) if len(processed_data) > 1 else 0
                new_val = (processed_data[pos - 1] + processed_data[pos]) / 2 if len(processed_data) > 1 else processed_data[0]
                processed_data.insert(pos, new_val)
        else:
            processed_data = second_column.tolist()

        # 预测
        input_data = pd.DataFrame([processed_data], columns=svm_feature_names)
        input_scaled = svm_scaler.transform(input_data)

        prediction = svm_model.predict(input_scaled)[0]
        predicted_type = str(prediction) if not isinstance(prediction, str) else prediction

        # 置信度计算
        confidence = 0.0
        probabilities = {}

        if hasattr(svm_model, 'predict_proba'):
            probs = svm_model.predict_proba(input_scaled)[0]
            for cls, prob in zip(svm_model.classes_, probs):
                probabilities[f'prob_{str(cls)}'] = round(float(prob), 8)
            confidence = probabilities[f'prob_{predicted_type}']
        else:
            dec_vals = svm_model.decision_function(input_scaled)[0]
            if len(dec_vals) > 1:
                confidence = float(abs(dec_vals).max() / abs(dec_vals).sum())
            else:
                confidence = float(1.0 / (1 + np.exp(-abs(dec_vals[0]))))
            confidence = round(confidence, 8)

        result_dict["status"] = "success"
        result_dict["file_info"] = {
            # "used_file": target_file,
            "used_file": "",
            "file_type": "custom" if custom_file_path else "default"
        }
        result_dict["result"] = {
            "predicted_type": predicted_type,
            "confidence": confidence,
            "original_length": data_length,
            "processed_length": svm_n_features
        }
        if probabilities:
            result_dict["probabilities"] = probabilities

        return result_dict

    except Exception as e:
        return {"status": "error", "message": f"处理或预测过程中出错: {str(e)}"}


def quantitative_predict(compound_type, file_path):
    """
    通用定量分析函数 - 类似process_and_predict风格
    只返回JSON结果，不保存CSV
    """
    result_dict = {}

    # 化合物配置参数（修正后的索引）
    compound_configs = ModelConfig.QUANTITATIVE_COMPOUND_CONFIGS

    try:
        # 检查化合物类型
        if compound_type not in compound_configs:
            return {"status": "error", "message": f"不支持的化合物类型: {compound_type}"}

        config = compound_configs[compound_type]

        with open(file_path, 'r') as f:
            lines = f.readlines()

        # 检查数据行数
        num_rows = len(lines)
        required_rows = config['required_rows']
        if num_rows < required_rows:
            return {"status": "error",
                    "message": f"{config['name']}需要至少{required_rows}行数据，当前文件只有{num_rows}行"}

        # 解析数据到二维数组
        data_rows = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    # 尝试转换为浮点数
                    row_data = [float(parts[0]) if parts[0].replace('.', '', 1).replace('-', '', 1).isdigit() else parts[0],
                                float(parts[1])]
                    data_rows.append(row_data)
                except ValueError:
                    # 跳过无法转换的行
                    continue

        if len(data_rows) < required_rows:
            return {"status": "error",
                    "message": f"有效数据行数不足{required_rows}行，只有{len(data_rows)}行有效数据"}

        # 获取指定行数据
        try:
            intensity_config_1 = config['intensity_1']
            intensity_config_2 = config['intensity_2']

            # 注意：我们的data_rows列表现在只包含有效的行，需要重新索引
            # 为了简化，我们假设文件行号与索引一致
            intensity_1 = float(lines[intensity_config_1['index']].strip().split()[1])
            intensity_2 = float(lines[intensity_config_2['index']].strip().split()[1])

        except (IndexError, ValueError) as e:
            # 如果行索引或转换失败，尝试使用解析后的data_rows
            try:
                # 使用原始代码的数据读取方式作为备选
                import pandas as pd
                try:
                    data = pd.read_csv(file_path, sep='\s+', header=None)
                except:
                    data = pd.read_csv(file_path, header=None)

                intensity_1 = data.iloc[intensity_config_1['index'], intensity_config_1['column']]
                intensity_2 = data.iloc[intensity_config_2['index'], intensity_config_2['column']]

            except Exception as pd_error:
                return {"status": "error",
                        "message": f"无法获取第{intensity_config_1['row']}行或第{intensity_config_2['row']}行的数据"}

        # 计算y值（强度比）
        if intensity_2 == 0:
            return {"status": "error", "message": "分母为0，无法计算"}

        y = intensity_1 / intensity_2

        # 根据公式计算浓度
        formula = config['formula']
        a = formula['a']
        b = formula['b']
        x = (y - b) / a

        # 构建结果字典 - 模仿process_and_predict的结构
        result_dict["status"] = "success"
        result_dict["file_info"] = {
            # "used_file": file_path,
            "used_file": "",
            "file_type": "custom",
            "total_rows": num_rows,
            "compound_type": compound_type
        }

        result_dict["calculation_data"] = {
            "intensity_1": {
                "row_number": intensity_config_1['row'],
                "value": float(intensity_1)
            },
            "intensity_2": {
                "row_number": intensity_config_2['row'],
                "value": float(intensity_2)
            },
            "ratio_y": float(y),
            "formula_parameters": {
                "a": float(a),
                "b": float(b),
                "formula": formula['description']
            }
        }

        result_dict["result"] = {
            "compound_name": config['name'],
            "concentration": float(x),
            "unit": config['unit'],
            "calculation_details": f"x = ({y:.6f} - {b}) / {a} = {x:.6f}"
        }

        # 添加质量控制信息
        result_dict["quality_info"] = {
            "data_validation": "passed",
            "rows_checked": num_rows,
            "minimum_required": required_rows,
            "intensity_ratio": float(y)
        }

        return result_dict

    except Exception as e:
        return {"status": "error", "message": f"定量分析过程中出错: {str(e)}"}


def tree_predict(model_name: str, txt_file: str = None) -> dict:
    """
    通用决策树预测函数
    :param model_name: 模型配置名称，对应 TREE_MODEL_CONFIGS 的 key
    :param txt_file: 可选，指定输入 txt 文件路径；如果不传，则使用配置默认路径
    :return: dict，包含预测结果、置信度、原始长度、概率信息
    """
    result_dict = {}
    try:
        if model_name not in ModelConfig.TREE_MODEL_CONFIGS:
            return {"status": "error", "message": f"未知模型名称: {model_name}"}

        config = ModelConfig.TREE_MODEL_CONFIGS[model_name]
        txt_file = txt_file or config['default_txt']
        model_path = config['model_path']
        training_csv = config['training_csv']

        # 安全检查
        normalized_path = os.path.abspath(os.path.realpath(txt_file))
        if not os.path.exists(normalized_path):
            return {"status": "error", "message": f"文件不存在 → {txt_file}"}
        if not normalized_path.endswith('.txt'):
            return {"status": "error", "message": "文件必须是txt格式"}

        # 读取txt文件
        with open(txt_file, 'r') as f:
            lines = f.readlines()
        second_column = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    second_column.append(float(parts[1]))
                except ValueError:
                    continue
        if not second_column:
            return {"status": "error", "message": f"文件 {os.path.basename(txt_file)} 中未提取到有效数据"}

        # 加载模型和训练特征
        model = joblib.load(model_path)
        train_data = pd.read_csv(training_csv)
        feature_names = train_data.columns[1:-1].tolist()

        # 调整长度
        data_length = len(second_column)
        if data_length > len(feature_names):
            indices = np.linspace(0, data_length - 1, len(feature_names), dtype=int)
            processed_data = [second_column[i] for i in indices]
        elif data_length < len(feature_names):
            processed_data = second_column[:]
            while len(processed_data) < len(feature_names):
                pos = random.randint(1, len(processed_data) - 1) if len(processed_data) > 1 else 0
                new_val = (processed_data[pos - 1] + processed_data[pos]) / 2 if len(processed_data) > 1 else processed_data[0]
                processed_data.insert(pos, new_val)
        else:
            processed_data = second_column[:]

        # 准备输入
        input_data = pd.DataFrame([processed_data], columns=feature_names)

        # 预测
        prediction = model.predict(input_data)[0]
        probabilities = {}

        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(input_data)[0]
            probabilities = {f'prob_{str(cls)}': round(float(p), 8) for cls, p in zip(model.classes_, probs)}
            confidence = probabilities[f'prob_{str(prediction)}']
        else:
            confidence = 0.0

        result_dict["status"] = "success"
        result_dict["file_info"] = {
            # "used_file": txt_file,
            "used_file": "",
            "file_type": "custom" if txt_file != config['default_txt'] else "default"
        }
        result_dict["result"] = {
            "predicted_type": str(prediction),
            "confidence": round(float(confidence), 8),
            "original_length": data_length,
            "processed_length": len(feature_names)
        }
        if probabilities:
            result_dict["probabilities"] = probabilities

        return result_dict

    except Exception as e:
        return {"status": "error", "message": f"处理或预测过程中出错: {str(e)}"}


if __name__ == '__main__':
    res = tree_predict(
        "hu_r"
    )
    print(res)
