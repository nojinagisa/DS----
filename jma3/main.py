import flet as ft
from datetime import datetime
from weather_database import WeatherDatabase
from weather_api import WeatherAPI

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    # ウィンドウサイズの設定を修正
    page.window_width = 800  # 一時的に古い方法を使用
    page.window_height = 600  # 一時的に古い方法を使用
    page.padding = 20

    db = WeatherDatabase()
    api = WeatherAPI()

    dialog = ft.AlertDialog(
        content=ft.ProgressRing(),
    )
    page.overlay.append(dialog)  # 新しい方法でダイアログを追加

    def update_weather_display(area_name: str, area_code: str):
        """天気情報の表示を更新"""
        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog.content = ft.ProgressRing()
        dialog.open = True
        page.update()

        # APIからデータを取得
        raw_data = api.fetch_weather_data(area_code)
        if raw_data:
            weather_data_list = api.process_weather_data(raw_data, area_code, area_name)
            
            # データベースに保存
            for weather_data in weather_data_list:
                db.save_weather_data(weather_data)

            # カードの作成
            dialog.content = ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"{area_name}の天気", size=20, weight=ft.FontWeight.BOLD),
                            ]),
                            ft.Row([
                                ft.Column([
                                    ft.Row([
                                        ft.Image(
                                            src=f"https://www.jma.go.jp/bosai/forecast/img/{weather_data_list[0]['weather_code']}.svg",
                                            width=100,
                                            height=100,
                                        ),
                                        ft.Column([
                                            ft.Text(
                                                weather_data_list[0]['weather_description'],
                                                size=24,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            ft.Row([
                                                ft.Text(
                                                    f"気温：{weather_data_list[0]['temperature_min']}℃ / {weather_data_list[0]['temperature_max']}℃",
                                                    size=20,
                                                ),
                                            ]),
                                            ft.Text(
                                                f"降水確率：{weather_data_list[0]['precipitation_probability']}%",
                                                size=16,
                                            ),
                                        ]),
                                    ]),
                                ]),
                            ]),
                        ]),
                        padding=15,
                    ),
                ),
                ft.Row([
                    ft.TextButton(
                        "閉じる",
                        on_click=close_dialog
                    ),
                ], alignment=ft.MainAxisAlignment.END),
            ])
        else:
            dialog.content = ft.Text("天気情報の取得に失敗しました")

        dialog.open = True
        page.update()

    # 地域選択ボタンの作成
    buttons = [
        ["北海道", "016000"], ["青森", "020000"], ["岩手", "030000"],
        ["宮城", "040000"], ["秋田", "050000"], ["山形", "060000"],
        ["福島", "070000"], ["茨城", "080000"], ["栃木", "090000"],
        ["群馬", "100000"], ["埼玉", "110000"], ["千葉", "120000"],
        ["東京", "130000"], ["神奈川", "140000"], ["新潟", "150000"],
        ["富山", "160000"], ["石川", "170000"], ["福井", "180000"],
        ["山梨", "190000"], ["長野", "200000"], ["岐阜", "210000"],
        ["静岡", "220000"], ["愛知", "230000"], ["三重", "240000"],
        ["滋賀", "250000"], ["京都", "260000"], ["大阪", "270000"],
        ["兵庫", "280000"], ["奈良", "290000"], ["和歌山", "300000"],
        ["鳥取", "310000"], ["島根", "320000"], ["岡山", "330000"],
        ["広島", "340000"], ["山口", "350000"], ["徳島", "360000"],
        ["香川", "370000"], ["愛媛", "380000"], ["高知", "390000"],
        ["福岡", "400000"], ["佐賀", "410000"], ["長崎", "420000"],
        ["熊本", "430000"], ["大分", "440000"], ["宮崎", "450000"],
        ["鹿児島", "460100"], ["沖縄", "471000"]
    ]

    rows = []
    current_row = []
    
    for name, code in buttons:
        if len(current_row) == 8:  # 8ボタンごとに新しい行を作成
            rows.append(ft.Row(current_row, wrap=True))
            current_row = []
            
        current_row.append(
            ft.ElevatedButton(
                text=name,
                on_click=lambda e, name=name, code=code: update_weather_display(name, code)
            )
        )
    
    if current_row:  # 残りのボタンを追加
        rows.append(ft.Row(current_row, wrap=True))

    # メインコンテンツの配置
    title = ft.Text("天気予報", size=32, weight=ft.FontWeight.BOLD)
    subtitle = ft.Text("地域を選択してください", size=16)
    
    page.add(
        title,
        subtitle,
        *rows
    )

if __name__ == "__main__":
    ft.app(target=main)