"use client";

import { useEffect, useState } from 'react';
import axios from 'axios';

// temporary data storage...
const cities = {
  'Toronto, Ontario, Canada': { city_id: 1, latitude: 43.7, longitude: -79.42, timezone: 'America/Toronto' },
  'New York, New York, USA': { city_id: 2, latitude: 40.71, longitude: -74.01, timezone: 'America/New_York' },
  'London, England': { city_id: 3, latitude: 51.51, longitude: -0.13, timezone: 'Europe/London' },
  'Los Angeles, California, USA': { city_id: 4, latitude: 34.05, longitude: -118.25, timezone: 'America/Los_Angeles' },
  'Tokyo, Japan': { city_id: 5, latitude: 35.68, longitude: 139.76, timezone: 'Asia/Tokyo' },
  'Sydney, Australia': { city_id: 6, latitude: -33.87, longitude: 151.21, timezone: 'Australia/Sydney' },
  'Moscow, Russia': { city_id: 7, latitude: 55.76, longitude: 37.62, timezone: 'Europe/Moscow' },
  'Budapest, Hungary': { city_id: 8, latitude: 47.5, longitude: 19.04, timezone: 'Europe/Budapest' }
};

export default function Home() {
  // data
  const [weather, setWeather] = useState(null);
  const [fetchTime, setFetchTime] = useState('');
  const [historicalData, setHistoricalData] = useState(null);
  const [futureWeather, setFutureWeather] = useState(null);
  // frontend states
  const [selectedCity, setSelectedCity] = useState('Toronto, Ontario, Canada');
  const [loading, setLoading] = useState(true);
  const [isFetching, setIsFetching] = useState(true);
  const [readingsVisible, setReadingsVisible] = useState(false);
  // flash message states
  const [intervalId, setIntervalId] = useState(null);
  const [flashMessage, setFlashMessage] = useState('');
  // these should be called up from the backend
  const [storedReadings, setStoredReadings] = useState([]);
  const [showReadings, setShowReadings] = useState(false);



  // this function to be broken into pieces?
  const fetchWeatherData = async () => {
    try {
      // execute data request to the backend
      const response = await axios.get(`http://127.0.0.1:8000/weather/fetch/${cities[selectedCity].city_id}`);
      // unpack the response (tuple?? dictionary.)
      const { current_weather, historical_weather, future_weather } = response.data;
      // "Last Updated At" time -- when the API was last updated. Caching triage could exist in frontend?
      const last_api_time = current_weather.time.toLocaleString('en-US', { timeZone: current_weather.timezone });
      // "Last Fetched At" time -- when data was fetched.
      setFetchTime(new Date().toLocaleString('en-US', { timeZone: 'UTC' }));

      // assign the unpacked data. If historical data has been looked up once, it should not need to be looked up again.
      setWeather({
        city: current_weather.city,
        temperature: current_weather.temperature,
        temperature_unit: current_weather.temperature_unit,
        windspeed: current_weather.windspeed,
        windspeed_unit: current_weather.windspeed_unit,
        precipitation: current_weather.precipitation,
        precipitation_unit: current_weather.precipitation_unit,
        // log the time that the api was last updated, in the current snapshot
        time: last_api_time,
        timezone: current_weather.timezone,
      });
      setHistoricalData({
        time: historical_weather.time.reverse(),
        temperature_2m_max: historical_weather.temperature_2m_max.reverse(),
        temperature_2m_min: historical_weather.temperature_2m_min.reverse(),
        precipitation_sum: historical_weather.precipitation_sum.reverse(),
      });
      setFutureWeather({
        time: future_weather.time,
        temperature_2m_min: future_weather.temperature_2m_min,
        temperature_2m_max: future_weather.temperature_2m_max,
        precipitation_sum: future_weather.precipitation_sum,
      });

      setLoading(false);
    } catch (error) {
      console.error("Error fetching weather data:", error);
      setLoading(false);
    }
  };


  useEffect(() => {
    if (isFetching) {
      // when true: fetch weather data. 
      fetchWeatherData();
      // initiate an interval, after which the data will be refreshed after 60 seconds.
      const id = setInterval(fetchWeatherData, 60000);
      setIntervalId(id);
      return () => clearInterval(id);
    }
  }, [isFetching, selectedCity]);


  const handleToggleFetching = () => {
    setIsFetching(prev => !prev)};

  const handleCityChange = (event) => {
    setSelectedCity(event.target.value)
  };
  
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
  
    // Get individual parts of the date
    const month = date.getMonth() + 1;  // getMonth is zero-based
    const day = date.getDate();
    const year = date.getFullYear();
  
    // Get hours, minutes, and seconds
    let hours = date.getHours();
    const minutes = date.getMinutes();
    const seconds = date.getSeconds();
  
    // Determine AM/PM
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;  // Convert 24-hour to 12-hour format, adjust 0-hour to 12
  
    // Format the date and time parts
    const formattedDate = `${month}/${day}/${year}, ${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')} ${ampm}`;
  
    return formattedDate;
  };

  const hideRecentReadings = () => {
    setReadingsVisible(false);
  };


  const storeCurrentReading = async () => {
    if (weather) {
      if (weather.city == selectedCity) {
        try {
          // const response = await axios.get('http://127.0.0.1:8000/readings/store');
          const response = await axios.post('http://127.0.0.1:8000/readings/store', {
              city: weather.city,
              temperature: weather.temperature,
              temperature_unit: weather.temperature_unit,
              windspeed: weather.windspeed,
              windspeed_unit: weather.windspeed_unit,
              precipitation: weather.precipitation,
              precipitation_unit: weather.precipitation_unit,
              // log the time that the api was last updated, in the current snapshot
              time: fetchTime,
              timezone: weather.timezone
          });
          setFlashMessage('Current reading stored!');
          setTimeout(() => setFlashMessage(''), 999);

          if (readingsVisible) {
            loadRecentReadings()
          }
      } catch (error) {
        console.error("Error loading recent readings:", error);
      }
    }
   }
  };

  const loadRecentReadings = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/readings/fetch');
      setStoredReadings(response.data);
      // setShowReadings(true);
      setReadingsVisible(true);
    } catch (error) {
      console.error("Error loading recent readings:", error);
    }
  };


  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 px-16">
      <h1 className="text-4xl font-bold mb-4">Weather App</h1>
      
      {/* City Selection Dropdown */}
      <select value={selectedCity} onChange={handleCityChange} className="mb-4 p-2 border border-gray-400 rounded">
        {Object.keys(cities).map((city) => (
          <option key={city} value={city}>{city}</option>
        ))}
      </select>
  
      <div className="flex flex-row w-full">
        {/* Left Column for Historical Data */}
        <div className="w-1/3 flex flex-col justify-center text-center">
          <h2 className="text-xl mb-2">Past 5 Days in {selectedCity}</h2>
          {historicalData && historicalData.temperature_2m_max.map((maxTemp, index) => (
            <div key={index} className="mb-1">
              <p>
                {historicalData.time[index]} | High: {maxTemp}°C | Low: {historicalData.temperature_2m_min[index]}°C | Precipitation: {historicalData.precipitation_sum[index]} mm
              </p>
            </div>
          ))}
        </div>
  
        {/* Center Column for Current Weather */}
        <div className="w-1/3 flex flex-col items-center justify-center">
          <h2 className="text-xl">Current Weather</h2>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <div className="text-center">
              <p>Location: {selectedCity}</p>
              <p>Temperature: {weather?.temperature}°C</p> 
              <p>Wind Speed: {weather?.windspeed} km/h</p>
              <p>Precipitation: {weather?.precipitation ?? 0} mm</p>
              <p>Last Updated: {formatDate(weather?.time)} (Local Time)</p>
              <p>Last Fetched At: {fetchTime} (UTC)</p>
              <p>Fetching: {isFetching ? 'Enabled' : 'Disabled'}</p>
              {flashMessage && <p className="text-green-500">{flashMessage}</p>}
            </div>
          )}
  
          {/* Actions Buttons */}
          <div className="mt-4 flex flex-row space-x-2">
            <button className="bg-blue-500 text-white py-2 px-4 rounded" onClick={handleToggleFetching}>
              {isFetching ? 'Pause Fetching' : 'Resume Fetching'}
            </button>
            <button className="bg-green-500 text-white py-2 px-4 rounded" onClick={storeCurrentReading}>
              Store Current Reading
            </button>
            <button className="bg-green-500 text-white py-2 px-4 rounded" onClick={loadRecentReadings}>
              Show Recent Readings
            </button>
            {readingsVisible && (
              <button className="bg-red-500 text-white py-2 px-4 rounded" onClick={hideRecentReadings}>
                Hide Recent Readings
              </button>
            )}
          </div>
        </div>
  
        {/* Right Column for Upcoming Weather Forecast */}
        <div className="w-1/3 flex flex-col justify-center text-center">
          <h2 className="text-xl mb-2">5 Day Forecast</h2>
          {futureWeather && futureWeather.temperature_2m_max.map((maxTemp, index) => (
            <div key={index} className="mb-1">
              <p>
                {futureWeather.time[index]} | High: {maxTemp}°C | Low: {futureWeather.temperature_2m_min[index]}°C | Precipitation: {futureWeather.precipitation_sum[index]} mm
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Readings Display */}
      {readingsVisible && (
        <div className="mt-4">
          <h2 className="text-xl text-center">5 Most Recent Weather Snapshots</h2>
          {storedReadings.length === 0 ? (
            <p>No readings stored.</p>
          ) : (
            <ul>
              {storedReadings.map((reading, index) => (
                <li key={index} className="mb-1">
                  {reading.city} | Temperature: {reading.temperature}°C | Wind Speed: {reading.windspeed} km/h | Precipitation: {reading.precipitation} mm | Recorded: {reading.time.replace("T", " ")} (UTC)
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
