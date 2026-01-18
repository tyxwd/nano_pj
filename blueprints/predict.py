# coding=utf-8
# @Author  : Wodiao
# @Software: PyCharm
# @Time    : 2025/12/15 15:55
# @Project : nano_pj
# @File    : predict.py
import os
from flask import Blueprint, request, Response, json
from services import predict_service
from config.settings import UPLOAD_ROOT

predict_bp = Blueprint('predict', __name__)


@predict_bp.route('/predict', methods=['GET'])
def predict_api():
    result = predict_service.svm_predict()
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
        except json.JSONDecodeError:
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
