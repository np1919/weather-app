from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime, pytz, requests
from fastapi.middleware.cors import CORSMiddleware

# Database setup
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

# Pydantic model for the weather data
class WeatherData(BaseModel):
    city: str
    temperature: float
    temperature_unit: str
    windspeed: float
    windspeed_unit: str
    precipitation: float
    precipitation_unit: str
    time: datetime.datetime

# City map
cities_map = {
    1: { "city": 'Toronto, Ontario, Canada', "latitude": 43.7, "longitude": -79.42, "timezone": 'America/Toronto' },
    2: { "city": 'New York, New York, USA', "latitude": 40.71, "longitude": -74.01, "timezone": 'America/New_York' },
    3: { "city": 'London, England', "latitude": 51.51, "longitude": -0.13, "timezone": 'Europe/London' },
    4: { "city": 'Los Angeles, California, USA', "latitude": 34.05, "longitude": -118.25, "timezone": 'America/Los_Angeles' },
    5: { "city": 'Tokyo, Japan', "latitude": 35.68, "longitude": 139.76, "timezone": 'Asia/Tokyo' },
    6: { "city": 'Sydney, Australia', "latitude": -33.87, "longitude": 151.21, "timezone": 'Australia/Sydney' },
    7: { "city": 'Moscow, Russia', "latitude": 55.76, "longitude": 37.62, "timezone": 'Europe/Moscow' },
    8: { "city": 'Budapest, Hungary', "latitude": 47.5, "longitude": 19.04, "timezone": 'Europe/Budapest' }
}

# Create the database tables
Base.metadata.create_all(bind=engine)
app = FastAPI()
origins = [
    "http://localhost:3000",  # Allows requests from this origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# def convert_time(utc_time: datetime.datetime, timezone: str):
#     local_tz = pytz.timezone(timezone)
#     return utc_time.astimezone(local_tz)

@app.post("/weather/store", response_model=WeatherData)
async def store_weather(data: WeatherData):
    print(data)  # Log the incoming data

    db = SessionLocal()
    reading = WeatherReading(
        city=data.city,
        temperature=data.temperature,
        temperature_unit=data.temperature_unit,
        windspeed=data.windspeed,
        windspeed_unit=data.windspeed_unit,
        precipitation=data.precipitation,
        precipitation_unit=data.precipitation_unit,
        time=data.time  # Ensure this is a valid datetime object
    )
    print(reading.__dict__)
    db.add(reading)
    db.commit()
    db.refresh(reading)
    db.close()
    return reading

# Endpoint to read the most recent readings
@app.get("/weather/readings", response_model=list[WeatherData])
async def read_recent_readings(limit: int = 5):
    db = SessionLocal()
    readings = db.query(WeatherReading).order_by(WeatherReading.time).limit(limit).all()
    db.close()
    return readings

@app.get("/")
async def homepage():
    return {"message": "Welcome to the Weather API!"}

@app.get("/weather/fetch/{city_id}")
async def fetch_weather(city_id: int):
    formatted_start_date = (datetime.datetime.now() - datetime.timedelta(days=5)).date()
    formatted_end_date = (datetime.datetime.now() + datetime.timedelta(days=5)).date()
    city = cities_map[city_id]['city']
    latitude = cities_map[city_id]['latitude']
    longitude = cities_map[city_id]['longitude']
    timezone = cities_map[city_id]['timezone']
    
    OPEN_METEO_URL = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={formatted_start_date}&end_date={formatted_end_date}&timezone={timezone}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&current_weather=true"

    try:
        response = requests.get(OPEN_METEO_URL)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching weather data: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing key in response data: {str(e)}")
    
    weather_data = response.json()
    # return weather_data
    current_weather = {
        "city": city,
        "temperature_unit": weather_data["current_weather_units"]["temperature"],
        "windspeed_unit": weather_data["current_weather_units"]["windspeed"],
        "precipitation_unit": weather_data['daily_units']['precipitation_sum'],

        "temperature": weather_data["current_weather"]["temperature"],
        "windspeed": weather_data["current_weather"]["windspeed"],
        "precipitation": weather_data["daily"]["precipitation_sum"][5],
        "time": weather_data["current_weather"]["time"],
        "timezone": weather_data['timezone'],
    }

    historical_weather = {
        'time': weather_data["daily"]["time"][:5],
        'temperature_2m_min': weather_data["daily"]["temperature_2m_min"][:5],
        'temperature_2m_max': weather_data["daily"]["temperature_2m_max"][:5],
        'precipitation_sum': weather_data["daily"]["precipitation_sum"][:5],
    }

    future_weather = {
        'time': weather_data["daily"]["time"][6:],
        'temperature_2m_min': weather_data["daily"]["temperature_2m_min"][6:],
        'temperature_2m_max': weather_data["daily"]["temperature_2m_max"][6:],
        'precipitation_sum': weather_data["daily"]["precipitation_sum"][6:],
    }

    # print(current_weather)
    
    return {"current_weather": current_weather, "historical_weather": historical_weather, "future_weather": future_weather}

  
