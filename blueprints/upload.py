# coding=utf-8
# @Author  : Wodiao
# @Software: PyCharm
# @Time    : 2025/12/15 15:51
# @Project : nano_pj
# @File    : upload.py
from flask import Blueprint, request, Response, json
import os
import uuid
from config.settings import UPLOAD_ROOT, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
from services.predict_service import allowed_file, get_month_folder

upload_bp = Blueprint('upload', __name__)
upload_bp.max_content_length = MAX_CONTENT_LENGTH


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        current_month = get_month_folder()
        save_dir = os.path.join(UPLOAD_ROOT, current_month, 'file')
        os.makedirs(save_dir, exist_ok=True)

        uuid_filename = f"{uuid.uuid4()}.txt"
        save_path = os.path.join(save_dir, uuid_filename)

        filename = ''
        file_detail: str = request.form.get('fileDetail')  # uni.uploadFile 中 formData.userId
        if file_detail:
            with open(save_path, "w", encoding="utf-8") as fp:
                fp.write(file_detail)
        else:
            file = request.files['file']
            if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
                return Response(json.dumps({"status": "error", "message": "仅支持txt文件上传"}, ensure_ascii=False),
                                mimetype='application/json; charset=utf-8', status=400)
            filename = file.filename
            file.save(save_path)

        return Response(
            json.dumps({
                "status": "success",
                "message": "文件上传成功",
                "file_info": {
                    "original_filename": filename,
                    "uuid_filename": uuid_filename,
                    "save_dir": save_dir,
                    "save_path": save_path,
                    "month_folder": current_month
                }
            }, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8',
            status=200
        )

    except Exception as e:
        return Response(json.dumps({"status": "error", "message": f"文件上传失败：{str(e)}"}, ensure_ascii=False),
                        mimetype='application/json; charset=utf-8', status=500)
