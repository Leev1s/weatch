import requests
import os
import time


class QWeatherAPI:
    def __init__(self, key, free_subscription=False):
        self.key = key
        self.base_url = (
            "https://devapi.qweather.com/v7/weather/now"
            if free_subscription
            else "https://api.qweather.com/v7/weather/now"
        )

    def get_weather(self, location, lang=None, unit=None):
        params = {
            "key": self.key,
            "location": location,
        }
        if lang:
            params["lang"] = lang
        if unit:
            params["unit"] = unit
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


def send_webhook(message):
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise ValueError(
            "Webhook URL not found. Please set WEBHOOK_URL in your .env file."
        )

    requests.get(webhook_url + message)


# 示例用法
if __name__ == "__main__":
    api_key = os.getenv("QWEATHER_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Please set QWEATHER_API_KEY in your .env file."
        )

    location = os.getenv("QWEATHER_API_LOCATION")
    if not location:
        raise ValueError(
            "Location not found. Please set QWEATHER_API_LOCATION in your .env file."
        )

    lang = "zh"
    unit = "m"
    weather_api = QWeatherAPI(api_key, free_subscription=True)
    last_text = None
    while True:
        try:
            weather_data = weather_api.get_weather(location, lang, unit)
            weather_detail = weather_data.get("now", {})
            current_weather = weather_detail.get("text")
            if current_weather and current_weather != last_text:
                last_text = current_weather
                send_webhook(
                    "天气变化："
                    + str(current_weather)
                    + str(weather_detail.get("temp"))
                    + "℃"
                )
                print(f"Weather changed: {weather_detail}")
            else:
                print(f"{weather_detail}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        time.sleep(120)
