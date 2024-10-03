from database import Base
from sqlalchemy import Column, Integer, Float, String, DateTime

# Weather model
class WeatherReading(Base):
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
    timezone = Column(String)

# # Historical 
# class HistoricalWeatherReading(Base):
#     __tablename__ = "historical_data"
#     id = Column(Integer, primary_key=True, index=True)
#     date = Column(DateTime)
#     city = Column(String)
#     temperature_min = Column(Float)
#     temperature_max = Column(Float)
#     temperature_unit = Column(String)
#     precipitation = Column(Float)
#     precipitation_unit = Column(String)

# # Location
# class LocationData(Base):
#     __tablename__ = "locations"
#     id = Column(Integer, primary_key=True, index=True)
#     city = Column(String)
#     latitude = Column(Float)
#     longitude = Column(Float)
#     timezone = Column(String)
