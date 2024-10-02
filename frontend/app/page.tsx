"use client";

import { useEffect, useState } from 'react';
import axios from 'axios';

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
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchTime, setFetchTime] = useState('');
  const [historicalData, setHistoricalData] = useState(null);
  const [futureWeather, setFutureWeather] = useState(null);
  const [isFetching, setIsFetching] = useState(true);
  const [intervalId, setIntervalId] = useState(null);
  const [storedReadings, setStoredReadings] = useState([]);
  const [showReadings, setShowReadings] = useState(false);
  const [flashMessage, setFlashMessage] = useState('');
  const [readingsVisible, setReadingsVisible] = useState(false);
  const [selectedCity, setSelectedCity] = useState('Toronto, Ontario, Canada');

  interface WeatherData {
    city: string;
    temperature: number;
    temperature_unit: string;
    windspeed: number;
    windspeed_unit: string;
    precipitation: number;
    precipitation_unit: string;
    time: Date
  }

  const fetchWeatherData = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/weather/fetch/${cities[selectedCity].city_id}`);
  
      const { current_weather, historical_weather, future_weather } = response.data;
      
      const last_api_time = current_weather.time.toLocaleString('en-US', { timeZone: current_weather.timezone });
      setWeather({
        city: current_weather.city,
        temperature: current_weather.temperature,
        temperature_unit: current_weather.temperature_unit,
        windspeed: current_weather.windspeed,
        windspeed_unit: current_weather.windspeed_unit,
        precipitation: current_weather.precipitation,
        precipitation_unit: current_weather.precipitation_unit,
        time: last_api_time
      });
  
      setHistoricalData({
        time: historical_weather.time.reverse(),
        temperature_2m_max: historical_weather.temperature_2m_max.reverse(),
        temperature_2m_min: historical_weather.temperature_2m_min.reverse(),
        precipitation_sum: historical_weather.precipitation_sum.reverse(),
      });
  
      // Set future weather data
      setFutureWeather({
        time: future_weather.time,
        temperature_2m_min: future_weather.temperature_2m_min,
        temperature_2m_max: future_weather.temperature_2m_max,
        precipitation_sum: future_weather.precipitation_sum,
      });
  
      setFetchTime(new Date().toLocaleString('en-US', { timeZone: cities[selectedCity].timezone }));
      setLoading(false);
    } catch (error) {
      console.error("Error fetching weather data:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isFetching) {
      fetchWeatherData();
      const id = setInterval(fetchWeatherData, 60000);
      setIntervalId(id);
      return () => clearInterval(id);
    }
  }, [isFetching, selectedCity]);

  const handleToggleFetching = () => {
    setIsFetching(prev => !prev);
    if (isFetching && intervalId) {
      clearInterval(intervalId);
    }
  };

  const handleCityChange = (event) => {
    setSelectedCity(event.target.value);
    fetchWeatherData();
  };

  // const formatLocalTime = (localTime) => {
  //   const date = new Date(localTime);
  //   const options = {
  //     timeZone: cities[selectedCity].timezone,
  //     year: 'numeric',
  //     month: 'numeric',
  //     day: 'numeric',
  //     hour: 'numeric',
  //     minute: 'numeric',
  //     second: 'numeric',
  //     hour12: true,
  //   };
  //   return date.toLocaleString('en-US', options).replace(',', '');
  // };

  const hideRecentReadings = () => {
    setReadingsVisible(false);
  };

  const storeCurrentReading = () => {
    if (weather) {
      const currentReading = {
        city: weather.city,
        temperature: weather.temperature,
        windspeed: weather.windspeed,
        precipitation: weather.precipitation,
        time: weather.time,
        timezone : weather.timezone
      };
      const updatedReadings = [currentReading, ...storedReadings];
      setStoredReadings(updatedReadings.slice(0, 5));
      localStorage.setItem('weatherReadings', JSON.stringify(updatedReadings.slice(0, 5)));
      setFlashMessage('Current reading stored!');
      setTimeout(() => setFlashMessage(''), 999);
    }
  };

  const loadRecentReadings = () => {
    const savedReadings = JSON.parse(localStorage.getItem('weatherReadings')) || [];
    setStoredReadings(savedReadings);
    setShowReadings(true);
    setReadingsVisible(true);
  };

  const storeCurrentReadingDB = async () => {
    if (!weather) return;
    setFetchTime(new Date().toLocaleString('en-US', { timeZone: cities[selectedCity].timezone }));
    const reading: WeatherData = {
      city: weather.city,
      temperature: weather.temperature,
      temperature_unit: weather.temperature_unit,
      windspeed: weather.windspeed,
      windspeed_unit: weather.windspeed_unit,
      precipitation: weather.precipitation,
      precipitation_unit: weather.precipitation_unit, 
      time: fetchTime
    };
    // console.log("Weather Object:", weather);
    // console.log(reading);
    try {
      const response = await axios.post('http://127.0.0.1:8000/weather/store', reading);
      setFlashMessage('Current reading stored successfully!');
      setTimeout(() => setFlashMessage(''), 500);
      // fetchStoredReadings(); // Optionally fetch the updated readings
    } catch (error) {
      console.error("Error storing current reading:", error);
      setFlashMessage('Error storing reading. Please try again.');
    }
};

  const loadRecentReadingsDB = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/weather/readings');
      setStoredReadings(response.data);
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
              <p>Last Updated (API): {weather?.time}</p>
              <p>Last Fetched At: {fetchTime}</p>
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
                  {reading.city} | Temperature: {reading.temperature}°C | Wind Speed: {reading.windspeed} km/h | Precipitation: {reading.precipitation} mm | Recorded: {reading.time.replace("T", " ")} (Local Time)
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
