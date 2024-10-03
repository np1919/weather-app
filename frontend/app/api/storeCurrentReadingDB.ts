
export const storeCurrentReadingDB = async () => {
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
