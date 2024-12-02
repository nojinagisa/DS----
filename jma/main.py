import flet as ft
import requests
import datetime
from datetime import timedelta

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.bgcolor = ft.colors.GREY_100

    def get_weather_info(area_code):
        url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data[0]
        except Exception as e:
            print(f"エラー: {e}")
            return None
        
    def close_dialog(e):
        page.dialog.open = False
        page.update()
    
    def show_weather_info(area_name, area_code):
        weather_data = get_weather_info(area_code)
        if weather_data:
            # 天気予報データの取得
            time_series = weather_data['timeSeries']
            weather_codes = time_series[0]['areas'][0].get('weatherCodes', [])  # 天気コードを取得
            weathers = time_series[0]['areas'][0]['weathers']
            temps = time_series[2]['areas'][0]['temps']
            pops = time_series[1]['areas'][0]['pops'] if len(time_series) > 1 else []

            # 日付の生成
            today = datetime.datetime.now()
            dates = [today + timedelta(days=i) for i in range(len(weathers))]


            # 天気予報カードの生成
            forecast_cards = []
            for i, (date, weather) in enumerate(zip(dates, weathers)):
                date_str = f"{date.month}/{date.day}({['月','火','水','木','金','土','日'][date.weekday()]})"
                
                temp_max = temps[i*2+1] if i*2+1 < len(temps) and temps[i*2+1] != "" else "--"
                temp_min = temps[i*2] if i*2 < len(temps) and temps[i*2] != "" else "--"

                pop = pops[i] if i < len(pops) else "--"
                weather_icon_url = f"https://www.jma.go.jp/bosai/forecast/img/{weather_codes[i]}.svg"

                forecast_cards.append(
                ft.Card( 
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(date_str, size=16, weight=ft.FontWeight.BOLD),
                            ft.Image(
                                src=weather_icon_url,
                                width=50,
                                height=50,
                            ),
                            ft.Text(weather, size=14),
                            ft.Row([
                                ft.Text(f"最高 {temp_max}℃", color="red", size=14),
                                ft.Text(" "),
                                ft.Text(f"最低 {temp_min}℃", color="blue", size=14),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Text(f"降水確率: {pop}%", size=14),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=10,
                        bgcolor=ft.colors.WHITE,
                    ),
                    width=150,
                )
            )

            page.dialog = ft.AlertDialog(
                title=ft.Text(area_name, size=20, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column([
                        ft.Row(
                            forecast_cards,
                            scroll=ft.ScrollMode.AUTO,
                            spacing=10,
                        ),
                    ]),
                    width=800,
                    height=300,
                ),
                actions=[
                    ft.TextButton("閉じる", on_click=close_dialog)
                ],
            )
            page.dialog.open = True
            page.update()
        else:
            page.dialog = ft.AlertDialog(
                title=ft.Text("エラー"),
                content=ft.Text("天気情報を取得できませんでした。"),
                actions=[
                    ft.TextButton("閉じる", on_click=close_dialog)
                ],
            )
            page.dialog.open = True
            page.update()

    def handle_expansion_tile_change(e):
        if e.data == 'true':
            message = "地域が展開されました"
        else:
            message = "地域が折りたたまれました"
        page.show_snack_bar(ft.SnackBar(content=ft.Text(message), duration=1000))

    content = [
        ft.ExpansionTile(
            title=ft.Text("東北地方(北海道を含める)"),
            subtitle=ft.Text("北海道、青森、岩手、秋田、宮城、山形、福島"),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.BLUE,
            text_color=ft.colors.BLUE,
            on_change=handle_expansion_tile_change,
            controls=[
                ft.ElevatedButton(
                    text="北海道",
                    on_click=lambda _: show_weather_info("北海道", "011000"),
                ),
                ft.ElevatedButton(
                    text="青森県",
                    on_click=lambda _: show_weather_info("青森県", "020000"),
                ),
                ft.ElevatedButton(
                    text="岩手県",
                    on_click=lambda _: show_weather_info("岩手県", "030000"),
                ),
                ft.ElevatedButton(
                    text="秋田県",
                    on_click=lambda _: show_weather_info("秋田県", "050000"),
                ),
                ft.ElevatedButton(
                    text="宮城県",
                    on_click=lambda _: show_weather_info("宮城県", "040000"),
                ),
                ft.ElevatedButton(
                    text="山形県",
                    on_click=lambda _: show_weather_info("山形県", "060000"),
                ),
                ft.ElevatedButton(
                    text="福島県",
                    on_click=lambda _: show_weather_info("福島県", "070000"),
                ),
            ]
        ),
        ft.ExpansionTile(
            title=ft.Text("関東地方"),
            subtitle=ft.Text("茨城、栃木、群馬、埼玉、千葉、東京、神奈川"),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.RED,
            text_color=ft.colors.RED,
            on_change=handle_expansion_tile_change,
            controls=[
                ft.ElevatedButton(
                    text="茨城県",
                    on_click=lambda _: show_weather_info("茨城県", "080000"),
                ),
                ft.ElevatedButton(
                    text="栃木県",
                    on_click=lambda _: show_weather_info("栃木県", "090000"),
                ),
                ft.ElevatedButton(
                    text="群馬県",
                    on_click=lambda _: show_weather_info("群馬県", "100000"),
                ),
                ft.ElevatedButton(
                    text="山梨県",
                    on_click=lambda _: show_weather_info("山梨県", "190000"),
                ),
                ft.ElevatedButton(
                    text="長野県",
                    on_click=lambda _: show_weather_info("長野県", "200000"),
                ),
                ft.ElevatedButton(
                    text="埼玉県",
                    on_click=lambda _: show_weather_info("埼玉県", "110000"),
                ), 
                ft.ElevatedButton(
                    text="千葉県",
                    on_click=lambda _: show_weather_info("千葉県", "120000"),
                ),  
                ft.ElevatedButton(
                    text="東京都",
                    on_click=lambda _: show_weather_info("東京都", "130000"),
                ),  
                ft.ElevatedButton(
                    text="神奈川県",
                    on_click=lambda _: show_weather_info("神奈川県", "140000"),
                ),   
            ]
        ),
        ft.ExpansionTile(
            title=ft.Text("東海地方"),
            subtitle=ft.Text("静岡、岐阜、愛知、三重"),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.LIGHT_BLUE,
            text_color=ft.colors.LIGHT_BLUE,
            on_change=handle_expansion_tile_change,
            controls=[
                ft.ElevatedButton(
                    text="静岡県",
                    on_click=lambda _: show_weather_info("静岡県", "220000"),
                ), 
                ft.ElevatedButton(
                    text="岐阜県",
                    on_click=lambda _: show_weather_info("岐阜県", "210000"),
                ),  
                ft.ElevatedButton(
                    text="愛知県",
                    on_click=lambda _: show_weather_info("愛知県", "230000"),
                ),  
                ft.ElevatedButton(
                    text="三重県",
                    on_click=lambda _: show_weather_info("三重県", "240000"),
                ),  
            ]
        ),
        ft.ExpansionTile(
            title=ft.Text("北陸地方"),
            subtitle=ft.Text("新潟、富山、石川、福井"),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.GREEN,
            text_color=ft.colors.GREEN,
            on_change=handle_expansion_tile_change,
            controls=[
                ft.ElevatedButton(
                    text="新潟県",
                    on_click=lambda _: show_weather_info("新潟県", "150000"),
                ),  
                ft.ElevatedButton(
                    text="富山県",
                    on_click=lambda _: show_weather_info("富山県", "160000"),
                ),  
                ft.ElevatedButton(
                    text="石川県",
                    on_click=lambda _: show_weather_info("石川県", "170000"),
                ),  
                ft.ElevatedButton(
                    text="福井県",
                    on_click=lambda _: show_weather_info("福井県", "180000"),
                ),  
            ]
        ),
        ft.ExpansionTile(
            title=ft.Text("近畿地方"),
            subtitle=ft.Text("滋賀、京都、奈良、和歌山、大阪、兵庫"),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.YELLOW,
            text_color=ft.colors.YELLOW,
            on_change=handle_expansion_tile_change,
            controls=[
                ft.ElevatedButton(
                    text="滋賀県",
                    on_click=lambda _: show_weather_info("滋賀県", "250000"),
                ),  
                ft.ElevatedButton(
                    text="京都府",
                    on_click=lambda _: show_weather_info("京都府", "260000"),
                ),  
                ft.ElevatedButton(
                    text="奈良県",
                    on_click=lambda _: show_weather_info("奈良県", "290000"),
                ),  
                ft.ElevatedButton(
                    text="和歌山県",
                    on_click=lambda _: show_weather_info("和歌山県", "300000"),
                ),  
                ft.ElevatedButton(
                    text="大阪県",
                    on_click=lambda _: show_weather_info("大阪県", "270000"),
                ),  
                ft.ElevatedButton(
                    text="兵庫県",
                    on_click=lambda _: show_weather_info("兵庫県", "280000"),
                ),  
            ]
        ),
        ft.ExpansionTile(
            title=ft.Text("中国地方"),
            subtitle=ft.Text("鳥取、島根、岡山、広島、山口"),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.PINK,
            text_color=ft.colors.PINK,
            on_change=handle_expansion_tile_change,
            controls=[
                ft.ElevatedButton(
                    text="鳥取県",
                    on_click=lambda _: show_weather_info("鳥取県", "310000"),
                ),  
                ft.ElevatedButton(
                    text="島根県",
                    on_click=lambda _: show_weather_info("島根県", "320000"),
                ),  
                ft.ElevatedButton(
                    text="岡山県",
                    on_click=lambda _: show_weather_info("岡山県", "330000"),
                ),  
                ft.ElevatedButton(
                    text="広島県",
                    on_click=lambda _: show_weather_info("広島県", "340000"),
                ),  
                ft.ElevatedButton(
                    text="山口県",
                    on_click=lambda _: show_weather_info("山口県", "350000"),
                ),  
            ]
        ),
        ft.ExpansionTile(
            title=ft.Text("四国地方"),
            subtitle=ft.Text("徳島、香川、愛媛、高知"),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.PURPLE,
            text_color=ft.colors.PURPLE,
            on_change=handle_expansion_tile_change,
            controls=[
                ft.ElevatedButton(
                    text="徳島県",
                    on_click=lambda _: show_weather_info("徳島県", "360000"),
                ),  
                ft.ElevatedButton(
                    text="香川県",
                    on_click=lambda _: show_weather_info("香川県", "370000"),
                ),  
                ft.ElevatedButton(
                    text="愛媛県",
                    on_click=lambda _: show_weather_info("愛媛県", "380000"),
                ),  
                ft.ElevatedButton(
                    text="高知県",
                    on_click=lambda _: show_weather_info("高知県", "390000"),
                ),  
            ]
        ),
        ft.ExpansionTile(
            title=ft.Text("九州地方(沖縄を含める)"),
            subtitle=ft.Text("福岡、佐賀、長崎、大分、熊本、宮崎、鹿児島、沖縄"),
            trailing=ft.Icon(ft.icons.ARROW_DROP_DOWN),
            collapsed_text_color=ft.colors.LIGHT_GREEN,
            text_color=ft.colors.LIGHT_GREEN,
            on_change=handle_expansion_tile_change,
            controls=[
                ft.ElevatedButton(
                    text="福岡県",
                    on_click=lambda _: show_weather_info("福岡県", "400000"),
                ),  
                ft.ElevatedButton(
                    text="佐賀県",
                    on_click=lambda _: show_weather_info("佐賀県", "410000"),
                ),  
                ft.ElevatedButton(
                    text="長崎県",
                    on_click=lambda _: show_weather_info("長崎県", "420000"),
                ),  
                ft.ElevatedButton(
                    text="大分県",
                    on_click=lambda _: show_weather_info("大分県", "440000"),
                ),  
                ft.ElevatedButton(
                    text="熊本県",
                    on_click=lambda _: show_weather_info("熊本県", "430000"),
                ),  
                ft.ElevatedButton(
                    text="宮崎県",
                    on_click=lambda _: show_weather_info("宮崎県", "450000"),
                ),  
                ft.ElevatedButton(
                    text="鹿児島県",
                    on_click=lambda _: show_weather_info("鹿児島県", "460100"),
                ),  
                ft.ElevatedButton(
                    text="沖縄県",
                    on_click=lambda _: show_weather_info("沖縄県", "471000"),
                ),  
            ]
        ),
    ]

#スクロールができるようにする
    page.add(
        ft.ListView(
            expand = True,
            controls=content,
            )
        )
ft.app(main)
