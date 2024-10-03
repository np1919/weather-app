from sqlalchemy import Column, Integer, Float, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

# Weather model
class WeatherReading(declarative_base()):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    temperature = Column(Float)
    temperature_unit = Column(String)
    windspeed = Column(Float)
    windspeed_unit = Column(String)
    precipitation = Column(Float)
    precipitation_unit = Column(String)
    time = Column(DateTime)

# Historical 
class HistoricalWeatherReading(declarative_base()):
    __tablename__ = "historical_data"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    city = Column(String)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    temperature_unit = Column(String)
    precipitation = Column(Float)
    precipitation_unit = Column(String)

# Location
class LocationData(declarative_base()):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    timezone = Column(String)
