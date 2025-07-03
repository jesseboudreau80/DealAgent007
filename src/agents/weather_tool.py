
import requests
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    description: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float

def get_current_weather(city: str, api_key: str) -> WeatherResponse:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
    response = requests.get(url)
    data = response.json()

    return WeatherResponse(
        description=data['weather'][0]['description'],
        temperature=data['main']['temp'],
        feels_like=data['main']['feels_like'],
        humidity=data['main']['humidity'],
        wind_speed=data['wind']['speed']
    )
