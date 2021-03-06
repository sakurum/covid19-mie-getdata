# coding: utf-8

import json
import datetime
import requests
import csv
import pandas
import re
from bs4 import BeautifulSoup

import pprint


DATA_FILENAME = "data/data.json"
NEWS_FILENAME = "data/news.json"

class DataManager():
    def __init__(self):
        self._data = self._load_json(DATA_FILENAME)
        self._news = self._load_json(NEWS_FILENAME)


    def _update(self):
        self._update_patients()
        self._update_patients_summary()
        self._update_inspections_summary()
        self._update_nowinfectedperson()
        self._update_last_update()
        self._dump_json(self._data, DATA_FILENAME)

        self._update_whatsnew()
        self._dump_json(self._news, NEWS_FILENAME)


    def _load_json(self, filename):
        with open(filename, "r") as fp:
            data = json.load(fp)
            return data


    def _dump_json(self, data, filename):
        with open(filename, "w") as fp:
            json.dump(
                obj=data,
                fp=fp,
                ensure_ascii=False,
                indent=4,
                sort_keys=False,
                separators=None
            )


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
    def _update_patients(self):
        url = "https://www.pref.mie.lg.jp/common/content/000896797.csv"
        try:
            df = pandas.read_csv(url, encoding="shift_jis")
        except Exception as e:
            print(type(e), e)
            return
        else:
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
            self._data["patients"].update(dict)


    # 陽性患者が確認された件数
    def _update_patients_summary(self):
        # patientsのcsvからカウントする
        url = "https://www.pref.mie.lg.jp/common/content/000896797.csv"
        try:
            df = pandas.read_csv(url, encoding="shift_jis")
        except Exception as e:
            print(type(e), e)
            return
        else:
            df.replace({pandas.np.nan: None}, inplace=True)
            df.rename(
                columns={
                    "公表年月日": "リリース日"
                },
                inplace=True
            )
            df["リリース日"] = df["リリース日"].apply(self._val2datastr)
            d = df["リリース日"].value_counts().to_dict()

            data = []
            for key, value in d.items():
                data.append({"日付": key, "小計": value})

            data.sort(key=lambda x: x["日付"])

            # データがない日付は小計を0にする
            begin = datetime.datetime.strptime(data[0]["日付"], "%Y-%m-%dT00:00:00.000+09:00")
            end = datetime.datetime.strptime(data[-1]["日付"], "%Y-%m-%dT00:00:00.000+09:00")

            for i in range((end - begin).days):
                key = (begin + datetime.timedelta(days=i)).strftime("%Y-%m-%dT00:00:00.000+09:00")
                if key != data[i]["日付"]:
                    data.insert(i, {"日付": key, "小計": 0})

            dict = {"date": self._get_lastupdate(), "data": data}
            self._data["patients_summary"].update(dict)


    # 検査実施数
    def _update_inspections_summary(self):
        url = "https://www.pref.mie.lg.jp/common/content/000896967.csv"
        try:
            df = pandas.read_csv(url, encoding="shift_jis")
        except Exception as e:
            print(type(e), e)
            return
        else:
            df.rename(columns={"検査件数": "小計"}, inplace=True)
            df["日付"] = df["日付"].apply(self._val2datastr)
            datalist = df[["小計", "日付"]].to_dict(orient="records")

            dict = {"date": self._get_lastupdate(), "data": datalist}
            self._data["inspections_summary"].update(dict)


    # 日別の陽性患者数
    def _update_nowinfectedperson(self):
        url = "https://www.pref.mie.lg.jp/YAKUMUS/HP/m0068000066_00002.htm"
        try:
            response = requests.get(url)
        except Exception as e:
            print(type(e), e)
            return
        else:
            try:
                soup = BeautifulSoup(response.content, features="html.parser")

                # 陽性患者数を取得
                nip_str = soup.find("span", string="陽性患者数").next_sibling.next_sibling.find_all("span")[1].text
                nip_str = nip_str.replace("名", "")
                nip_num = int(nip_str.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})))

                # その日付を取得
                datestr = re.findall(r"入退院状況（令和[0-9 ０-９]{1,2}年[0-9 ０-９]{1,2}月[0-9 ０-９]{1,2}日現在）", soup.find("div", class_="main-text").text)[0]
                datestr = datestr.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
                m = re.findall(r"\d+", datestr)
                date = datetime.date(int(m[0])+2018, int(m[1]), int(m[2])).strftime("%Y-%m-%dT00:00:00.000+09:00")

                if self._data["nowinfectedperson"]["data"][-1]["日付"] == date:
                    return

            except Exception as e:
                print(type(e), e)
                return
                
            else:
                self._data["nowinfectedperson"]["data"].append({"日付": date, "小計": nip_num})
                self._data["nowinfectedperson"]["date"] = self._get_lastupdate()


    def _update_last_update(self):
        self._data["lastUpdate"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")


    # 新着情報を取得
    def _update_whatsnew(self):
        url = "https://www.pref.mie.lg.jp/index.shtm"
        try:
            response = requests.get(url)
        except Exception as e:
            print(type(e), e)
            return
        else:
            soup = BeautifulSoup(response.content, features="html.parser")
            divbox = soup.find(class_="box-emergency-inner")
            ullist = divbox.ul.find_all("li")

            newslist = []
            for li in ullist:
                try:
                    url = "https://www.pref.mie.lg.jp" + li.a.get("href")
                    text = li.a.get_text()

                    # 最終更新日時を調べる
                    response = requests.head(url)
                except:
                    pass
                else:
                    str = response.headers["Last-Modified"]
                    lastupdate = datetime.datetime.strptime(str, "%a, %d %b %Y %H:%M:%S GMT")
                    date = lastupdate.strftime("%Y/%m/%d")

                    news = {"date": date, "url": url, "text": text}
                    newslist.append(news)


            # 上位3件のみ抜粋
            dict = {"newsItems": newslist[0:3]}
            self._news.update(dict)


if __name__ == "__main__":
    dm = DataManager()
    dm._update()
