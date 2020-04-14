# coding: utf-8

import json
import datetime
import requests
from bs4 import BeautifulSoup

import csv
import pandas
import re

# url
INDEX_URL = "https://www.pref.mie.lg.jp"
NEWS_TARGET_URL = "https://www.pref.mie.lg.jp/index.shtm"

# 使ってない
# INSPECTIONS_SUMMARY_TARGET_URL = "https://www.pref.mie.lg.jp/YAKUMUS/HP/m0068000071_00005.htm"


# import json(template)
def import_json(filename):
    with open(filename, "r") as f:
        dict = json.load(f)
        return dict

# export json
def export_json(obj, filename):
    with open(filename, "w") as f:
        json.dump(
            obj=obj,
            fp=f,
            ensure_ascii=False,
            indent=4,
            sort_keys=False,
            separators=None
            )


# yyyy/mm/ddを変換
def val_to_datestr(val):
    m = re.findall(r"\d+", val)
    date = datetime.datetime(int(m[0]), int(m[1]), int(m[2]))
    datestr = date.strftime("%Y-%m-%dT00:00:00.000+09:00")

    return datestr


# オープンデータの最終更新日をとってくる
def get_lastupdate():
    target_url = "https://www.pref.mie.lg.jp/YAKUMUS/HP/m0068000071_00022.htm"
    response = requests.get(target_url)
    soup = BeautifulSoup(response.content, features="html.parser")

    text = soup.find(string="最終更新日").next

    # 全角 to 半角
    text = text.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
    # 数字のみ取得
    m = re.findall(r"\d+", text)

    date = datetime.datetime(int(m[0])+2018, int(m[1]), int(m[2]))
    lastupdate = date.strftime("%Y/%m/%d 00:00")

    return lastupdate


# 新着情報をとってくる
def get_whatsnew():
    target_url = NEWS_TARGET_URL
    response = requests.get(target_url)
    soup = BeautifulSoup(response.content, features="html.parser")

    divbox = soup.find(class_="box-emergency-inner")
    ullist = divbox.ul.find_all("li")

    # newsの辞書型のリスト
    newslist = []

    for li in ullist:
        url = INDEX_URL + li.a.get("href")
        text = li.a.get_text()

        # 最終更新日時を調べる
        response = requests.head(url)
        str = response.headers["Last-Modified"]
        lastupdate = datetime.datetime.strptime(str, "%a, %d %b %Y %H:%M:%S GMT")
        date = lastupdate.strftime("%Y/%m/%d")

        news = {"date": date, "url": url, "text": text}
        newslist.append(news)

    # 上位3件のみ抜粋
    dict = {"newsItems": newslist[0:3]}

    return dict

def get_lastupdate():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M")

# 検査実施数をとってくる
def get_inspections_summary():
    csv_url = "https://www.pref.mie.lg.jp/common/content/000885246.csv"

    # 必要な要素の抽出
    df = pandas.read_csv(csv_url, encoding="shift_jis")
    df.rename(columns={"検査件数": "小計"}, inplace=True)
    df["日付"] = df["日付"].apply(val_to_datestr)

    # jsonに書き出すリスト
    datalist = df[["小計", "日付"]].to_dict(orient="records")

    # 辞書を作成
    dict = {"date": get_lastupdate(), "data": datalist}

    return dict

# patientsをとってくる
def get_patients():
    with open("./patients.json", "r") as f:
        patients_dict = json.load(f)
        return patients_dict

# patients_summaryをとってくる
def get_patients_summary():
    with open("./patients_summary.json", "r") as f:
        patients_summary_dict = json.load(f)
        return patients_summary_dict


# main
if __name__ == "__main__":
    # ---- make data.json ----
    # make update data
    """
        "contacts",
        "querents",
        "patients",
        "patients_summary",
        "discharges_summary",
        "inspections",
        "inspections_summary",
        "better_patients_summary",
        "lastUpdate",
        "main_summary"
    """

    update_dict = {
        "inspections_summary" : get_inspections_summary(),
        "patients" : get_patients(),
        "patients_summary" : get_patients_summary(),
        "lastUpdate": get_lastupdate()
    }
    # import template
    dict = import_json("./data_template.json")

    # update
    dict.update(update_dict)

    # export data.json
    export_json(obj=dict, filename="./data/data.json")


    # ---- make news.json ----
    newslist = get_whatsnew()
    export_json(newslist, "./data/news.json")
