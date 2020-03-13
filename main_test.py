# coding: utf-8

import json
import datetime
import requests
from bs4 import BeautifulSoup

target_url = "https://www.pref.mie.lg.jp/YAKUMUS/HP/m0068000071_00005.htm"
response = requests.get(target_url)
soup = BeautifulSoup(response.content, features="html.parser")


def get_dataset(table):
    # key = ["date", "inspections", "positive", "negative"]

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

    return dataset

def datetime_to_mystr(date):
    # to 2020-03-07T18:00:00.000+09:00
    # 18時のデータとする。
    datestr = date.strftime("%Y-%m-%dT%18:%M:%S+09:00")
    return datestr

def convert_inspections_sammary(dataset):
    # data
    data_dict_array = []
    for data in dataset:
        data_dict = {"日付": datetime_to_mystr(data[0]), "小計": data[1]}
        data_dict_array.append(data_dict)

    # dateを作成
    date_str = "2020\/00\/00 00:00"

    # 辞書を作成
    dict = {"date": date_str, "data": data_dict_array}

    return dict

def export_json(obj):
    f = open("date.json", "w")
    json.dump(
        obj=obj,
        fp=f,
        ensure_ascii=False,
        indent=4,
        sort_keys=False,
        separators=None
        )


if __name__ == "__main__":
    dataset = get_dataset(soup.table)

    dict = convert_inspections_sammary(dataset)

    export_json(obj=dict)
