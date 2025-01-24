# 作ったデータベースを読み込み、分析を行う
import sqlite3
import pandas as pd
import scipy.stats as stats
import re
import seaborn as sns
import matplotlib.pyplot as plt
import japanize_matplotlib

# SQLiteデータベースに接続
conn = sqlite3.connect('jalan_reviews.db')

# データベースからデータを読み込む
df = pd.read_sql('SELECT * FROM jalan_reviews', conn)

# 先頭の5行を表示
#print(df.head())
# 欠損値がないか確認
#print(df.isnull().sum())

#データを綺麗に整理する
room = df[df['item_name'] == '部屋']
bath = df[df['item_name'] == '風呂']
breakfast = df[df['item_name'] == '料理(朝食)']
dinner = df[df['item_name'] == '料理(夕食)']
service = df[df['item_name'] == '接客・サービス']
clean = df[df['item_name'] == '清潔感']
# 時期のデータを数値だけに変換
def convert_season(season_str):
    match = re.match(r'(\d+)年(\d+)月宿泊', season_str)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return year + month / 12
    # 変換できない場合はNone
    else:
        return None  

# seasonカラムを変換
df['season'] = df['season'].apply(convert_season)


# item_value列を数値型に変換
df['item_value'] = pd.to_numeric(df['item_value'], errors='coerce')

# NaNを含む行を削除
df = df.dropna(subset=['item_value'])

# データを大きい順に並び替え
bath_sorted = bath.sort_values(by='item_value', ascending=False)
bath_sorted = bath_sorted.sort_values(by=['season', 'item_value'], ascending=[False, False], na_position='last') 
clean_sorted = clean.sort_values(by='item_value',ascending=False)

# 正規性の確認
shapiro_A = stats.shapiro(df['item_value'])
shapiro_B = stats.shapiro(df['season'])
# p値が0.05未満の場合、正規分布とは異なると判断
print(f'評価の正規性の検定結果: {shapiro_A}')
print(f'時期の正規性の検定結果: {shapiro_B}')

# 清潔感とサービスの散布図を描画
plt.figure(figsize=(10, 6))
sns.scatterplot(x='item_value', y='item_value', data=clean_sorted, hue='item_name')
plt.xlabel('清潔感', fontsize=12)
plt.ylabel('接客・サービス', fontsize=12)
plt.title('清潔感と接客・サービスの評価の関係', fontsize=14)
plt.tight_layout()
plt.show()

# 時期と風呂の散布図を描画
plt.figure(figsize=(10, 6))
sns.scatterplot(x='season', y='item_value', data=bath_sorted, hue='item_name')
plt.xlabel('時期', fontsize=12)
plt.ylabel('風呂', fontsize=12)
plt.title('時期と風呂の評価の関係', fontsize=14)
plt.tight_layout()
plt.show()


# 接続を閉じる
conn.close()