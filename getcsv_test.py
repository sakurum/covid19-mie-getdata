# coding: utf-8

import csv
import json
import pandas
import pprint
import datetime
import requests
import re
from bs4 import BeautifulSoup

def show_csv(url):
    df = pandas.read_csv(url, encoding="shift_jis")
    pprint.pprint(df)

def get_csv():
    url = "https://www.pref.mie.lg.jp/common/content/000885246.csv"
    df = pandas.read_csv(url, encoding="shift_jis")
    json = df.to_json(orient="records")

    df.rename(columns={"検査件数": "小計"}, inplace=True)
    df["日付"] = df["日付"].apply(val_to_datestr)

    pprint.pprint(df)

    print(df[["日付", "小計"]])
    list = df[["小計", "日付"]].to_dict(orient="records")

    pprint.pprint(list)


def val_to_datestr(val):
    m = re.findall(r"\d+", val)
    date = datetime.datetime(int(m[0]), int(m[1]), int(m[2]))
    datestr = date.strftime("%Y-%m-%dT00:00:00.000+09:00")

    return datestr

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
    show_csv("https://www.pref.mie.lg.jp/common/content/000883953.csv")
