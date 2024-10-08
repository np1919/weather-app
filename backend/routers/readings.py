from fastapi import APIRouter, Request
from models import WeatherReading
from main import SessionLocal, datetime
  
router = APIRouter(prefix='/readings')

# @router.get("/store")
# async def store_weather():
#     """writes the cached 'most_recent_reading' to the WeatherReading table in db"""
#     # print('youre in the readings/store endpoint', cache.most_recent_reading) ## for testing
#     reading = models.WeatherReading(**cache.most_recent_reading)
#     #use backend server UTC time for consistency
#     reading.time = datetime.datetime.utcnow()
#     db = SessionLocal()
#     db.add(reading)
#     db.commit()
#     db.refresh(reading)
#     db.close() # todo: wrap these procedures ? use get_db with try/except/finally blocks?
#     return reading # return the data you wrote to the db as json/dictionary (for testing) 

@router.post("/store", response_model=dict) ## more to learn about serialization? authentication?
async def store_weather(reading:Request):
    """writes the POSTed data packet to WeatherReading table in db"""
    # print('youre in the readings/store endpoint', cache.most_recent_reading) ## for testing
    # print(reading)
    request_data = await reading.json()
    # print(request_data)
    reading = WeatherReading(**request_data)
    # #use backend server UTC time for consistency
    reading.time = datetime.datetime.utcnow()
    db = SessionLocal()
    db.add(reading)
    db.commit()
    db.refresh(reading)
    db.close() # todo: wrap these procedures ? use get_db with try/except/finally blocks?
    return request_data # returning the data you wrote to the db as a json/dictionary?



#Endpoint to read the (5) most recent readings
@router.get("/fetch")
async def read_recent_readings(skip: int=0, limit: int = 5):
    """reads the WeatherReading table and returns a list of dictionaries
    todo: use the schemas.py pydantic models to verify data transactions between backend and frontend"""
    db = SessionLocal()
    readings = db.query(WeatherReading).order_by(WeatherReading.time.desc()).limit(limit).all()
    db.close()
    return readings
