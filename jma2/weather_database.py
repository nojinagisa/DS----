import sqlite3
from datetime import datetime
import threading
from typing import Dict, Any

class WeatherDatabase:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.db_name = "weather.db"
        self._create_tables()

    def _create_tables(self):
        """データベーステーブルの作成"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # 地方マスターテーブル
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS regions (
                region_code TEXT PRIMARY KEY,
                region_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # 地域マスターテーブル
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS areas (
                area_code TEXT PRIMARY KEY,
                area_name TEXT NOT NULL,
                region_code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (region_code) REFERENCES regions (region_code)
            )
            ''')

            # 天気種別マスターテーブル
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_types (
                weather_code TEXT PRIMARY KEY,
                weather_description TEXT NOT NULL,
                icon_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # 天気予報テーブル
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT,
                forecast_date DATE,
                weather_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (area_code) REFERENCES areas (area_code),
                FOREIGN KEY (weather_code) REFERENCES weather_types (weather_code),
                UNIQUE (area_code, forecast_date)
            )
            ''')

            # 気温テーブル
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                forecast_id INTEGER,
                temperature_type TEXT CHECK (temperature_type IN ('max', 'min')),
                temperature INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (forecast_id) REFERENCES weather_forecasts (id)
            )
            ''')

            # 降水確率テーブル
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS precipitation_probabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                forecast_id INTEGER,
                probability INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (forecast_id) REFERENCES weather_forecasts (id)
            )
            ''')

            conn.commit()

    def save_weather_data(self, weather_data: Dict[str, Any]) -> bool:
        """天気データの保存"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                # 地域情報の保存/更新
                cursor.execute('''
                INSERT OR REPLACE INTO areas (area_code, area_name, region_code)
                VALUES (?, ?, ?)
                ''', (
                    weather_data['area_code'],
                    weather_data['area_name'],
                    weather_data['region_code']
                ))

                # 天気種別の保存/更新
                cursor.execute('''
                INSERT OR REPLACE INTO weather_types (weather_code, weather_description, icon_path)
                VALUES (?, ?, ?)
                ''', (
                    weather_data['weather_code'],
                    weather_data['weather_description'],
                    f"https://www.jma.go.jp/bosai/forecast/img/{weather_data['weather_code']}.svg"
                ))

                # 天気予報の保存
                cursor.execute('''
                INSERT OR REPLACE INTO weather_forecasts (area_code, forecast_date, weather_code)
                VALUES (?, ?, ?)
                ''', (
                    weather_data['area_code'],
                    weather_data['forecast_date'],
                    weather_data['weather_code']
                ))

                forecast_id = cursor.lastrowid

                # 気温の保存
                if weather_data.get('temperature_max'):
                    cursor.execute('''
                    INSERT INTO temperatures (forecast_id, temperature_type, temperature)
                    VALUES (?, 'max', ?)
                    ''', (forecast_id, weather_data['temperature_max']))

                if weather_data.get('temperature_min'):
                    cursor.execute('''
                    INSERT INTO temperatures (forecast_id, temperature_type, temperature)
                    VALUES (?, 'min', ?)
                    ''', (forecast_id, weather_data['temperature_min']))

                # 降水確率の保存
                if weather_data.get('precipitation_probability'):
                    cursor.execute('''
                    INSERT INTO precipitation_probabilities (forecast_id, probability)
                    VALUES (?, ?)
                    ''', (forecast_id, weather_data['precipitation_probability']))

                conn.commit()
                return True

            except Exception as e:
                print(f"データベース保存エラー: {e}")
                conn.rollback()
                return False

    def get_weather_forecast(self, area_code: str, date: str) -> Dict[str, Any]:
        """天気予報データの取得"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            query = """
            SELECT 
                a.area_name,
                wf.forecast_date,
                wt.weather_description,
                wt.icon_path,
                t_max.temperature as max_temp,
                t_min.temperature as min_temp,
                pp.probability as rain_probability,
                wf.updated_at
            FROM weather_forecasts wf
            JOIN areas a ON wf.area_code = a.area_code
            JOIN weather_types wt ON wf.weather_code = wt.weather_code
            LEFT JOIN temperatures t_max ON wf.id = t_max.forecast_id 
                AND t_max.temperature_type = 'max'
            LEFT JOIN temperatures t_min ON wf.id = t_min.forecast_id 
                AND t_min.temperature_type = 'min'
            LEFT JOIN precipitation_probabilities pp ON wf.id = pp.forecast_id
            WHERE wf.area_code = ? AND wf.forecast_date = ?
            """
            
            cursor.execute(query, (area_code, date))
            result = cursor.fetchone()
            
            if result:
                return {
                    'area_name': result[0],
                    'forecast_date': result[1],
                    'weather_description': result[2],
                    'icon_path': result[3],
                    'temperature_max': result[4],
                    'temperature_min': result[5],
                    'precipitation_probability': result[6],
                    'updated_at': result[7]
                }
            return None