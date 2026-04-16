# coding=utf-8
import os
import re
import shutil
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from config.model_config_repository import (
    create_site_profile,
    create_quantitative_compound,
    create_svm_model,
    create_tree_model,
    delete_site_profile,
    delete_quantitative_compound,
    delete_svm_model,
    delete_tree_model,
    get_site_profile,
    get_site_scope,
    get_quantitative_compound,
    get_probability_labels,
    get_quantitative_model_usage_in_sites,
    get_svm_model,
    get_svm_model_usage_in_sites,
    get_tree_model,
    get_tree_model_usage_in_sites,
    list_site_profiles,
    list_quantitative_compounds,
    list_probability_labels,
    list_svm_models,
    list_tree_models,
    quantitative_compound_exists,
    save_site_scope,
    set_svm_model_active,
    site_profile_exists,
    svm_model_exists,
    upsert_probability_labels,
)
from config.settings import ASSETS_ROOT, ModelConfig
from services import predict_service

model_admin_bp = Blueprint("model_admin", __name__)

SVM_MODEL_KEY_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
COMPOUND_KEY_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
ALLOWED_TRANSFORM_TYPES = {"10^x"}
ALLOWED_METHOD_TYPES = {"svm", "tree", "quantitative"}


def _normalize_model_key(raw_value: str) -> str:
    return raw_value.strip().lower()


def _normalize_site_key(raw_value: str) -> str:
    return str(raw_value or "").strip()


def _to_int(raw_value, field_name: str) -> int:
    try:
        return int(str(raw_value).strip())
    except Exception as exc:
        raise ValueError(f"字段 {field_name} 必须是整数") from exc


def _to_float(raw_value, field_name: str) -> float:
    try:
        return float(str(raw_value).strip())
    except Exception as exc:
        raise ValueError(f"字段 {field_name} 必须是数字") from exc


def _save_uploaded_file(file_storage, expected_ext: str, target_path: str):
    if file_storage is None or not file_storage.filename:
        raise ValueError(f"缺少文件: {os.path.basename(target_path)}")

    _, ext = os.path.splitext(file_storage.filename)
    if ext.lower() != expected_ext.lower():
        raise ValueError(
            f"文件 {file_storage.filename} 类型错误，应为 {expected_ext}"
        )

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    file_storage.save(target_path)


def _remove_assets_dirs_by_rel_paths(rel_paths):
    assets_root_abs = os.path.abspath(ASSETS_ROOT)
    candidate_dirs = set()
    for rel_path in rel_paths:
        if not rel_path:
            continue
        rel_path_os = rel_path.replace("/", os.sep)
        model_file_abs = os.path.abspath(os.path.join(ASSETS_ROOT, rel_path_os))
        model_dir_abs = os.path.dirname(model_file_abs)
        if not model_dir_abs.startswith(assets_root_abs + os.sep):
            raise ValueError("待删除目录不在 assets 目录内")
        candidate_dirs.add(model_dir_abs)

    for model_dir_abs in sorted(candidate_dirs):
        if os.path.isdir(model_dir_abs):
            shutil.rmtree(model_dir_abs)


def _canonical_probability_label_key(raw_key: str) -> str:
    key = str(raw_key or "").strip()
    if key.startswith("prob_"):
        return key[5:]
    return key


def _render_svm_admin_page(
    svm_message: str = "",
    svm_error: str = "",
    pending_model_key: str = "",
    pending_prob_labels=None,
    activation_mode: bool = False,
    all_prob_labels=None,
    existing_prob_label_map=None,
):
    svm_models = list_svm_models(ModelConfig.DB_PATH)
    return render_template(
        "model_admin_svm.html",
        svm_models=svm_models,
        svm_message=svm_message,
        svm_error=svm_error,
        pending_model_key=pending_model_key,
        pending_prob_labels=(pending_prob_labels or []),
        activation_mode=activation_mode,
        all_prob_labels=all_prob_labels or [],
        existing_prob_label_map=existing_prob_label_map or {},
        now=datetime.now(),
        active_menu="svm",
    )


def _build_svm_config_from_db_record(model):
    return {
        "name": model["name_zh"] or model["name_en"] or model["model_key"],
        "model_path": os.path.join(ASSETS_ROOT, model["model_rel_path"].replace("/", os.sep)),
        "scaler_path": os.path.join(ASSETS_ROOT, model["scaler_rel_path"].replace("/", os.sep)),
        "training_csv": os.path.join(ASSETS_ROOT, model["training_rel_path"].replace("/", os.sep)),
        "default_txt": os.path.join(ASSETS_ROOT, model["default_txt_rel_path"].replace("/", os.sep)),
    }


def _probe_svm_probabilities(model_key: str):
    """Call svm_predict for admin activation check, including inactive models via temporary runtime config."""
    if model_key in ModelConfig.SVM_MODEL_CONFIGS:
        return predict_service.svm_predict(model_key)

    model = get_svm_model(ModelConfig.DB_PATH, model_key)
    if not model:
        return {"status": "error", "message": f"模型不存在: {model_key}"}

    temp_cfg = _build_svm_config_from_db_record(model)
    return predict_service.svm_predict(model_key, model_config_override=temp_cfg)


@model_admin_bp.route("/admin/models/svm", methods=["GET"])
def svm_model_admin_page():
    pending_model_key = _normalize_model_key(request.args.get("pending_model_key", ""))
    pending_prob_labels_raw = request.args.get("pending_prob_labels", "")
    pending_prob_labels = []
    if pending_prob_labels_raw:
        pending_prob_labels = [
            _canonical_probability_label_key(x)
            for x in pending_prob_labels_raw.split(",")
            if _canonical_probability_label_key(x)
        ]

    activation_mode = request.args.get("activation_mode", "").strip() == "1"

    return _render_svm_admin_page(
        svm_message=request.args.get("svm_message", ""),
        svm_error=request.args.get("svm_error", ""),
        pending_model_key=pending_model_key,
        pending_prob_labels=pending_prob_labels,
        activation_mode=activation_mode,
    )


@model_admin_bp.route("/admin/models/quantitative", methods=["GET"])
def quantitative_model_admin_page():
    quantitative_models = list_quantitative_compounds(ModelConfig.DB_PATH)
    return render_template(
        "model_admin_quantitative.html",
        quantitative_models=quantitative_models,
        q_message=request.args.get("q_message", ""),
        q_error=request.args.get("q_error", ""),
        now=datetime.now(),
        active_menu="quantitative",
    )


@model_admin_bp.route("/admin/models/probability-labels", methods=["GET"])
def probability_label_admin_page():
    return render_template(
        "model_admin_probability_labels.html",
        probability_labels=list_probability_labels(ModelConfig.DB_PATH),
        prob_message=request.args.get("prob_message", ""),
        prob_error=request.args.get("prob_error", ""),
        now=datetime.now(),
        active_menu="probability_labels",
    )


@model_admin_bp.route("/admin/models/probability-labels/edit/<label_key>", methods=["GET"])
def edit_probability_label_page(label_key):
    label_key = str(label_key or "").strip()
    if not label_key:
        return redirect(url_for("model_admin.probability_label_admin_page", prob_error="标签键不能为空"))

    label_map = get_probability_labels(ModelConfig.DB_PATH, [label_key])
    label = label_map.get(label_key)
    if not label:
        return redirect(url_for("model_admin.probability_label_admin_page", prob_error=f"标签不存在: {label_key}"))

    return render_template(
        "model_admin_probability_labels.html",
        label_key=label_key,
        label=label,
        prob_message=request.args.get("prob_message", ""),
        prob_error=request.args.get("prob_error", ""),
        now=datetime.now(),
        active_menu="probability_labels",
    )


@model_admin_bp.route("/admin/models/tree", methods=["GET"])
def tree_model_admin_page():
    tree_models = list_tree_models(ModelConfig.DB_PATH)
    return render_template(
        "model_admin_tree.html",
        tree_models=tree_models,
        tree_message=request.args.get("tree_message", ""),
        tree_error=request.args.get("tree_error", ""),
        now=datetime.now(),
        active_menu="tree",
    )


@model_admin_bp.route("/admin/sites", methods=["GET"])
def site_admin_page():
    sites = list_site_profiles(ModelConfig.DB_PATH)
    selected_site_key = _normalize_site_key(request.args.get("site_key", ""))
    selected_site = get_site_profile(ModelConfig.DB_PATH, selected_site_key) if selected_site_key else None
    selected_scope = get_site_scope(ModelConfig.DB_PATH, selected_site_key) if selected_site else {
        "methods": [],
        "svm": [],
        "tree": [],
        "quantitative": [],
    }

    return render_template(
        "model_admin_sites.html",
        sites=sites,
        selected_site=selected_site,
        selected_scope=selected_scope,
        svm_models=list_svm_models(ModelConfig.DB_PATH),
        tree_models=list_tree_models(ModelConfig.DB_PATH),
        quantitative_models=list_quantitative_compounds(ModelConfig.DB_PATH),
        site_message=request.args.get("site_message", ""),
        site_error=request.args.get("site_error", ""),
        now=datetime.now(),
        active_menu="sites",
    )


@model_admin_bp.route("/admin/models", methods=["GET"])
def model_admin_home():
    return redirect(url_for("model_admin.svm_model_admin_page"))


@model_admin_bp.route("/admin/sites", methods=["POST"])
def create_site_profile_action():
    site_key = _normalize_site_key(request.form.get("site_key", ""))
    display_name = _normalize_site_key(request.form.get("display_name", "")) or site_key

    if not site_key:
        return redirect(url_for("model_admin.site_admin_page", site_error="站点名不能为空"))

    if site_profile_exists(ModelConfig.DB_PATH, site_key):
        return redirect(url_for("model_admin.site_admin_page", site_error=f"站点已存在: {site_key}"))

    try:
        create_site_profile(ModelConfig.DB_PATH, site_key, display_name)
        return redirect(
            url_for(
                "model_admin.site_admin_page",
                site_key=site_key,
                site_message=f"站点创建成功: {site_key}",
            )
        )
    except Exception as exc:
        return redirect(url_for("model_admin.site_admin_page", site_error=f"创建站点失败: {str(exc)}"))


@model_admin_bp.route("/admin/sites/config", methods=["POST"])
def save_site_scope_action():
    site_key = _normalize_site_key(request.form.get("site_key", ""))
    site = get_site_profile(ModelConfig.DB_PATH, site_key)
    if not site:
        return redirect(url_for("model_admin.site_admin_page", site_error=f"站点不存在: {site_key}"))

    if site.get("is_builtin") == 1:
        return redirect(
            url_for(
                "model_admin.site_admin_page",
                site_key=site_key,
                site_error=f"默认初始站点不允许修改: {site_key}",
            )
        )

    svm_keys = [_normalize_model_key(k) for k in request.form.getlist("svm_keys") if k]
    tree_keys = [_normalize_model_key(k) for k in request.form.getlist("tree_keys") if k]
    quantitative_keys = [_normalize_model_key(k) for k in request.form.getlist("quantitative_keys") if k]

    # 获取所有模型的详细信息
    all_svm_models = list_svm_models(ModelConfig.DB_PATH)
    all_tree_models = list_tree_models(ModelConfig.DB_PATH)
    all_quantitative_models = list_quantitative_compounds(ModelConfig.DB_PATH)

    # 验证SVM模型
    svm_model_dict = {item["model_key"]: item for item in all_svm_models}
    invalid_svm = [k for k in svm_keys if k not in svm_model_dict]
    if invalid_svm:
        return redirect(url_for("model_admin.site_admin_page", site_key=site_key, site_error=f"存在无效 SVM 模型编码: {', '.join(invalid_svm)}"))
    
    inactive_svm = [k for k in svm_keys if svm_model_dict[k].get("is_active") != 1]
    if inactive_svm:
        return redirect(url_for("model_admin.site_admin_page", site_key=site_key, site_error=f"以下 SVM 模型未激活，无法选择: {', '.join(inactive_svm)}"))

    # 验证TREE模型
    tree_model_dict = {item["model_key"]: item for item in all_tree_models}
    invalid_tree = [k for k in tree_keys if k not in tree_model_dict]
    if invalid_tree:
        return redirect(url_for("model_admin.site_admin_page", site_key=site_key, site_error=f"存在无效 TREE 模型编码: {', '.join(invalid_tree)}"))
    
    inactive_tree = [k for k in tree_keys if tree_model_dict[k].get("is_active") != 1]
    if inactive_tree:
        return redirect(url_for("model_admin.site_admin_page", site_key=site_key, site_error=f"以下 TREE 模型未激活，无法选择: {', '.join(inactive_tree)}"))

    # 验证定量模型
    quantitative_model_dict = {item["compound_key"]: item for item in all_quantitative_models}
    invalid_quantitative = [k for k in quantitative_keys if k not in quantitative_model_dict]
    if invalid_quantitative:
        return redirect(url_for("model_admin.site_admin_page", site_key=site_key, site_error=f"存在无效定量模型编码: {', '.join(invalid_quantitative)}"))
    
    inactive_quantitative = [k for k in quantitative_keys if quantitative_model_dict[k].get("is_active") != 1]
    if inactive_quantitative:
        return redirect(url_for("model_admin.site_admin_page", site_key=site_key, site_error=f"以下定量模型未激活，无法选择: {', '.join(inactive_quantitative)}"))

    selected_method_count = sum(
        [
            1 if svm_keys else 0,
            1 if tree_keys else 0,
            1 if quantitative_keys else 0,
        ]
    )

    if selected_method_count <= 0:
        return redirect(
            url_for(
                "model_admin.site_admin_page",
                site_key=site_key,
                site_error="请至少选择一个模型",
            )
        )

    try:
        save_site_scope(
            ModelConfig.DB_PATH,
            site_key,
            svm_keys,
            tree_keys,
            quantitative_keys,
        )
        return redirect(
            url_for(
                "model_admin.site_admin_page",
                site_key=site_key,
                site_message=f"站点配置保存成功: {site_key}",
            )
        )
    except Exception as exc:
        return redirect(
            url_for(
                "model_admin.site_admin_page",
                site_key=site_key,
                site_error=f"保存站点配置失败: {str(exc)}",
            )
        )


@model_admin_bp.route("/admin/sites/delete", methods=["POST"])
def delete_site_profile_action():
    site_key = _normalize_site_key(request.form.get("site_key", ""))
    site = get_site_profile(ModelConfig.DB_PATH, site_key)
    if not site:
        return redirect(url_for("model_admin.site_admin_page", site_error=f"站点不存在: {site_key}"))

    if site.get("is_builtin") == 1:
        return redirect(url_for("model_admin.site_admin_page", site_error=f"默认初始站点不允许删除: {site_key}"))

    try:
        rows = delete_site_profile(ModelConfig.DB_PATH, site_key)
        if rows <= 0:
            return redirect(url_for("model_admin.site_admin_page", site_error=f"删除失败: 站点不存在 {site_key}"))
        return redirect(url_for("model_admin.site_admin_page", site_message=f"站点已删除: {site_key}"))
    except Exception as exc:
        return redirect(url_for("model_admin.site_admin_page", site_error=f"删除站点失败: {str(exc)}"))


@model_admin_bp.route("/admin/models/svm", methods=["POST"])
def create_svm_model_config():
    model_key = _normalize_model_key(request.form.get("model_key", ""))
    name_en = request.form.get("name_en", "").strip()
    name_zh = request.form.get("name_zh", "").strip()

    if not model_key:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error="模型编码不能为空")
        )
    if not name_en or not name_zh:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error="模型名称(中/英)不能为空")
        )

    if not SVM_MODEL_KEY_PATTERN.match(model_key):
        return redirect(
            url_for(
                "model_admin.svm_model_admin_page",
                svm_error="SVM模型编码仅支持英文字母、数字和下划线，且只能以英文字母开头",
            )
        )

    if svm_model_exists(ModelConfig.DB_PATH, model_key):
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error=f"模型编码已存在: {model_key}")
        )

    model_dir_rel = f"svm/{model_key}"
    model_dir_abs = os.path.join(ASSETS_ROOT, "svm", model_key)

    svm_model_path = os.path.join(model_dir_abs, "svm_model_tuned.pkl")
    scaler_path = os.path.join(model_dir_abs, "scaler.pkl")
    training_csv_path = os.path.join(model_dir_abs, "training.csv")
    newdata_path = os.path.join(model_dir_abs, "newdata.txt")

    try:
        _save_uploaded_file(request.files.get("svm_model_file"), ".pkl", svm_model_path)
        _save_uploaded_file(request.files.get("scaler_file"), ".pkl", scaler_path)
        _save_uploaded_file(request.files.get("training_csv_file"), ".csv", training_csv_path)
        _save_uploaded_file(request.files.get("newdata_file"), ".txt", newdata_path)

        create_svm_model(
            db_path=ModelConfig.DB_PATH,
            model_key=model_key,
            name_en=name_en,
            name_zh=name_zh,
            model_rel_path=f"{model_dir_rel}/svm_model_tuned.pkl",
            scaler_rel_path=f"{model_dir_rel}/scaler.pkl",
            training_rel_path=f"{model_dir_rel}/training.csv",
            default_txt_rel_path=f"{model_dir_rel}/newdata.txt",
        )

        return redirect(
            url_for(
                "model_admin.svm_model_admin_page",
                svm_message=f"SVM模型上传成功(默认未激活): {model_key} ({name_zh})，请先完成概率标签检查后激活",
            )
        )
    except Exception as exc:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error=f"创建失败: {str(exc)}")
        )


@model_admin_bp.route("/admin/models/probability-labels/save", methods=["POST"])
def save_probability_label_action():
    label_key = str(request.form.get("label_key", "")).strip()
    label_en = str(request.form.get("label_en", "")).strip()
    label_zh = str(request.form.get("label_zh", "")).strip()

    if not label_key:
        return redirect(url_for("model_admin.probability_label_admin_page", prob_error="保存失败: 标签键不能为空"))
    if not label_en or not label_zh:
        return redirect(url_for("model_admin.edit_probability_label_page", label_key=label_key, prob_error=f"保存失败: {label_key} 的中英文名称不能为空"))

    try:
        upsert_probability_labels(
            ModelConfig.DB_PATH,
            [{"label_key": label_key, "label_en": label_en, "label_zh": label_zh}],
        )
        return redirect(url_for("model_admin.edit_probability_label_page", label_key=label_key, prob_message=f"已保存翻译: {label_key}"))
    except Exception as exc:
        return redirect(url_for("model_admin.edit_probability_label_page", label_key=label_key, prob_error=f"保存失败: {str(exc)}"))


@model_admin_bp.route("/admin/models/probability-labels/add", methods=["POST"])
def add_probability_label_action():
    label_key = str(request.form.get("label_key", "")).strip()
    label_en = str(request.form.get("label_en", "")).strip()
    label_zh = str(request.form.get("label_zh", "")).strip()

    if not label_key:
        return redirect(url_for("model_admin.probability_label_admin_page", prob_error="新增失败: 标签键不能为空"))
    if not label_en or not label_zh:
        return redirect(url_for("model_admin.probability_label_admin_page", prob_error=f"新增失败: {label_key} 的中英文名称不能为空"))

    try:
        upsert_probability_labels(
            ModelConfig.DB_PATH,
            [{"label_key": label_key, "label_en": label_en, "label_zh": label_zh}],
        )
        return redirect(url_for("model_admin.probability_label_admin_page", prob_message=f"已新增翻译: {label_key}"))
    except Exception as exc:
        return redirect(url_for("model_admin.probability_label_admin_page", prob_error=f"新增失败: {str(exc)}"))


@model_admin_bp.route("/admin/models/svm/activate/check", methods=["POST"])
def check_and_activate_svm_model():
    model_key = _normalize_model_key(request.form.get("model_key", ""))
    if not model_key:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error="激活失败: 模型编码不能为空")
        )

    model = get_svm_model(ModelConfig.DB_PATH, model_key)
    if not model:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error=f"激活失败: 模型不存在 {model_key}")
        )

    if model.get("is_active") == 1:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_message=f"模型已是启用状态: {model_key}")
        )

    result = _probe_svm_probabilities(model_key)
    if result.get("status") != "success":
        return redirect(
            url_for(
                "model_admin.svm_model_admin_page",
                svm_error=f"激活前预测校验失败: {result.get('message', '未知错误')}",
            )
        )

    probabilities = result.get("probabilities")
    if not isinstance(probabilities, dict):
        probabilities = {}
    label_keys = sorted(
        {
            _canonical_probability_label_key(k)
            for k in probabilities.keys()
            if _canonical_probability_label_key(k)
        }
    )

    if not label_keys:
        try:
            changed = set_svm_model_active(ModelConfig.DB_PATH, model_key, True)
            if changed <= 0:
                return redirect(
                    url_for("model_admin.svm_model_admin_page", svm_error=f"激活失败: 模型不存在 {model_key}")
                )
            return redirect(
                url_for("model_admin.svm_model_admin_page", svm_message=f"模型已激活(无概率标签): {model_key}")
            )
        except Exception as exc:
            return redirect(
                url_for("model_admin.svm_model_admin_page", svm_error=f"激活失败: {str(exc)}")
            )

    existing_map = get_probability_labels(ModelConfig.DB_PATH, label_keys)
    missing_keys = [k for k in label_keys if k not in existing_map]

    # 激活页面显示所有标签，已登记的只展示，未登记的可填写
    return _render_svm_admin_page(
        svm_error="检测到未登记的概率标签，请补全中英文名称后再激活。" if missing_keys else "",
        pending_model_key=model_key,
        pending_prob_labels=missing_keys,
        activation_mode=True,
        all_prob_labels=label_keys,
        existing_prob_label_map=existing_map,
    )


@model_admin_bp.route("/admin/models/svm/activate/register-labels", methods=["POST"])
def register_prob_labels_and_activate_svm_model():
    model_key = _normalize_model_key(request.form.get("model_key", ""))
    if not model_key:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error="提交失败: 模型编码不能为空")
        )

    label_keys = request.form.getlist("label_key")
    # 只处理未登记的标签（即表单中有填写项的标签）
    label_rows = []
    for key in label_keys:
        k = _canonical_probability_label_key(key)
        if not k:
            continue
        label_en = request.form.get(f"label_en__{k}")
        label_zh = request.form.get(f"label_zh__{k}")
        # 只处理表单中有填写项的标签（即未登记标签）
        if label_en is not None and label_zh is not None:
            label_en = label_en.strip()
            label_zh = label_zh.strip()
            if not label_en or not label_zh:
                return _render_svm_admin_page(
                    svm_error=f"标签 {k} 的中英文名称不能为空",
                    pending_model_key=model_key,
                    pending_prob_labels=[_canonical_probability_label_key(x) for x in label_keys if _canonical_probability_label_key(x)],
                    activation_mode=True,
                )
            label_rows.append({"label_key": k, "label_en": label_en, "label_zh": label_zh})

    try:
        if label_rows:
            upsert_probability_labels(ModelConfig.DB_PATH, label_rows)
        changed = set_svm_model_active(ModelConfig.DB_PATH, model_key, True)
        if changed <= 0:
            return redirect(
                url_for("model_admin.svm_model_admin_page", svm_error=f"激活失败: 模型不存在 {model_key}")
            )
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_message=f"标签登记完成并已激活模型: {model_key}")
        )
    except Exception as exc:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error=f"提交失败: {str(exc)}")
        )


@model_admin_bp.route("/admin/models/quantitative", methods=["POST"])
def create_quantitative_model_config():
    try:

        compound_key = _normalize_model_key(request.form.get("compound_key", ""))
        name_en = request.form.get("name_en", "").strip()
        name_zh = request.form.get("name_zh", "").strip()
        compound_name = name_en  # name 字段默认与 name_en 相同
        unit = request.form.get("unit", "").strip()
        required_rows = _to_int(request.form.get("required_rows", ""), "required_rows")

        intensity_1_index = _to_int(request.form.get("intensity_1_index", ""), "intensity_1_index")
        intensity_2_index = _to_int(request.form.get("intensity_2_index", ""), "intensity_2_index")

        intensity_1_row = intensity_1_index + 1
        intensity_2_row = intensity_2_index + 1
        intensity_1_col = 1
        intensity_2_col = 1

        formula_a = _to_float(request.form.get("formula_a", ""), "formula_a")
        formula_b = _to_float(request.form.get("formula_b", ""), "formula_b")

        transform_type = request.form.get("transform_type", "").strip() or None
        if transform_type and transform_type not in ALLOWED_TRANSFORM_TYPES:
            return redirect(
                url_for("model_admin.quantitative_model_admin_page", q_error="transform_type 仅支持 10^x 或留空")
            )
        formula_description = f"x = (y - {formula_b}) / {formula_a}"

        if not compound_key or not unit or not name_en or not name_zh:
            return redirect(
                url_for("model_admin.quantitative_model_admin_page", q_error="compound_key、unit、name_en、name_zh 不能为空")
            )

        if not COMPOUND_KEY_PATTERN.match(compound_key):
            return redirect(
                url_for("model_admin.quantitative_model_admin_page", q_error="compound_key 仅支持英文字母、数字和下划线，且只能以英文字母开头")
            )

        if quantitative_compound_exists(ModelConfig.DB_PATH, compound_key):
            return redirect(
                url_for("model_admin.quantitative_model_admin_page", q_error=f"定量模型编码已存在: {compound_key}")
            )

        create_quantitative_compound(
            db_path=ModelConfig.DB_PATH,
            compound_key=compound_key,
            name=compound_name,
            unit=unit,
            required_rows=required_rows,
            formula_a=formula_a,
            formula_b=formula_b,
            formula_description=formula_description,
            intensity_1_row=intensity_1_row,
            intensity_1_index=intensity_1_index,
            intensity_1_col=intensity_1_col,
            intensity_2_row=intensity_2_row,
            intensity_2_index=intensity_2_index,
            intensity_2_col=intensity_2_col,
            transform_type=transform_type,
            name_en=name_en,
            name_zh=name_zh,
        )
        return redirect(
            url_for("model_admin.quantitative_model_admin_page", q_message=f"定量模型创建成功: {compound_key}")
        )
    except Exception as exc:
        return redirect(
            url_for("model_admin.quantitative_model_admin_page", q_error=f"创建失败: {str(exc)}")
        )


@model_admin_bp.route("/admin/models/tree", methods=["POST"])
def create_tree_model_config():
    model_key = _normalize_model_key(request.form.get("model_key", ""))
    name_en = request.form.get("name_en", "").strip()
    name_zh = request.form.get("name_zh", "").strip()

    if not model_key:
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_error="模型编码不能为空")
        )
    if not name_en or not name_zh:
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_error="模型名称(中/英)不能为空")
        )

    if not SVM_MODEL_KEY_PATTERN.match(model_key):
        return redirect(
            url_for(
                "model_admin.tree_model_admin_page",
                tree_error="TREE模型编码仅支持英文字母、数字和下划线，且只能以英文字母开头",
            )
        )

    if get_tree_model(ModelConfig.DB_PATH, model_key):
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_error=f"模型编码已存在: {model_key}")
        )

    model_dir_rel = f"tree/{model_key}"
    model_dir_abs = os.path.join(ASSETS_ROOT, "tree", model_key)

    tree_model_path = os.path.join(model_dir_abs, "tree_model.pkl")
    training_csv_path = os.path.join(model_dir_abs, "training.csv")
    newdata_path = os.path.join(model_dir_abs, "newdata.txt")

    try:
        _save_uploaded_file(request.files.get("tree_model_file"), ".pkl", tree_model_path)
        _save_uploaded_file(request.files.get("training_csv_file"), ".csv", training_csv_path)
        _save_uploaded_file(request.files.get("newdata_file"), ".txt", newdata_path)

        create_tree_model(
            db_path=ModelConfig.DB_PATH,
            model_key=model_key,
            name_en=name_en,
            name_zh=name_zh,
            model_rel_path=f"{model_dir_rel}/tree_model.pkl",
            training_rel_path=f"{model_dir_rel}/training.csv",
            default_txt_rel_path=f"{model_dir_rel}/newdata.txt",
        )
        return redirect(
            url_for(
                "model_admin.tree_model_admin_page",
                tree_message=f"TREE模型上传成功: {model_key} ({name_zh})",
            )
        )
    except Exception as exc:
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_error=f"创建失败: {str(exc)}")
        )


@model_admin_bp.route("/admin/models/svm/delete", methods=["POST"])
def delete_svm_model_config():
    model_key = _normalize_model_key(request.form.get("model_key", ""))
    if not model_key:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error="删除失败: 模型编码不能为空")
        )

    model = get_svm_model(ModelConfig.DB_PATH, model_key)
    if not model:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error=f"删除失败: 模型不存在 {model_key}")
        )

    if model.get("is_builtin") == 1:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error=f"删除失败: 默认初始模型不允许删除 ({model_key})")
        )

    # 检查模型是否被站点使用
    usage_sites = get_svm_model_usage_in_sites(ModelConfig.DB_PATH, model_key)
    if usage_sites:
        site_names = "、".join([site["display_name"] for site in usage_sites])
        return redirect(
            url_for("model_admin.svm_model_admin_page", 
                   svm_error=f"删除失败: 该模型正在被站点【{site_names}】使用。请先在站点管理中移除该模型，再进行删除。")
        )

    try:
        _remove_assets_dirs_by_rel_paths(
            [
                model.get("model_rel_path"),
                model.get("scaler_rel_path"),
                model.get("training_rel_path"),
                model.get("default_txt_rel_path"),
            ]
        )
        deleted_rows = delete_svm_model(ModelConfig.DB_PATH, model_key)
        if deleted_rows <= 0:
            return redirect(
                url_for("model_admin.svm_model_admin_page", svm_error=f"删除失败: 模型不存在 {model_key}")
            )
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_message=f"SVM模型已删除: {model_key}")
        )
    except Exception as exc:
        return redirect(
            url_for("model_admin.svm_model_admin_page", svm_error=f"删除失败: {str(exc)}")
        )


@model_admin_bp.route("/admin/models/tree/delete", methods=["POST"])
def delete_tree_model_config():
    model_key = _normalize_model_key(request.form.get("model_key", ""))
    if not model_key:
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_error="删除失败: 模型编码不能为空")
        )

    model = get_tree_model(ModelConfig.DB_PATH, model_key)
    if not model:
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_error=f"删除失败: 模型不存在 {model_key}")
        )

    if model.get("is_builtin") == 1:
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_error=f"删除失败: 默认初始模型不允许删除 ({model_key})")
        )

    # 检查模型是否被站点使用
    usage_sites = get_tree_model_usage_in_sites(ModelConfig.DB_PATH, model_key)
    if usage_sites:
        site_names = "、".join([site["display_name"] for site in usage_sites])
        return redirect(
            url_for("model_admin.tree_model_admin_page", 
                   tree_error=f"删除失败: 该模型正在被站点【{site_names}】使用。请先在站点管理中移除该模型，再进行删除。")
        )

    try:
        _remove_assets_dirs_by_rel_paths(
            [
                model.get("model_rel_path"),
                model.get("training_rel_path"),
                model.get("default_txt_rel_path"),
            ]
        )
        deleted_rows = delete_tree_model(ModelConfig.DB_PATH, model_key)
        if deleted_rows <= 0:
            return redirect(
                url_for("model_admin.tree_model_admin_page", tree_error=f"删除失败: 模型不存在 {model_key}")
            )
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_message=f"TREE模型已删除: {model_key}")
        )
    except Exception as exc:
        return redirect(
            url_for("model_admin.tree_model_admin_page", tree_error=f"删除失败: {str(exc)}")
        )


@model_admin_bp.route("/admin/models/quantitative/delete", methods=["POST"])
def delete_quantitative_model_config():
    compound_key = _normalize_model_key(request.form.get("compound_key", ""))
    if not compound_key:
        return redirect(
            url_for("model_admin.quantitative_model_admin_page", q_error="删除失败: compound_key 不能为空")
        )

    compound = get_quantitative_compound(ModelConfig.DB_PATH, compound_key)
    if not compound:
        return redirect(
            url_for("model_admin.quantitative_model_admin_page", q_error=f"删除失败: 定量模型不存在 {compound_key}")
        )

    if compound.get("is_builtin") == 1:
        return redirect(
            url_for("model_admin.quantitative_model_admin_page", q_error=f"删除失败: 默认初始模型不允许删除 ({compound_key})")
        )

    # 检查模型是否被站点使用
    usage_sites = get_quantitative_model_usage_in_sites(ModelConfig.DB_PATH, compound_key)
    if usage_sites:
        site_names = "、".join([site["display_name"] for site in usage_sites])
        return redirect(
            url_for("model_admin.quantitative_model_admin_page", 
                   q_error=f"删除失败: 该模型正在被站点【{site_names}】使用。请先在站点管理中移除该模型，再进行删除。")
        )

    try:
        # 为定量模型预留目录清理：若未来使用 assets/quantitative/{compound_key}，会随配置一并删除。
        _remove_assets_dirs_by_rel_paths([f"quantitative/{compound_key}/placeholder.txt"])
        deleted_rows = delete_quantitative_compound(ModelConfig.DB_PATH, compound_key)
        if deleted_rows <= 0:
            return redirect(
                url_for("model_admin.quantitative_model_admin_page", q_error=f"删除失败: 定量模型不存在 {compound_key}")
            )
        return redirect(
            url_for("model_admin.quantitative_model_admin_page", q_message=f"定量模型已删除: {compound_key}")
        )
    except Exception as exc:
        return redirect(
            url_for("model_admin.quantitative_model_admin_page", q_error=f"删除失败: {str(exc)}")
        )
