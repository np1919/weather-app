from pydantic import BaseModel
import datetime

# Pydantic model for the weather data
class WeatherDataBase(BaseModel):
    city: str
    temperature: float
    temperature_unit: str
    windspeed: float
    windspeed_unit: str
    precipitation: float
    precipitation_unit: str
    time: datetime.datetime

# # Pydantic model for Historical weather data
class HistoricalWeatherDataBase(BaseModel):
    date : datetime.datetime
    city: str
    temperature_min: float
    temperature_max : float
    temperature_unit: str
    precipitation: float
    precipitation_unit: str

# Model for Location
class LocationBase(BaseModel):
    city: str
    latitude: float
    longitude : float
    timezone: str