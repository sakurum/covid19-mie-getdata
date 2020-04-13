# coding: utf-8

import csv
import json
import pandas
import pprint
import datetime
import requests
import re
from bs4 import BeautifulSoup

url = "https://www.pref.mie.lg.jp/common/content/000885246.csv"


def get_csv(url):
    df = pandas.read_csv(url, encoding="shift_jis")
    json = df.to_json(orient="records")
    pprint.pprint(df)
    # pprint.pprint(str(json).encode().decode("unicode-escape"))

def csv_to_dict(csvfile):

    json_list = []
    json_data = {}

    data = []
    with open(csvfile, "r", encoding="shift_jis") as f:
        for line in csv.DictReader(f):
            data.append(line)

        dict = {"csvfile": data}

    return dict

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
    lastupdate = date.strftime("%Y/%m/%d")

    return lastupdate

if __name__ == "__main__":
    print(get_lastupdate())
