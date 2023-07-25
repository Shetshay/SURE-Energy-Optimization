const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 3000;
const API_KEY = '9c588b8e394a9797f8013e82ead2ca35';

app.get('/temperature', async (req, res) => {
  try {
    const city = 'Bakersfield';
    const state = 'California';
    const weatherAPIUrl = `http://api.openweathermap.org/data/2.5/weather?q=${city},${state}&units=metric&appid=${API_KEY}`;

    const response = await axios.get(weatherAPIUrl);
    const temperature = response.data.main.temp;

    res.json({ temperature: temperature });
  } catch (error) {
    console.error('Error fetching temperature:', error.message);
    res.status(500).json({ error: 'Failed to fetch temperature data' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

