# covid19-mie-getdata
[三重県版の新型コロナウイルス感染症対策サイト](https://github.com/FlexiblePrintedCircuits/covid19-mie)に使うためのjsonファイルを作成するプログラム

https://sakurum.github.io/covid19-mie-getdata/data.json
https://sakurum.github.io/covid19-mie-getdata/news.json

を自動更新して公開しています。

## 動作

:warning: [WIP] 以下の記事の時点から大幅に内容を更新しています。READMEは現在作成中ですので、main.pyをご確認下さい。
<!--
### GitHub Actionsによる定期実行について
6時間に一度、`main.py`が実行され、[data.json](https://raw.githubusercontent.com/sakurum/covid19-mie-getdata/gh-pages/data.json)と[news.json](https://raw.githubusercontent.com/sakurum/covid19-mie-getdata/gh-pages/news.json)が更新されます。
-->

更新しているデータ
| key | 状況 |
| --- | --- |
| patients | 正常（2020/09/20）|
| patients_summary | 正常（2020/09/20）|
| inspections_summary | 正常（2020/09/20）|
| nowinfectedperson | 取得できていない |

<!--
### 単体の動作について
`main.py`が実行されると、三重県Webサイトと下記のjsonファイルから情報を取得し、`data.json`と`news.json`を作成します。

`data.json`の雛形として`data_template.json`を読み込みます。

`data.json`の項目のデフォルト値は`data_template.json`の値です。

## 取得する情報のソースについて
以下のように対応します。

まず、[新型コロナウイルス感染症検査実施件数一覧及び県内で発生した事例一覧](https://www.pref.mie.lg.jp/YAKUMUS/HP/m0068000071_00022.htm)から、新型コロナウイルス感染症検査実施件数一覧と県内で発生した事例一覧のcsvファイルのリンクを取得します。（何故かファイルのリンクが更新の度に変わる仕様だったので...）

それから、新型コロナウイルス感染症検査実施件数一覧と県内で発生した事例一覧のcsvファイルを読み込み、データを取得します。

#### data.json
data.jsonの項目（出力） | 情報ソース（入力）
--- | ---
contacts | なし（data_template.jsonそのまま）
querents | なし（data_template.jsonそのまま）
patients | 県内で発生した事例一覧
patients_summary | patients_summary.json
discharges_summary | なし（data_template.jsonそのまま）
inspections | なし（data_template.jsonそのまま）
inspections_summary | 新型コロナウイルス感染症検査実施件数一覧
better_patients_summary | なし（data_template.jsonそのまま）
lastUpdate | main.pyが実行された時刻
main_summary | なし（data_template.jsonそのまま）
nowinfectedperson | なし（data_template.jsonそのまま）


#### news.json
news.jsonの項目（出力） | 情報ソース（入力）
--- | ---
newsItems | [三重県Webサイト]("https://www.pref.mie.lg.jp/index.shtm")


## 使い方
```bash
$ python3 main.py
```

とすると、`data.json`と`news.json`がカレントディレクトリに作成されます。


上記の情報ソースの対応表より、必要なjsonファイルをカレントディレクトリに置いてから実行してください。

（現状では一部しか対応しておらず、例外処理も行っていません。）

-->

## 記事を書きました
https://qiita.com/sakuranomiyu/items/30c09efaf717b5e82973
