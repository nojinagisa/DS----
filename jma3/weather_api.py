import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class WeatherAPI:
    BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast"

    @staticmethod
    def fetch_weather_data(area_code: str) -> Optional[Dict[str, Any]]:
        """気象庁APIから天気データを取得"""
        try:
            url = f"{WeatherAPI.BASE_URL}/{area_code}.json"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()[0]
        except Exception as e:
            print(f"API取得エラー: {e}")
            return None

    @staticmethod
    def process_weather_data(raw_data: Dict[str, Any], area_code: str, area_name: str) -> List[Dict[str, Any]]:
        """APIから取得した天気データを処理"""
        processed_data = []
        time_series = raw_data['timeSeries']
        
        weather_codes = time_series[0]['areas'][0]['weatherCodes']
        weathers = time_series[0]['areas'][0]['weathers']
        temps = time_series[2]['areas'][0]['temps']
        pops = time_series[1]['areas'][0]['pops'] if len(time_series) > 1 else []

        today = datetime.now()
        
        for i, (weather_code, weather) in enumerate(zip(weather_codes, weathers)):
            forecast_date = today + timedelta(days=i)
            
            weather_data = {
                'area_code': area_code,
                'area_name': area_name,
                'region_code': area_code[:2],
                'forecast_date': forecast_date.strftime('%Y-%m-%d'),
                'weather_code': weather_code,
                'weather_description': weather,
                'temperature_max': temps[i*2+1] if i*2+1 < len(temps) else None,
                'temperature_min': temps[i*2] if i*2 < len(temps) else None,
                'precipitation_probability': pops[i] if i < len(pops) else None
            }
            processed_data.append(weather_data)
            
        return processed_data