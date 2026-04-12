# coding=utf-8
# @Author  : Wodiao
# @Software: PyCharm
# @Time    : 2025/12/15 15:55
# @Project : nano_pj
# @File    : predict.py
import os
from flask import Blueprint, request, Response, json
from config.model_config_repository import get_site_runtime_config, get_all_lang_configs
from services import predict_service
from config.settings import ModelConfig, UPLOAD_ROOT

predict_bp = Blueprint('predict', __name__)


@predict_bp.route('/predict', methods=['GET'])
def predict_api():
    result = predict_service.svm_predict('default')
    return Response(json.dumps(result, ensure_ascii=False, indent=2),
                    mimetype='application/json; charset=utf-8')


@predict_bp.route('/predict_custom', methods=['POST'])
def predict_custom_api():
    try:
        if not request.data:
            return Response(json.dumps({"status": "error", "message": "请求体不能为空！"}, ensure_ascii=False),
                            mimetype='application/json; charset=utf-8', status=400)

        try:
            request_json = json.loads(request.data)
        except Exception:
            return Response(json.dumps({"status": "error", "message": "请求体格式错误！"}, ensure_ascii=False),
                            mimetype='application/json; charset=utf-8', status=400)

        relative_path = request_json.get('file_path')
        type_ = request_json.get('type_', 'svm')  # svm, tree, quantitative
        model = request_json.get('model', 'default')
        if not relative_path:
            return Response(json.dumps({"status": "error", "message": "缺少 file_path 字段！"}, ensure_ascii=False),
                            mimetype='application/json; charset=utf-8', status=400)

        relative_path = relative_path.lstrip('/')
        custom_file_path = os.path.abspath(os.path.realpath(os.path.join(UPLOAD_ROOT, relative_path)))

        if not os.path.exists(custom_file_path):
            return Response(json.dumps({"status": "error", "message": "文件不存在！"}, ensure_ascii=False),
                            mimetype='application/json; charset=utf-8', status=404)
        if not custom_file_path.endswith('.txt'):
            return Response(json.dumps({"status": "error", "message": "文件必须是txt格式！"}, ensure_ascii=False),
                            mimetype='application/json; charset=utf-8', status=400)
        if type_ == 'svm':
            result = predict_service.svm_predict(model, custom_file_path)
        elif type_ == 'quantitative':
            result = predict_service.quantitative_predict(model, custom_file_path)
        else:  # tree
            result = predict_service.tree_predict(model, custom_file_path)
        return Response(json.dumps(result, ensure_ascii=False, indent=2),
                        mimetype='application/json; charset=utf-8')

    except Exception as e:
        return Response(json.dumps({"status": "error", "message": f"预测接口异常：{str(e)}"}, ensure_ascii=False),
                        mimetype='application/json; charset=utf-8', status=500)


@predict_bp.route('/init_lang_config', methods=['GET'])
def init_lang_config_api():
    """
    返回模型的中英文名称配置
    """
    try:
        data = get_all_lang_configs(ModelConfig.DB_PATH)
        return Response(
            json.dumps({"status": "ok", "data": data}, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8',
        )
    except Exception as e:
        return Response(
            json.dumps({"status": "error", "message": f"获取语言配置异常：{str(e)}"}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8',
            status=500,
        )

@predict_bp.route('/site_runtime_config', methods=['GET', 'POST'])
def site_runtime_config_api():
    try:
        site = ''
        if request.method == 'GET':
            site = (request.args.get('site') or '').strip()
        else:
            if request.data:
                try:
                    body = json.loads(request.data)
                except Exception:
                    body = {}
            else:
                body = {}
            site = str(body.get('site', '')).strip()

        if not site:
            return Response(
                json.dumps({"status": "error", "message": "缺少 site 参数"}, ensure_ascii=False),
                mimetype='application/json; charset=utf-8',
                status=400,
            )

        runtime = get_site_runtime_config(ModelConfig.DB_PATH, site)
        if not runtime:
            return Response(
                json.dumps({"status": "error", "message": f"站点不存在: {site}"}, ensure_ascii=False),
                mimetype='application/json; charset=utf-8',
                status=404,
            )

        return Response(
            json.dumps({"status": "ok", "data": runtime}, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8',
        )

    except Exception as e:
        return Response(
            json.dumps({"status": "error", "message": f"获取配置异常：{str(e)}"}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8',
            status=500,
        )


@predict_bp.route('/available_models', methods=['GET', 'POST'])
def available_models_api():
    """
    提供给前端Vue界面的接口，根据上传的站点名称，返回可以选择的模型信息及计算方法类型。
    """
    try:
        site = ''
        if request.method == 'GET':
            site = (request.args.get('site') or '').strip()
        else:
            if request.data:
                try:
                    body = json.loads(request.data)
                    site = str(body.get('site', '')).strip()
                except Exception:
                    pass

        if not site:
            return Response(
                json.dumps({"status": "error", "message": "缺少 site 参数"}, ensure_ascii=False),
                mimetype='application/json; charset=utf-8',
                status=400,
            )

        runtime = get_site_runtime_config(ModelConfig.DB_PATH, site)
        if not runtime:
            return Response(
                json.dumps({"status": "error", "message": f"站点不存在: {site}"}, ensure_ascii=False),
                mimetype='application/json; charset=utf-8',
                status=404,
            )

        # 按照前端的配置结构构造返回数据格式
        svm_model_configs = {item['key']: {'name': item['name']} for item in runtime['models'].get('svm', [])}
        quantitative_configs = {item['key']: {'name': item['name']} for item in runtime['models'].get('quantitative', [])}
        tree_configs = {item['key']: {'name': item['name']} for item in runtime['models'].get('tree', [])}
        calculation_types = runtime.get('calculation_types', [])

        data = {
            "svm_model_configs": svm_model_configs,
            "quantitative_compound_configs": quantitative_configs,
            "tree_model_configs": tree_configs,
            "calculation_types": calculation_types
        }

        return Response(
            json.dumps({"status": "ok", "data": data}, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8',
        )
    except Exception as e:
        return Response(
            json.dumps({"status": "error", "message": f"接口异常：{str(e)}"}, ensure_ascii=False),
            mimetype='application/json; charset=utf-8',
            status=500,
        )
