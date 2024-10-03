import pytz, datetime 

class LocalHostCache:

    def __init__(self):
        self.__most_recent_reading = None
        self.location_data = return_location_data()
        # for cached API pulls: 
        self.cache = dict()
        time_start = datetime.datetime.now() - datetime.timedelta(minutes=15)  # calculate the most recent update time, push it back by 15 minutes
        last_update_cycle = time_start.replace(second=0, microsecond=0)
        for city_id in self.location_data:
            self.cache[city_id] = {'last_updated':last_update_cycle} # initialize a dict to cache current, historical, and future data
    
    @property
    def most_recent_reading(self):
        return self.__most_recent_reading
    
    @most_recent_reading.setter
    def most_recent_reading(self, new):
        """coerce API date-strings to datetime objects"""
        timezone = pytz.timezone(new['timezone'])
        if type(new['time']) == str:
            new['time'] = datetime.datetime.fromisoformat(new['time'])
        timezone.localize(new['time'])
        #assert type(new['time']) == datetime.datetime
        self.__most_recent_reading = new


def round_down_minutes_to_last_15(my_dt=datetime.datetime.now()):
    now = my_dt
    minutes = now.minute
    if minutes >= 0 and minutes <= 14:
        rounded_minutes = 0
    elif minutes >= 15 and minutes <= 29:
        rounded_minutes = 15
    elif minutes >= 30 and minutes <= 44:
        rounded_minutes = 30
    else:
        rounded_minutes = 45

    return now.replace(minute=rounded_minutes, second=0, microsecond=0) 

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