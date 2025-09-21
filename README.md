# 🤖 AI Task Planning Agent

An intelligent task planning system that converts natural language goals into structured, actionable travel plans with real-time weather data and external information enrichment using Google's Gemini AI.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)


## 🔍 Trip Logging System
![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green.svg)

## 🌟 Features

### 🎯 Core Capabilities
- **Natural Language Processing**: Accepts travel goals in plain English
- **AI-Powered Planning**: Uses Google Gemini 2.0 Flash for intelligent plan generation
- **Weather-Smart Planning**: Integrates real-time weather data for activity optimization
- **External Data Enrichment**: Web search for places, restaurants, and attractions
- **Trip-Specific Logging**: Individual log files for each trip planning request

### 🔧 Technical Features
- **Multi-Layer Architecture**: Clean separation with controllers, use cases, services, and repositories
- **Dependency Injection**: FastAPI's dependency injection for testable, maintainable code
- **Async Operations**: Full async/await support for optimal performance
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **RESTful API**: Well-structured API endpoints with proper HTTP status codes

### 🎨 Frontend Features
- **Modern React UI**: Built with React 18 + TypeScript
- **Responsive Design**: Mobile-first responsive design using Tailwind CSS
- **Component Library**: Shadcn/ui components for consistent UI/UX
- **Real-time Updates**: Dynamic plan display with loading states
- **Error Notifications**: User-friendly error messages with retry functionality

## 🏗️ Architecture

```
task_planning_agent/
├── backend/                    # FastAPI Backend
│   ├── controllers/           # Request/Response handling
│   ├── usecases/             # Business logic
│   ├── services/             # External services (AI, APIs)
│   ├── repositories/         # Data access layer
│   ├── models/               # Domain models and schemas
│   ├── utils/                # Utilities (logging, error handling)
│   ├── config/               # Configuration and database
│   ├── routers/              # API route definitions
│   └── logs/                 # Trip-specific log files
│       └── trips/            # Individual trip logs
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   ├── hooks/           # Custom React hooks
│   │   ├── types/           # TypeScript types
│   │   └── utils/           # Frontend utilities
│   └── public/              # Static assets
├── .env                      # Environment variables
├── .env.example             # Environment template
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 18+**
- **MongoDB** (local or cloud)
- **API Keys** (Google Gemini, OpenWeatherMap, SerpAPI)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd task_planning_agent
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
notepad .env  # On Windows
# or
nano .env     # On Linux/Mac
```

### 3. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload (recommended for development)
python main.py

# Alternative: Run with uvicorn directly for more control
uvicorn main:app --reload --host 0.0.0.0 --port 8000

```

### 4. Frontend Setup
```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔑 Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Google Gemini AI API
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=task_planning_db

# External APIs
WEATHER_API_KEY=your_openweather_api_key_here
WEB_SEARCH_API_KEY=your_serpapi_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 🔗 Getting API Keys

1. **Google Gemini API**:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Create new API key

2. **OpenWeatherMap API**:
   - Visit: https://openweathermap.org/api
   - Sign up for free account
   - Get API key from dashboard

3. **SerpAPI (Web Search)**:
   - Visit: https://serpapi.com/
   - Sign up for account
   - Get API key from dashboard

## 📝 API Endpoints

### Plans Management
- **POST** `/api/v1/plans` - Create a new plan from a goal
- **GET** `/api/v1/plans` - Get all plans with pagination
- **GET** `/api/v1/plans/{id}` - Get a specific plan by ID
- **PUT** `/api/v1/plans/{id}` - Update an existing plan
- **DELETE** `/api/v1/plans/{id}` - Delete a plan
- **GET** `/api/v1/plans/search?goal={pattern}` - Search plans by goal pattern

### Utility Endpoints
- **GET** `/api/v1/health` - Health check endpoint
- **GET** `/health` - Legacy health check (backward compatibility)
- **GET** `/` - Root endpoint with API information
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation

## 🎯 Usage Examples

### Using the Frontend
1. Open http://localhost:5173
2. Enter a travel goal like: "Plan a 3-day trip to Jaipur with cultural highlights"
3. Wait for AI to generate your personalized itinerary
4. View detailed day-by-day plans with weather-optimized activities

### Using the API Directly
```python
import requests

# Create a new plan
response = requests.post("http://localhost:8000/api/v1/plans", json={
    "goal": "Plan a weekend getaway to Paris with romantic activities"
    })

plan = response.json()
print(f"Created plan ID: {plan['id']}")

# Get the plan
plan_detail = requests.get(f"http://localhost:8000/api/v1/plans/{plan['id']}")
print(plan_detail.json())
```

## � Example Generated Plans

Here are two example goals with their AI-generated travel plans:

### Example 1: 
**Goal**: "Plan a 3-day trip to Jaipur with cultural highlights"

**Generated Plan Summary**:
```json
{
  "description": "A 3-day cultural and culinary exploration of Jaipur, carefully planned to accommodate the weather conditions and optimize travel time.",
  "total_duration": "3 days",
  "days": [
    {
      "day_number": 1,
      "date": "2025-09-24",
      "summary": "Arrival, hotel check-in, and exploration of the City Palace and Jantar Mantar. Evening stroll and dinner in the Pink City.",
      "tasks": [
        {
          "title": "Arrival at Jaipur International Airport (JAI)",
          "description": "Arrive at Jaipur International Airport (JAI). Take a pre-booked taxi or ride-sharing service to your hotel. (Estimated travel time: 30 minutes)",
          "estimated_duration": "0.5 hours",
          "status": "pending"
        },
        {
          "title": "Hotel Check-in: Hotel Diggi Palace (near City Palace)",
          "description": "Check into Hotel Diggi Palace (Diggi House, Shivaji Marg, C-Scheme, Jaipur, Rajasthan 302001, India). This hotel is centrally located near many attractions. Leave luggage and freshen up.",
          "estimated_duration": "1 hour",
          "status": "pending"
        },
        {
          "title": "City Palace Visit",
          "description": "Visit the City Palace (Jaleb Chowk, Near Jantar Mantar, Jaipur, Rajasthan 302002, India). Explore the Mubarak Mahal, Chandra Mahal, and other courtyards and museums within the palace complex. (Estimated exploration time: 2.5 hours). Due to pleasant weather, outdoor exploration is ideal.",
          "estimated_duration": "2.5 hours",
          "status": "pending"
        },
        {
          "title": "Lunch near City Palace",
          "description": "Have lunch at Laxmi Misthan Bhandar (LMB) (No. 98, 99, Johari Bazar Rd, Bapu Bazar, Pink City, Jaipur, Rajasthan 302003, India) for traditional Rajasthani cuisine. (Estimated time: 1 hour)",
          "estimated_duration": "1 hour",
          "status": "pending"
        },
        {
          "title": "Jantar Mantar Visit",
          "description": "Visit Jantar Mantar (Gangori Bazaar, J Jaipur, Rajasthan 302002, India), an astronomical observation site. Explore the various instruments and learn about their functions. (Estimated exploration time: 1.5 hours). Weather is suitable for outdoor viewing.",
          "estimated_duration": "1.5 hours",
          "status": "pending"
        },
        {
          "title": "Explore the Pink City and Bapu Bazaar",
          "description": "Take a leisurely walk through the Pink City, exploring Bapu Bazaar and Johari Bazaar. Shop for textiles, jewelry, and handicrafts. (Estimated time: 2 hours). Weather is suitable for walking and shopping.",
          "estimated_duration": "2 hours",
          "status": "pending"
        },
        {
          "title": "Dinner at Niros",
          "description": "Enjoy dinner at Niros (MI Road, Panch Batti, C-Scheme, Jaipur, Rajasthan 302001, India), a restaurant known for its Indian and Continental cuisine. (Estimated time: 1.5 hours)",
          "estimated_duration": "1.5 hours",
          "status": "pending"
        }
      ]
    },
    {
      "day_number": 2,
      "date": "2025-09-25",
      "summary": "Visit Amber Fort and Jaigarh Fort in the morning, followed by a visit to Panna Meena ka Kund. Evening visit to Nahargarh Fort for sunset views.",
      "tasks": [
        {
          "title": "Amber Fort Visit",
          "description": "Visit Amber Fort (Devisinghpura, Amer, Jaipur, Rajasthan 302001, India). Take an elephant ride (optional) or jeep to the top. Explore the Sheesh Mahal, Diwan-i-Aam, and other sections of the fort. (Estimated exploration time: 3 hours). Morning is ideal due to pleasant weather. Start early to avoid crowds.",
          "estimated_duration": "3 hours",
          "status": "pending"
        },
        {
          "title": "Jaigarh Fort Visit",
          "description": "Visit Jaigarh Fort (Devisinghpura, Amer, Jaipur, Rajasthan 302001, India), which overlooks Amber Fort. See the Jaivana cannon, the world's largest wheeled cannon. (Estimated exploration time: 1.5 hours).",
          "estimated_duration": "1.5 hours",
          "status": "pending"
        },
        {
          "title": "Lunch near Amber Fort",
          "description": "Have lunch at 1135 AD (Level 2, Jaleb Chowk, Amer Fort, Jaipur, Rajasthan 302001, India) within Amber Fort for a royal dining experience. (Estimated time: 1.5 hours)",
          "estimated_duration": "1.5 hours",
          "status": "pending"
        },
        {
          "title": "Panna Meena ka Kund Stepwell",
          "description": "Visit Panna Meena ka Kund, a historic stepwell located near Amber Fort. Admire the unique architecture and take photos. (Estimated exploration time: 1 hour)",
          "estimated_duration": "1 hour",
          "status": "pending"
        },
        {
          "title": "Travel to Nahargarh Fort",
          "description": "Travel to Nahargarh Fort (Brahmpuri, Jaipur, Rajasthan 302002, India). (Estimated travel time: 45 min)",
          "estimated_duration": "0.75 hours",
          "status": "pending"
        },
        {
          "title": "Nahargarh Fort Sunset View",
          "description": "Enjoy the sunset view from Nahargarh Fort, offering panoramic views of Jaipur city. (Estimated time: 1.5 hours). Arrive by late afternoon to secure a good viewing spot.",
          "estimated_duration": "1.5 hours",
          "status": "pending"
        },
        {
          "title": "Dinner at Padao Restaurant (Nahargarh Fort)",
          "description": "Have dinner at Padao Restaurant within Nahargarh Fort, enjoying the city lights. (Estimated time: 1.5 hours)",
          "estimated_duration": "1.5 hours",
          "status": "pending"
        }
      ]
    },
    {
      "day_number": 3,
      "date": "2025-09-26",
      "summary": "Morning visit to Hawa Mahal, followed by Albert Hall Museum. Afternoon shopping at a local market. Departure from Jaipur International Airport.",
      "tasks": [
        {
          "title": "Hawa Mahal Visit (early morning)",
          "description": "Visit Hawa Mahal (Badi Chaupar, Pink City, Jaipur, Rajasthan 302002, India). Capture the iconic facade and learn about its history. (Estimated exploration time: 1 hour). Arrive early (around 9 AM) to avoid the midday heat and crowds. ",
          "estimated_duration": "1 hour",
          "status": "pending"
        },
        {
          "title": "Albert Hall Museum Visit",
          "description": "Visit Albert Hall Museum (Ram Niwas Garden, Kailash Puri, Adarsh Nagar, Jaipur, Rajasthan 302004, India). Explore the collection of art and artifacts. (Estimated exploration time: 2 hours). Ideal for a hot day as it's an indoor activity.",
          "estimated_duration": "2 hours",
          "status": "pending"
        },
        {
          "title": "Lunch near Albert Hall Museum",
          "description": "Have lunch at Tapri Central (B4 E, 3rd Floor, Surana Jewelers, Opposite Central Park, Prithviraj Road, C-Scheme, Jaipur, Rajasthan 302001, India), known for its snacks and tea. (Estimated time: 1 hour)",
          "estimated_duration": "1 hour",
          "status": "pending"
        },
        {
          "title": "Shopping at Tripolia Bazaar",
          "description": "Visit Tripolia Bazaar, famous for bangles, textiles, and traditional Rajasthani clothing. (Estimated shopping time: 2 hours). Choose light, breathable clothing due to the heat. Consider buying souvenirs.",
          "estimated_duration": "2 hours",
          "status": "pending"
        },
        {
          "title": "Travel to Jaipur International Airport (JAI)",
          "description": "Travel to Jaipur International Airport (JAI) for departure. (Estimated travel time: 45 minutes).",
          "estimated_duration": "0.75 hours",
          "status": "pending"
        },
        {
          "title": "Departure from Jaipur International Airport (JAI)",
          "description": "Depart from Jaipur International Airport (JAI).",
          "estimated_duration": "1 hour",
          "status": "pending"
        }
      ]
    }
  ]
}
```

### Example 2:
**Goal**: "Plan a 2‑day vegetarian food tour in Hyderabad."

**Generated Plan Summary**:
```json
{
  "description": "A 2-day vegetarian food tour in Hyderabad, designed to maximize enjoyment despite the predicted rainy weather. The plan prioritizes indoor venues and delicious vegetarian cuisine, with efficient route planning to minimize travel time.",
  "total_duration": "2 days",
  "days": [
    {
      "day_number": 1,
      "date": "2025-09-21",
      "summary": "Arrival, hotel check-in, and exploration of vegetarian culinary delights in Hyderabad, focusing on areas near the hotel due to the high probability of rain.",
      "tasks": [
        {
          "title": "Arrival at Rajiv Gandhi International Airport (HYD)",
          "description": "Arrive at Rajiv Gandhi International Airport (HYD). Collect your luggage and proceed to the pre-booked taxi/Ola/Uber. Account for potential delays.",
          "estimated_duration": "1 hour",
          "status": "pending"
        },
        {
          "title": "Check-in at Hotel Minerva Grand (Near Begumpet)",
          "description": "Take a taxi/Ola/Uber from the airport to Hotel Minerva Grand, Begumpet (Address: SD Road, Near Railway Station, Secunderabad, Telangana 500003). Check in and freshen up.  Hotel choice is based on proximity to many attractions and good vegetarian options nearby.  Travel time from airport: ~45 minutes. Weather Rating: 4/10 for outdoor activities.",
          "estimated_duration": "1.5 hours",
          "status": "pending"
        },
        {
          "title": "Lunch at Chutneys (Himayatnagar)",
          "description": "Head to Chutneys in Himayatnagar for a delicious South Indian vegetarian thali. It's a popular spot known for its diverse chutney selection. From Minerva Grand, take a taxi/auto-rickshaw (~15 minutes). Address: 3-6-356/357, Liberty Road, Himayath Nagar, Hyderabad, Telangana 500029. Weather consideration: Indoor dining.",
          "estimated_duration": "1.5 hours",
          "status": "pending"
        },
        {
          "title": "Visit Birla Mandir",
          "description": "Visit Birla Mandir, a white marble temple dedicated to Lord Venkateswara. Take a taxi from Himayatnagar (approx. 20 min). While the temple offers panoramic city views, limit outdoor time due to the rain. Address: Naubat Pahad, Khairatabad, Hyderabad, Telangana 500004.  Weather consideration: Partly covered, but limit outdoor time. Weather Rating: 6/10 with rain gear.",
          "estimated_duration": "2 hours",
          "status": "pending"
        },
        {
          "title": "Dinner at Ohri's De Thali (Abids)",
          "description": "Enjoy a traditional vegetarian thali at Ohri's De Thali in Abids. This restaurant offers a variety of North Indian and Rajasthani dishes. From Birla Mandir, take a taxi (approx. 25 minutes). Address: 4-1-898, Tilak Road, Abids, Hyderabad, Telangana 500001. Weather consideration: Indoor dining.",
          "estimated_duration": "2 hours",
          "status": "pending"
        },
        {
          "title": "Return to Hotel Minerva Grand",
          "description": "Take a taxi/Ola/Uber from Abids back to Hotel Minerva Grand. Relax and prepare for the next day. Travel time: ~20 minutes.",
          "estimated_duration": "1 hour",
          "status": "pending"
        }
      ]
    },
    {
      "day_number": 2,
      "date": "2025-09-22",
      "summary": "Exploring Hyderabad's cultural heritage and enjoying more vegetarian cuisine, with a focus on indoor activities due to the heavy rain forecast.",
      "tasks": [
        {
          "title": "🌤️ WEATHER: Overcast clouds, 23.2°C - 30.4°C, 100% rain probability - Activity Impact: Plan adjusted for indoor activities.",
          "description": "⚠️ WEATHER ADVISORY: Heavy Rain - Plan modified for indoor activities. Weather Rating: 3/10 for outdoor activities. Wear waterproof clothing and shoes. Keep an umbrella handy.",
          "estimated_duration": "0 hours",
          "status": "pending"
        },
        {
          "title": "Breakfast at Hotel Minerva Grand",
          "description": "Enjoy breakfast at the hotel's restaurant. Fuel up for a day of exploring Hyderabad. Weather Consideration: Indoor Activity",
          "estimated_duration": "1 hour",
          "status": "pending"
        },
        {
          "title": "Visit Salar Jung Museum",
          "description": "Take a taxi/Ola/Uber to Salar Jung Museum (Address: Salar Jung Road, Near Minar Function Hall, Darulshifa, Hyderabad, Telangana 500002). Explore the vast collection of art and artifacts. Allow ample time to wander through the exhibits. From Hotel Minerva Grand, approx travel time is 45 minutes due to anticipated traffic. Weather consideration: Entirely indoor activity.",
          "estimated_duration": "3.5 hours",
          "status": "pending"
        },
        {
          "title": "Lunch at Dakshin (ITC Kakatiya)",
          "description": "Enjoy a fine dining vegetarian experience at Dakshin (ITC Kakatiya) serving South Indian cuisine. From Salar Jung, take a taxi/Uber (approx 30 min) Weather consideration: Indoor dining. Address: ITC Kakatiya, 6-3-1187, Greenlands, Begumpet, Hyderabad, Telangana 500016.",
          "estimated_duration": "2 hours",
          "status": "pending"
        },
        {
          "title": "Shopping at GVK One Mall",
          "description": "Head to GVK One Mall (Road No. 1, Banjara Hills, Hyderabad, Telangana 500034) for some shopping. It's a large indoor mall, perfect for a rainy afternoon. From ITC Kakatiya, it's a short taxi ride (approx. 20 min). Weather Consideration: Indoor activity.",
          "estimated_duration": "3 hours",
          "status": "pending"
        },
        {
          "title": "Dinner at Little Italy (Banjara Hills)",
          "description": "Enjoy a vegetarian Italian dinner at Little Italy in Banjara Hills. From GVK One Mall, it's a short walk or taxi ride. Address: 8-2-684/3/A, Plot No. 3, Road No. 12, Banjara Hills, Hyderabad, Telangana 500034. Weather Consideration: Indoor dining.",
          "estimated_duration": "2 hours",
          "status": "pending"
        },
        {
          "title": "Return to Hotel Minerva Grand & Departure",
          "description": "Take a taxi/Ola/Uber from Banjara Hills back to Hotel Minerva Grand (approx. 30 min). Collect your luggage and proceed to the airport for your departure flight.  Allow ample time for traffic delays.",
          "estimated_duration": "2 hours",
          "status": "pending"
        }
      ]
    }
  ]
}
```

## �🔍 Trip Logging System

The application features a comprehensive trip-specific logging system:

### Log Structure
- **Location**: `backend/logs/trips/`
- **Format**: `YYYYMMDD_HHMMSS_goal_summary_trip-id.log`
- **Content**: Complete audit trail of trip planning process

### Log Contents
- Goal analysis and extraction
- External API calls (weather, search) with full request/response data
- AI plan generation with prompts and responses
- Database operations and results
- Error handling with detailed context
- Performance timing information

### Example Log Entry
```
================================================================================
TRIP LOG STARTED: Plan a 3-day trip to Jaipur with cultural highlights
Trip ID: Generated
Timestamp: 2025-09-21 15:26:35
================================================================================
2025-09-21 15:26:35 - INFO - 🔄 STEP: Plan Creation Started
2025-09-21 15:26:36 - INFO - ✅ SUCCESS: Goal information extracted
{
  "destination": "Jaipur",
  "duration": 3,
  "activities": ["cultural highlights"],
  "preferences": []
}
...
```

## 🧪 Development

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload (recommended for development)
python main.py

# Alternative: Run with uvicorn directly for more control
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for APIs
- **Python 3.12+**: Latest Python with type hints
- **MongoDB**: NoSQL database with Motor async driver
- **Pydantic v2**: Data validation and serialization
- **Google Gemini AI**: Advanced language model for plan generation
- **OpenWeatherMap**: Real-time weather data
- **SerpAPI**: Web search for local information

### Frontend
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/ui**: High-quality component library
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🤖 AI Development Disclosure

This project was developed with assistance from AI tools to enhance productivity and code quality. AI was used as a coding assistant to help implement features, suggest improvements, and solve technical challenges throughout the development process. The AI assistance included help with code structure, error handling patterns, logging implementation, performance optimizations, and frontend component design and user interface development.

### Human Oversight:
- All AI-generated code was reviewed, tested, and modified by me
- Business logic and architecture decisions were made by me
- API integrations and external service configurations were manually implemented and tested
- Security considerations and environment variable handling were human-verified
- Frontend design patterns and component structure were human-reviewed and customized

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for intelligent plan generation
- OpenWeatherMap for weather data
- SerpAPI for web search capabilities
- Shadcn/ui for beautiful UI components
- FastAPI community for excellent documentation

---

**Happy Trip Planning! 🌍✈️**