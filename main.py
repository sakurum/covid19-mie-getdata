# coding: utf-8

import json
import datetime
import requests
import csv
import pandas
import re
from bs4 import BeautifulSoup

class DataManager():
    def __init__(self):
        pass


    def _update(self):
        pass


    # グラフに用いる最終更新日時
    def _get_lastupdate(self):
        # オープンデータの最終更新日時がどこにも表記されていないので現在時刻を使用
        return datetime.datetime.now().strftime("%Y/%m/%d %H:%M")


    # yyyy/mm/ddを変換
    def _val2datastr(self, val):
        m = re.findall(r"\d+", val)
        date = datetime.datetime(int(m[0]), int(m[1]), int(m[2]))
        return date.strftime("%Y-%m-%dT00:00:00.000+09:00")


    # 陽性患者の属性
    def _get_patients(self):
        url = "https://www.pref.mie.lg.jp/common/content/000896797.csv"

        df = pandas.read_csv(url, encoding="shift_jis")
        df.replace({pandas.np.nan: None}, inplace=True)
        df.rename(
            columns={
                "公表年月日": "リリース日",
                "退院済フラグ": "退院",
                "発症_年月日": "date"
            },
            inplace=True
        )
        df["リリース日"] = df["リリース日"].apply(self._val2datastr)
        output_columns = ["リリース日", "居住地", "年代", "性別", "退院", "date"]
        datalist = df[output_columns].to_dict(orient="records")

        dict = {"date": self._get_lastupdate(), "data": datalist}
        return dict


    # 陽性患者が確認された件数
    def _get_patients_summary(self):
        # patientsのcsvからカウントする
        pass


    # 検査実施数
    def _get_inspections_summary(self):
        url = "https://www.pref.mie.lg.jp/common/content/000896967.csv"

        df = pandas.read_csv(url, encoding="shift_jis")
        df.rename(columns={"検査件数": "小計"}, inplace=True)
        df["日付"] = df["日付"].apply(self._val2datastr)
        datalist = df[["小計", "日付"]].to_dict(orient="records")

        dict = {"date": self._get_lastupdate(), "data": datalist}
        return dict


    # 日別の陽性患者数
    def _get_nowinfectedperson(self):
        url = "https://www.pref.mie.lg.jp/YAKUMUS/HP/m0068000066_00002.htm"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, features="html.parser")

        # 陽性患者数を取得
        nip_str = soup.find("span", string="陽性患者数").next_sibling.next_sibling.find_all("span")[1].text
        nip_str = nip_str.replace("名", "")
        nip_num = int(nip_str.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})))
        print(nip_num)

        # その日付を取得
        datestr = re.findall(r"（令和.年.月.日現在）", soup.find("div", class_="main-text").text)[0]
        datestr = datestr.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
        m = re.findall(r"\d+", datestr)
        date = datetime.date(int(m[0])+2018, int(m[1]), int(m[2])).strftime("%Y-%m-%dT00:00:00.000+09:00")

        print(date)


if __name__ == "__main__":
    dm = DataManager()
    dm._get_nowinfectedperson()
