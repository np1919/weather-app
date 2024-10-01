"use client";

import { useEffect, useState } from 'react';
import axios from 'axios';

const cities = {
  'Toronto, Ontario, Canada': { latitude: 43.7, longitude: -79.42, timezone: 'America/Toronto' },
  'New York, New York, USA': { latitude: 40.71, longitude: -74.01, timezone: 'America/New_York' },
  'London, England': { latitude: 51.51, longitude: -0.13, timezone: 'Europe/London' },
  'Los Angeles, California, USA': { latitude: 34.05, longitude: -118.25, timezone: 'America/Los_Angeles' },
  'Tokyo, Japan': { latitude: 35.68, longitude: 139.76, timezone: 'Asia/Tokyo' },
  'Sydney, Australia': { latitude: -33.87, longitude: 151.21, timezone: 'Australia/Sydney' },
  'Moscow, Russia': { latitude: 55.76, longitude: 37.62, timezone: 'Europe/Moscow' },
  'Budapest, Hungary': { latitude: 47.5, longitude: 19.04, timezone: 'Europe/Budapest' },
  // Add more cities as needed. 
  // These could be held in a database, or integrated with an auto-complete/dropdown selection and an API lookup, but I wanted to keep this as simple as possible.  
};

export default function Home() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchTime, setFetchTime] = useState('');
  const [historicalData, setHistoricalData] = useState(null);
  const [isFetching, setIsFetching] = useState(true);
  const [intervalId, setIntervalId] = useState(null);
  const [storedReadings, setStoredReadings] = useState([]);
  const [showReadings, setShowReadings] = useState(false);
  const [flashMessage, setFlashMessage] = useState('');
  const [readingsVisible, setReadingsVisible] = useState(false);
  const [selectedCity, setSelectedCity] = useState('Toronto, Ontario, Canada');

  const fetchWeatherData = async () => {
    const { latitude, longitude } = cities[selectedCity];

    try {
        const response = await axios.get(
            `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true&daily=precipitation_sum`
        );

        // // Log the entire API response
        // console.log("Weather API Response:", response.data.current_weather);
        // console.log("Daily API Response:", response.data.daily);

        // Get the current weather
        const currentWeather = response.data.current_weather;

        // Extract today's precipitation sum (usually at index 0 for today)
        const precipitationSum = response.data.daily.precipitation_sum[0] || 0; // Default to 0 if no data

        // Set the state with current weather and precipitation sum
        setWeather({
            temperature: currentWeather.temperature,
            windspeed: currentWeather.windspeed,
            precipitation: precipitationSum, // Include today's precipitation sum
            time: currentWeather.time, // Add the time if needed
        });

        setLoading(false);
        setFetchTime(new Date().toLocaleString('en-US', { timeZone: cities[selectedCity].timezone }));
    } catch (error) {
        console.error("Error fetching weather data:", error);
        setLoading(false);
    }
};

  // todo: clean up redundant constants?
  const fetchHistoricalData = async () => {
    const today = new Date();
    const endDate = new Date(today);
    endDate.setDate(today.getDate() - 1);
    const formattedEndDate = endDate.toISOString().split('T')[0];
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - 6);
    const formattedStartDate = startDate.toISOString().split('T')[0];
    const { latitude, longitude, timezone } = cities[selectedCity];
    const response = await axios.get(
      `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&start_date=${formattedStartDate}&end_date=${formattedEndDate}&timezone=${timezone}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum`
    );
    const { time, temperature_2m_max, temperature_2m_min, precipitation_sum } = response.data.daily;
    // this operation could probably use some work. I'm a little unfamiliar with the data structures involved in the API request and storage. 
    setHistoricalData({
      time: time.reverse(),
      temperature_2m_max: temperature_2m_max.reverse(),
      temperature_2m_min: temperature_2m_min.reverse(),
      precipitation_sum: precipitation_sum.reverse(),
    });
  };

  useEffect(() => {
    if (isFetching) {
      fetchWeatherData();
      fetchHistoricalData();
      const id = setInterval(fetchWeatherData, 60000);
      setIntervalId(id);
      return () => clearInterval(id);
    }
  }, [isFetching, selectedCity]); // Fetch new data when city changes

  const handleToggleFetching = () => {
    setIsFetching(prev => !prev);
    if (isFetching && intervalId) {
      clearInterval(intervalId);
    }
  };

  const handleCityChange = (event) => {
    setSelectedCity(event.target.value);
    fetchHistoricalData(); // Fetch historical data for the new city
    fetchWeatherData();

  };

  const formatLocalTime = (utcTime) => {
    const date = new Date(utcTime + 'Z');
    const options = {
      timeZone: cities[selectedCity].timezone,
      hour: 'numeric',
      minute: 'numeric',
      second: 'numeric',
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
    };
    return date.toLocaleString('en-US', options);
  };

  // main "reading" fields
  const storeCurrentReading = () => {
    if (weather) {
      const currentReading = {
        temperature: weather.temperature,
        windspeed: weather.windspeed,
        precipitation: weather.precipitation ?? 0,
        time: fetchTime, // Use the last fetched time -- could be based on the last updated time, as given by the API. 
        location: selectedCity, // Store the selected city, so as to not rely on the current selection
      };
      const updatedReadings = [currentReading, ...storedReadings];
      setStoredReadings(updatedReadings.slice(0, 5));
      localStorage.setItem('weatherReadings', JSON.stringify(updatedReadings.slice(0, 5)));
      setFlashMessage('Current reading stored!');
      setTimeout(() => setFlashMessage(''), 2000);
    }
  };

  const loadRecentReadings = () => {
    const savedReadings = JSON.parse(localStorage.getItem('weatherReadings')) || [];
    setStoredReadings(savedReadings);
    setShowReadings(true);
    setReadingsVisible(true);
  };

  const hideRecentReadings = () => {
    setReadingsVisible(false);
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

      <div className="flex flex-row w-full justify-between">
        {/* Left Column for Historical Data */}
        <div className="w-1/3 flex flex-col justify-center">
          <h2 className="text-xl mb-2">Past 5 Days Weather for {selectedCity}</h2>
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
              <p>Last Updated (API): {formatLocalTime(weather?.time)}</p>
              <p>Last Fetched At: {fetchTime}</p>
              <p>Fetching: {isFetching ? 'Enabled' : 'Disabled'}</p>
            </div>
          )}

          {/* Actions Buttons */}
          <div className="mt-4 flex flex-row space-x-2">
            <button 
              className="bg-blue-500 text-white py-2 px-4 rounded"
              onClick={handleToggleFetching}
            >
              {isFetching ? 'Pause Fetching' : 'Resume Fetching'}
            </button>
            <button 
              className="bg-green-500 text-white py-2 px-4 rounded"
              onClick={storeCurrentReading}
            >
              Store Current Reading
            </button>
            <button 
              className="bg-green-500 text-white py-2 px-4 rounded"
              onClick={loadRecentReadings}
            >
              Show Recent Readings
            </button>
            {readingsVisible && (
              <button 
                className="bg-red-500 text-white py-2 px-4 rounded"
                onClick={hideRecentReadings}
              >
                Hide Recent Readings
              </button>
            )}
          </div>
        </div>

        {/* Right Column for Notifications and Recent Readings */}
        <div className="w-1/3 flex flex-col items-center justify-center">
          <div className="h-16">
            {flashMessage && (
              <div className="mt-2 p-2 bg-green-200 text-green-800 rounded">
                {flashMessage}
              </div>
            )}
          </div>

          {showReadings && readingsVisible && storedReadings.length > 0 && (
            <div>
              <h2 className="text-xl">Recent Temperature Readings</h2>
              {storedReadings.map((reading, index) => (
                <div key={index}>
                  <p>{reading.temperature}°C | {reading.precipitation} mm | {reading.windspeed} km/h | {reading.location} | {reading.time} (Local Time)
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
