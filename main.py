# coding: utf-8

import json
import datetime
import requests
from bs4 import BeautifulSoup

# url
INDEX_URL = "https://www.pref.mie.lg.jp"
NEWS_TARGET_URL = "https://www.pref.mie.lg.jp/index.shtm"
INSPECTIONS_SUMMARY_TARGET_URL = "https://www.pref.mie.lg.jp/YAKUMUS/HP/m0068000071_00005.htm"

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

# datetimeをjsonにある文字列に変換
def datetime_to_mystr(date):
    # to 2020-03-07T18:00:00.000+09:00
    # 18時のデータとする。
    datestr = date.strftime("%Y-%m-%dT%18:%M:%S+09:00")
    return datestr

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

    dict = {"newsItems": newslist[0:3]}

    return dict


# 検査実施数をとってくる
def get_inspections_summary():
    target_url = INSPECTIONS_SUMMARY_TARGET_URL
    response = requests.get(target_url)
    soup = BeautifulSoup(response.content, features="html.parser")

    # key = ["date", "inspections", "positive", "negative"]
    table = soup.table
    dataset = []

    # tableから情報を抜き出す
    rows = table.find_all("tr")
    for i in range(len(rows) - 1):
        if i==0:
            continue

        cells = rows[i].find_all("td")

        data = []
        for cell in cells:
            text = cell.get_text()
            # 全角 to 半角
            text = text.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
            # 空白を消す
            text = text.replace(" ", "").replace("　","")
            data.append(text)

        # m月d日の処理
        date_str = str(data[0].replace("月", "/").replace("日", ""))
        data[0] = datetime.datetime.strptime("2020/"+date_str, "%Y/%m/%d")

        # 数の処理
        data[1] = data[1].replace("件", "")
        data[2] = data[2].replace("件", "")
        data[3] = data[3].replace("件", "")

        dataset.append(data)

    # 念の為日付でソートする
    dataset = sorted(dataset)

    # データにない日付を補完する
    i = 0
    while (dataset[-1][0]-dataset[i][0]).days > 1:
        dt = dataset[i][0]+datetime.timedelta(days=1)
        if dt != dataset[i+1][0]:
            dataset.insert(i+1, [dt, 0, 0, 0])

        i += 1


    # ここから整形処理
    data_dict_array = []
    for data in dataset:
        data_dict = {"日付": datetime_to_mystr(data[0]), "小計": data[1]}
        data_dict_array.append(data_dict)

    # dateを作成
    date_str = "2020/00/00 00:00"

    # 辞書を作成
    dict = {"date": date_str, "data": data_dict_array}

    return dict

# patientsをとってくる
def get_patients():
    with open("patients.json", "r") as f:
        patients_dict = json.load(f)
        return patients_dict


if __name__ == "__main__":
    # ---- make data.json ----
    # make update data
    inspections_summary = get_inspections_summary()
    patients = get_patients()

    update_dict = {
        "inspections_summary" : inspections_summary,
        "patients" : patients
    }

    # import template
    dict = import_json("data_template.json")

    # update
    dict.update(update_dict)

    # export data.json
    export_json(obj=dict, filename="data.json")


    # ---- make news.json ----
    newslist = get_whatsnew()
    export_json(newslist, "news.json")
