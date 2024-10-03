from fastapi import FastAPI, HTTPException
from models import WeatherDataBase
from schemas import WeatherReading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import datetime, requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.declarative import declarative_base
from utility_functions import return_location_data


# Database setup
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)

# Create the database tables
app = FastAPI()


origins = [
    "http://localhost:3000",]  # Allows requests from this origin

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# @app.post("/weather/store", response_model=WeatherData)
# async def store_weather(data: WeatherData):

# """ 
# 
# 
# 
#           function to post 'event' to database -- for live streaming, run through kafka or another message queue for persistence? 
# 
# 
# 
# 
#                   """

#     # print(data)  # Log the incoming data
#     db = SessionLocal()
#     reading = WeatherReading(
#         city=data.city,
#         temperature=data.temperature,
#         temperature_unit=data.temperature_unit,
#         windspeed=data.windspeed,
#         windspeed_unit=data.windspeed_unit,
#         precipitation=data.precipitation,
#         precipitation_unit=data.precipitation_unit,
#         time=data.time  # Ensure this is a valid datetime object
#     )
#     # print(reading.__dict__)
#     db.add(reading)
#     db.commit()
#     db.refresh(reading)
#     db.close()
#     return reading

# Endpoint to read the most recent readings
# @app.get("/weather/readings", response_model=list[WeatherData])
# async def read_recent_readings(limit: int = 5):
#   """   
#   
#   grab most recent five requests from the database (which could grow to be larger than the frontend local storage -- but is excessive/duplicated without the caching layer)
# 
#     """
#     db = SessionLocal()
#     readings = db.query(WeatherReading).order_by(WeatherReading.time).limit(limit).all()
#     db.close()
#     return readings


@app.get("/")
async def homepage():
    return {"message": "Welcome to the Weather API!"}


@app.get("/weather/fetch/{city_id}")
async def fetch_weather(city_id: int):
    """todo: 1. implement request triage based on whether data is available already; 
                a. cache "live data" within API refresh timeframe to prevent excessive API requests (could be similar to the 'refresh' functionality in frontend, as well?)
                b. store historical data in database -- look up by..?? request date, local time? execute an API call for 1 day of data, in a persistent db store?
                c. for a persistent data store of locations (as opposed to using an API, which would be superior), map correctly with frontend
             
            2. modify the singular API request, breaking it into pieces as async lookups
                a. make sure that the data has been refreshed or looked up correctly for each piece before storing to db
             """
    
    cities_map = return_location_data()
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

  
