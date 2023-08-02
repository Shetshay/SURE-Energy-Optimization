const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 3000;
const WEATHER_API_KEY = '9c588b8e394a9797f8013e82ead2ca35';
const CALIFORNIAISO_API_KEY = 'YOUR_CALIFORNIAISO_API_KEY';

app.get('/temperature', async (req, res) => {
  try {
    const city = 'Bakersfield';
    const state = 'California';
    const weatherAPIUrl = `http://api.openweathermap.org/data/2.5/weather?q=${city},${state}&units=metric&appid=${WEATHER_API_KEY}`;

    const response = await axios.get(weatherAPIUrl);
    const temperature = response.data.main.temp;

    res.json({ temperature: temperature });
  } catch (error) {
    console.error('Error fetching temperature:', error.message);
    res.status(500).json({ error: 'Failed to fetch temperature data' });
  }
});

app.get('/energy-cost', async (req, res) => {
  try {
    const currentDate = new Date().toISOString().slice(0, 10);

    const response = await axios.get(`https://oasisapi.caiso.com/oasisapi/SingleZip?queryname=PRC_LMP&startdatetime=${currentDate}T00:00-0000&enddatetime=${currentDate}T23:59-0000&version=1&market_run_id=RTPD&node=ALL&resultformat=6&queryformat=JSON`, {
      headers: {
        'Authorization': `Bearer ${CALIFORNIAISO_API_KEY}`,
      },
    });

    const energyCostData = response.data;

    res.json(energyCostData);
  } catch (error) {
    console.error('Error fetching energy cost data:', error.message);
    res.status(500).json({ error: 'Failed to fetch energy cost data' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
