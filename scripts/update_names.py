# coding=utf-8
import sqlite3
from typing import Dict
from config.settings import ModelConfig

def update_db_lang_names():
    en_names = {
        "default": "Default Model",
        "brca": "BRCA Model",
        "brca_mix": "BRCA Mix Model",
        "p": "P Model",
        "p_mix": "P Mix Model",
        "hpv": "HPV Model",
        "gzb": "GZB Model",
        "retinol": "Retinol",
        "vitamin_k": "Vitamin K",
        "vitamin_d": "Vitamin D",
        "carotene": "Carotene",
        "brca1_mt": "BRCA1 MT",
        "brca1_wt": "BRCA1 WT",
        "p16": "p16",
        "p21": "p21",
        "p53": "p53",
        "hu_r": "Carotene and Retinol Mix",
        "hu_vd": "Carotene and VD Mix",
        "hu_vd_vk": "Carotene, VD and VK Mix",
        "hu_vk": "Carotene and VK Mix",
        "vk_r_vd": "Retinol, VK and VD Mix",
        "han": "Sweat",
        "lei": "Tear",
        "niao": "Urine",
        "shui": "Water",
        "xueqing": "Serum",
        "crp": "C-Reactive Protein",
        "il": "Interleukin",
        "ua": "Uric Acid",
        "pesticide": "Pesticide",
        "sjl": "Thiabendazole",
        "fms": "Thiram",
        "osteoporosis": "Osteoporosis",
        "quino": "Quino",
        "ciplvfx": "CIP:LVFX",
        "cippef": "CIP:PEF",
        "cippeflvfx": "CIP:PEF:LVFX",
        "peflvfx": "PEF:LVFX",
        "cip": "CIP",
        "norf": "NORF",
        "pef": "PEF",
        "cip_rengonghu": "CIP(Artificial Lake)",
    }

    zh_names = {
        "default": "默认模型",
        "retinol": "视黄醇 (Retinol)",
        "vitamin_k": "维生素K (Vitamin K)",
        "vitamin_d": "维生素D (Vitamin D)",
        "carotene": "胡萝卜素 (Carotene)",
        "brca": "BRCA模型",
        "brca_mix": "BRCA混合模型",
        "p": "P模型",
        "p_mix": "P混合模型",
        "hpv": "HPV模型",
        "gzb": "GZB模型",
        "brca1_mt": "BRCA1突变型",
        "brca1_wt": "BRCA1野生型",
        "p16": "p16",
        "p21": "p21",
        "p53": "p53",
        "hu_r": "胡萝卜素和视黄醇混合",
        "hu_vd": "胡萝卜素和VD混合",
        "hu_vd_vk": "胡萝卜素和VD、VK混合",
        "hu_vk": "胡萝卜素和VK混合",
        "vk_r_vd": "视黄醇和VK、VD混合",
        "han": "汗液",
        "lei": "泪液",
        "niao": "尿液",
        "shui": "水",
        "xueqing": "血清",
        "crp": "C反应蛋白",
        "il": "白细胞介素",
        "ua": "尿酸",
        "pesticide": "农药",
        "sjl": "噻菌灵",
        "fms": "福美双",
        "osteoporosis": "骨质疏松",
        "quino": "Quino",
        "ciplvfx": "CIP:LVFX",
        "cippef": "CIP:PEF",
        "cippeflvfx": "CIP:PEF:LVFX",
        "peflvfx": "PEF:LVFX",
        "cip": "CIP",
        "norf": "NORF",
        "pef": "PEF",
        "cip_rengonghu": "CIP（人工湖）",
    }

    conn = sqlite3.connect(ModelConfig.DB_PATH)
    try:
        # Check and add columns if they don't exist
        for table in ["svm_models", "tree_models", "quantitative_compounds"]:
            rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
            cols = {r[1] for r in rows}
            if "name_en" not in cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN name_en TEXT")
            if "name_zh" not in cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN name_zh TEXT")

        for key in en_names:
            en = en_names[key]
            zh = zh_names.get(key, "")
            conn.execute("UPDATE svm_models SET name_en=?, name_zh=? WHERE model_key=?", (en, zh, key))
            conn.execute("UPDATE tree_models SET name_en=?, name_zh=? WHERE model_key=?", (en, zh, key))
            conn.execute("UPDATE quantitative_compounds SET name_en=?, name_zh=? WHERE compound_key=?", (en, zh, key))

        conn.commit()
        print("Updated language configs in database.")
    finally:
        conn.close()

if __name__ == "__main__":
    update_db_lang_names()
