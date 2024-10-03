import pytz, datetime 
from sqlalchemy.orm import Session
import models, schemas

def round_down_minutes_to_last_15(my_dt=datetime.datetime.now()):
    now = my_dt
    minutes = now.minute
    rounded_minutes = minutes - (minutes %15)
    return now.replace(minute=rounded_minutes, second=0, microsecond=0) 

class LocalStore:
    def __init__(self):
        self.__most_recent_reading = None
        self.locations = dict()
        self.location_data = return_location_data()
        
        self.cache = dict()
        time_start = datetime.datetime.now() - datetime.timedelta(minutes=15)
        minutes = time_start.minute
        rounded_minutes = minutes - (minutes %15)
        last_update_cycle = time_start.replace(minute=rounded_minutes, second=0, microsecond=0)

        for city_id in self.location_data:
            # calculate the most recent update time
            self.cache[city_id] = {'last_updated':last_update_cycle}
                    # initialize a dict to store historical data for past and future
                    # This will indicate whether historical data (5 previous, 5 future) exists for a given city, for a given date 

    @property
    def most_recent_reading(self):
        return self.__most_recent_reading
    
    @most_recent_reading.setter
    def most_recent_reading(self, new):
        timezone = pytz.timezone(new['timezone'])
        if type(new['time']) == str:
            new['time'] = datetime.datetime.fromisoformat(new['time'])
        elif type(new['time'] == datetime.datetime):
            pass
        timezone.localize(new['time'])
        #assert type(new['time']) == datetime.datetime
        self.__most_recent_reading = new

        
# def create_locations(db:Session, ):

#     data = {1: { "city": 'Toronto, Ontario, Canada', "latitude": 43.7, "longitude": -79.42, "timezone": 'America/Toronto' },
#             2: { "city": 'New York, New York, USA', "latitude": 40.71, "longitude": -74.01, "timezone": 'America/New_York' },
#             3: { "city": 'London, England', "latitude": 51.51, "longitude": -0.13, "timezone": 'Europe/London' },
#             4: { "city": 'Los Angeles, California, USA', "latitude": 34.05, "longitude": -118.25, "timezone": 'America/Los_Angeles' },
#             5: { "city": 'Tokyo, Japan', "latitude": 35.68, "longitude": 139.76, "timezone": 'Asia/Tokyo' },
#             6: { "city": 'Sydney, Australia', "latitude": -33.87, "longitude": 151.21, "timezone": 'Australia/Sydney' },
#             7: { "city": 'Moscow, Russia', "latitude": 55.76, "longitude": 37.62, "timezone": 'Europe/Moscow' },
#             8: { "city": 'Budapest, Hungary', "latitude": 47.5, "longitude": 19.04, "timezone": 'Europe/Budapest' }
#             }
    
#     def create_location(stored_location, db=db, 
#                         skip:int=0, limit:int = 0):
#         # if len(db.query(models.LocationData).filter(models.LocationData.city == location['city']).first() > 0):
#         #     pass
#         # else:
#         location = models.LocationData(**stored_location)
#         db.add()
#         db.commit()
#         db.refresh()
#         return location

#     for stored_location in data:
#         create_location(stored_location)
#     return db.query(models.LocationData).offset(skip).limit(limit).all()


# def get_location(db:Session, location):
#     return db.query(models.LocationData).filter(models.LocationData.city == location['city']).first()

# City map
def return_location_data():
    return {1: { "city": 'Toronto, Ontario, Canada', "latitude": 43.7, "longitude": -79.42, "timezone": 'America/Toronto' },
            2: { "city": 'New York, New York, USA', "latitude": 40.71, "longitude": -74.01, "timezone": 'America/New_York' },
            3: { "city": 'London, England', "latitude": 51.51, "longitude": -0.13, "timezone": 'Europe/London' },
            4: { "city": 'Los Angeles, California, USA', "latitude": 34.05, "longitude": -118.25, "timezone": 'America/Los_Angeles' },
            5: { "city": 'Tokyo, Japan', "latitude": 35.68, "longitude": 139.76, "timezone": 'Asia/Tokyo' },
            6: { "city": 'Sydney, Australia', "latitude": -33.87, "longitude": 151.21, "timezone": 'Australia/Sydney' },
            7: { "city": 'Moscow, Russia', "latitude": 55.76, "longitude": 37.62, "timezone": 'Europe/Moscow' },
            8: { "city": 'Budapest, Hungary', "latitude": 47.5, "longitude": 19.04, "timezone": 'Europe/Budapest' }
            }



# def convert_time(utc_time: datetime.datetime, timezone: str):
#     """convert a naive datetime.datetime object to a timezone-aware object with timezone {timezone}
#     accepts: datetime.datetime object 
#              timezone (str)
#     returns:
#             datetime.datetime object"""
#     local_tz = pytz.timezone(timezone)
#     return utc_time.astimezone(local_tz)