# coding=utf-8
import sqlite3
from typing import Dict
from config.settings import ModelConfig

def update_db_prob_names():
    en_names = {
        "vitaminD3": "Vitamin D3",
        "vitaminK3": "Vitamin K3",
        "retinol": "Retinol",
        "betaCarotene": "β-Carotene",
        "BRCA1-MT": "BRCA1-MT in Water",
        "BRCA1-MT-S": "BRCA1-MT in Serum",
        "BRCA1-WT": "BRCA1-WT in Water",
        "BRCA1-WT-S": "BRCA1-WT in Serum",
        "10:01": "BRCA1-WT:BRCA1-MT=10:1",
        "5:01": "BRCA1-WT:BRCA1-MT=5:1",
        "1:01": "BRCA1-WT:BRCA1-MT=1:1",
        "1:05": "BRCA1-WT:BRCA1-MT=1:5",
        "1:10": "BRCA1-WT:BRCA1-MT=1:10",
        "p16": "p16 in Water",
        "p16-S": "p16 in Serum",
        "p21": "p21 in Water",
        "p21-S": "p21 in Serum",
        "p53": "p53 in Water",
        "p53-S": "p53 in Serum",
        "1:01:01": "p16:p21:p53=1:1:1",
        "1:01:02": "p16:p21:p53=1:1:2",
        "1:02:01": "p16:p21:p53=1:2:1",
        "2:01:01": "p16:p21:p53=2:1:1",
        "HPV18 Clinical Sample": "HPV18 Clinical Sample",
        "HPV16 Clinical Sample": "HPV16 Clinical Sample",
        "Acetone": "Acetone",
        "Formaldehyde": "Formaldehyde",
        "Styrene": "Styrene",
        "Xylene": "Xylene",
        "CR": "CR",
        "CRP": "CRP",
        "IL-6": "IL-6",
        "LA": "LA",
        "PCT": "PCT",
        "UA": "UA",
        "ACE": "Acephate",
        "DM": "Dimethoate",
        "DQ": "Diquat",
        "TBZ": "Thiabendazole",
        "Thiram": "Thiram",
        "Normal": "Normal",
        "Osteopenia": "Osteopenia",
        "Osteoporosis": "Osteoporosis",
        "CIP": "CIP",
        "ENRO": "ENRO",
        "NORF": "NORF",
        "PEF": "PEF",
        "LVFX": "LVFX",
        "2_8": "2:8",
        "4_6": "4:6",
        "5_5": "5:5",
        "6_4": "6:4",
        "8_2": "8:2",
        "2_4_4": "2:4:4",
        "2_6_2": "2:6:2",
        "4_2_4": "4:2:4",
        "4_4_2": "4:4:2",
        "6_2_2": "6:2:2",
    }

    zh_names = {
        "vitaminD3": "维生素D3",
        "vitaminK3": "维生素K3",
        "retinol": "视黄醇",
        "betaCarotene": "β-胡萝卜素",
        "BRCA1-MT": "水中含有BRCA1-MT",
        "BRCA1-MT-S": "血清中含有BRCA1-MT",
        "BRCA1-WT": "水中含有BRCA1-WT",
        "BRCA1-WT-S": "血清中含有BRCA1-WT",
        "10:01": "BRCA1-WT：BRCA1-MT=10:1",
        "5:01": "BRCA1-WT：BRCA1-MT=5:1",
        "1:01": "BRCA1-WT：BRCA1-MT=1:1",
        "1:05": "BRCA1-WT：BRCA1-MT=1:5",
        "1:10": "BRCA1-WT：BRCA1-MT=1:10",
        "p16": "水中含有p16",
        "p16-S": "血清中含有p16",
        "p21": "水中含有p21",
        "p21-S": "血清中含有p21",
        "p53": "水中含有p53",
        "p53-S": "血清中含有p53",
        "1:01:01": "p16：p21：p53=1:1:1",
        "1:01:02": "p16：p21：p53=1:1:2",
        "1:02:01": "p16：p21：p53=1:2:1",
        "2:01:01": "p16：p21：p53=2:1:1",
        "HPV18 Clinical Sample": "HPV18 临床样本",
        "HPV16 Clinical Sample": "HPV16 临床样本",
        "Acetone": "丙酮",
        "Formaldehyde": "甲醛",
        "Styrene": "苯乙烯",
        "Xylene": "二甲苯",
        "CR": "CR",
        "CRP": "CRP",
        "IL-6": "IL-6",
        "LA": "LA",
        "PCT": "PCT",
        "UA": "UA",
        "ACE": "乙酰甲胺磷",
        "DM": "乐果",
        "DQ": "敌草快",
        "TBZ": "噻菌灵",
        "Thiram": "福美双",
        "Normal": "正常",
        "Osteopenia": "骨量减少",
        "Osteoporosis": "骨质疏松症",
        "CIP": "CIP",
        "ENRO": "ENRO",
        "NORF": "NORF",
        "PEF": "PEF",
        "LVFX": "LVFX",
        "2_8": "2:8",
        "4_6": "4:6",
        "5_5": "5:5",
        "6_4": "6:4",
        "8_2": "8:2",
        "2_4_4": "2:4:4",
        "2_6_2": "2:6:2",
        "4_2_4": "4:2:4",
        "4_4_2": "4:4:2",
        "6_2_2": "6:2:2",
    }

    conn = sqlite3.connect(ModelConfig.DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS probability_labels (
                label_key TEXT PRIMARY KEY,
                label_en TEXT NOT NULL,
                label_zh TEXT NOT NULL
            )
            """
        )

        for key in en_names:
            en = en_names[key]
            zh = zh_names.get(key, "")
            conn.execute(
                """
                INSERT INTO probability_labels (label_key, label_en, label_zh)
                VALUES (?, ?, ?)
                ON CONFLICT(label_key) DO UPDATE SET
                label_en=excluded.label_en,
                label_zh=excluded.label_zh
                """,
                (key, en, zh)
            )

        conn.commit()
        print("Updated probability labels in database.")
    finally:
        conn.close()

if __name__ == "__main__":
    update_db_prob_names()
