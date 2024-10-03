import pytz, datetime 

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