from pydantic import BaseModel
import datetime

class WeatherDataBase(BaseModel):
    city: str
    temperature: float
    temperature_unit: str
    windspeed: float
    windspeed_unit: str
    precipitation: float
    precipitation_unit: str
    time: datetime.datetime
    timezone: str
    class Config:
        from_attributes = True

# class HistoricalWeatherDataBase(BaseModel):
#     date : datetime.datetime
#     city: str
#     temperature_min: float
#     temperature_max : float
#     temperature_unit: str
#     precipitation: float
#     precipitation_unit: str

# class LocationBase(BaseModel):
#     city: str
#     latitude: float
#     longitude : float
#     timezone: str