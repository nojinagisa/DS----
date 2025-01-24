#スクレイピングできたものをデータベースに保存する
import requests
from bs4 import BeautifulSoup
import time
import sqlite3

# 取得したデータを保存するデータベース
db_name = 'jalan_reviews.db'

# データベース接続
con = sqlite3.connect(db_name)
cur = con.cursor()

# テーブルを作成(評価と時期を保存)
cur.execute('''
    CREATE TABLE IF NOT EXISTS jalan_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        item_value TEXT,
        season TEXT
    )
''')

# ベースURL(ページが変わるため、URLの一部を変数にしておく)
base_url = 'https://www.jalan.net/yad317902/kuchikomi'
query_params = '?screenId=UWW3701&idx={idx}&smlCd=091102&dateUndecided=1&adultNum=2&yadNo=317902&distCd=01'

def scrape_reviews(url):
    #サイトに負荷をかけないように1秒スリープ
    time.sleep(1)
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    #ほしい情報が入ってるタグから要素を取得
    reviews = soup.find_all('div', class_='jlnpc-kuchikomiCassette')
    #口コミの取得をループで回す
    for review in reviews:
        #評価項目と評価値を取得(口コミの評価)
        rate_list = review.find('dl', class_='jlnpc-kuchikomiCassette__rateList')
        #宿泊プランの情報を取得(宿泊時期)
        plan_info_list = review.find('dl', class_='jlnpc-kuchikomiCassette__planInfoList')

        if rate_list and plan_info_list:
            #評価項目のリスト
            dt_tags = rate_list.find_all('dt')
            #評価値のリスト
            dd_tags = rate_list.find_all('dd')
            #宿泊時期の取得
            season_dd = plan_info_list.find('dd')
            season = season_dd.text.strip() if season_dd else "時期不明"

            for dt_tag, dd_tag in zip(dt_tags, dd_tags):
                item_name = dt_tag.text.strip()
                #空白や記号を削除
                item_value = dd_tag.text.replace('"', '').strip()
                
                # データベースに保存
                cur.execute("INSERT INTO jalan_reviews (item_name, item_value, season) VALUES (?, ?, ?)", (item_name, item_value, season))

# 1ページ目の処理
scrape_reviews(f"{base_url}/?{query_params.format(idx=0)}")

# 2ページ目以降の処理
last_page_num = 10  # 実際の最終ページ番号に適宜変更 
for page_num in range(2, last_page_num + 1):
    page_url = f"{base_url}/{page_num}.HTML?{query_params.format(idx=30*(page_num-1))}"
    scrape_reviews(page_url)

# 変更をコミットして接続を閉じる
con.commit()
con.close()