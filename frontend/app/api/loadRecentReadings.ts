
export const loadRecentReadingsDB = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/weather/readings');
      setStoredReadings(response.data);
      setReadingsVisible(true);
    } catch (error) {
      console.error("Error loading recent readings:", error);
    }
  };
