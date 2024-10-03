from fastapi import FastAPI, HTTPException
import asyncio
import crud_utils, models, schemas
import datetime, requests
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
import pprint 

origins = [
    "http://localhost:3000",]  # Allows requests from this origin

# Create the database tables
models.Base.metadata.create_all(bind=engine)

# run the server
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
     
# custom caching/triage class
cache = crud_utils.LocalStore()


@app.get("/")
async def homepage():
    return {"message": "Welcome to the Weather API!"}


def get_all_data(city_id):
    ### api params
    latitude = cache.location_data[city_id]['latitude']
    longitude = cache.location_data[city_id]['longitude']
    timezone = cache.location_data[city_id]['timezone']
    # todo: these dates should be dependent on the city's timezone?
    formatted_start_date = (datetime.datetime.now() - datetime.timedelta(days=5)).date()
    formatted_end_date = (datetime.datetime.now() + datetime.timedelta(days=5)).date()
    
    OPEN_METEO_URL = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={formatted_start_date}&end_date={formatted_end_date}&timezone={timezone}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&current_weather=true"
    try:
        response = requests.get(OPEN_METEO_URL)
        response.raise_for_status() 
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching weather data: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing key in response data: {str(e)}")

    return response.json()


@app.get("/weather/fetch/{city_id}")
async def fetch_weather(city_id: int):
    """todo: 1. modify the singular API request, breaking it into pieces as async lookups
             2. make sure that the data has been refreshed or looked up correctly for each piece before storing to db?
             3. add unit testing
             """
    
    ### Branching logic, to separate API calls for immediate, past, and future data (and/or retrieve those data from db)

    if datetime.datetime.now() - cache.cache[city_id]['last_updated'] > datetime.timedelta(minutes=15):
        ### Cache stores a 'last_updated_at' value, which is instantiated on cache creation.
        ### When storing the last-updated-at value in the cache upon a new request (below), the value is rounded down to the previous 15 minute interval. 
        ### This hijinks is not confirmed by checking the time which comes out of the API... 
        weather_data = get_all_data(city_id)
        # return weather_data ## for testing api structure
        city = cache.location_data[city_id]['city'] 
        ## random integers are not the best unique identifier...should absolutely be sharing a single table with frontend and backend.
        ## data in the locations dictionary (cache) is not atomic -- locations have commas, some have province/state, others just city and country.
        ## latitude, longitude, and timezone work for all 8 of the included locations -- if more were added, set up a table.

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
        
        ### when performing a lookup, store all data in the cache.
        cache.cache[city_id]['current_weather'] = current_weather
        cache.cache[city_id]['historical_weather'] = historical_weather
        cache.cache[city_id]['future_weather'] = future_weather 
        cache.cache[city_id]['last_updated'] = crud_utils.round_down_minutes_to_last_15() ## round the current time down to the previous 15 minute interval.
        # pprint.pprint(cache.cache) ## for testing

    else: 
        ## if data has been looked up within the past 15 minutes, there's no need to hit the API again (we assume :())
        current_weather, historical_weather, future_weather = cache.cache[city_id]['current_weather'], cache.cache[city_id]['historical_weather'], cache.cache[city_id]['future_weather']
    
    # in any case, the most recent value (stored in cache) needs to be available to be recorded by the button-press event on the frontend
    cache.most_recent_reading = current_weather
    pprint.pprint(cache.cache) ## for testing
    pprint.pprint(cache.most_recent_reading) ## for testing
    return {"current_weather": current_weather, "historical_weather": historical_weather, "future_weather": future_weather}

  
@app.get("/readings/store")
async def store_weather():
    """writes the cached 'most_recent_reading' to the WeatherReading table in db"""
    # print('youre in the readings/store endpoint', cache.most_recent_reading) ## for testing
    reading = models.WeatherReading(**cache.most_recent_reading)
    #use backend server UTC time for consistency
    reading.time = datetime.datetime.utcnow()
    db = SessionLocal()
    db.add(reading)
    db.commit()
    db.refresh(reading)
    db.close() # todo: wrap these procedures ? use get_db with try/except/finally blocks?
    return reading # return the data you wrote to the db as json/dictionary (for testing) 


#Endpoint to read the (5) most recent readings
@app.get("/readings/fetch")
async def read_recent_readings(skip: int=0, limit: int = 5):
    """reads the WeatherReading table and returns a list of dictionaries
    todo: use the schemas.py pydantic models to verify data transactions between backend and frontend"""
    db = SessionLocal()
    readings = db.query(models.WeatherReading).order_by(models.WeatherReading.time.desc()).limit(limit).all()
    db.close()
    return readings


