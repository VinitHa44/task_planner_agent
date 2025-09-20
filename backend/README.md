# AI Task Planning Agent

An intelligent task planning agent that converts natural language goals into structured, actionable plans with external data enrichment using Google's Gemini 2.5 Pro.

## Features

- **Natural Language Processing**: Accepts goals in plain English
- **AI-Powered Planning**: Uses Google Gemini 2.5 Pro to break down goals into actionable steps
- **External Data Integration**: 
  - Weather API for contextual information
  - Web search for places, restaurants, and activities
- **Database Storage**: MongoDB for persistent plan storage
- **RESTful API**: FastAPI-based API for all operations

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Database Setup**:
   ```bash
   # Make sure MongoDB is running
   python setup.py
   ```

4. **Run the Application**:
   ```bash
   python run.py
   ```

## API Endpoints

- `POST /plans` - Create a new plan from a goal
- `GET /plans` - Get all plans
- `GET /plans/{id}` - Get a specific plan
- `PUT /plans/{id}` - Update a plan
- `DELETE /plans/{id}` - Delete a plan
- `GET /health` - Health check

## Example Usage

```python
import requests

# Create a new plan
response = requests.post("http://localhost:8000/plans", json={
    "goal": "Plan a 3-day trip to Jaipur with cultural highlights and good food"
})

plan = response.json()
print(f"Created plan: {plan['id']}")
```

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (get from https://makersuite.google.com/app/apikey)
- `MONGODB_URL`: MongoDB connection string
- `WEATHER_API_KEY`: OpenWeatherMap API key
- `WEB_SEARCH_API_KEY`: SerpAPI key for web search

## Getting Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Add it to your `.env` file as `GEMINI_API_KEY`

