import axios from 'axios';
import { cities } from '../data/constants';

export const fetchWeatherData = async (city: string) => {
  const response = await axios.get(`http://127.0.0.1:8000/weather/fetch/${cities[city].city_id}`);
  return response.data;
};