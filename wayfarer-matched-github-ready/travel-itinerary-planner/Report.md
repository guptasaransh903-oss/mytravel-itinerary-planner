# WanderPlan — Personalized Travel Itinerary Planner

**An AI-Powered Full-Stack Web Application**

- **Live Website:** https://travel-itinerary-planner-sigma.vercel.app/
- **Backend API:** https://wanderplan-api.onrender.com/health
- **GitHub Repository:** https://github.com/anvij61-collab/travel-itinerary-planner

---

## 1. Abstract

WanderPlan is an AI-powered web application designed to simplify travel planning by generating personalized, day-by-day travel itineraries. Users can enter their destination, travel dates, total budget, preferred travel style, and interests to receive customized travel suggestions.

The application uses React for the frontend, FastAPI for backend services, Google Gemini AI for itinerary generation, and Supabase for storing saved trips. The frontend and backend are deployed using Vercel and Render, respectively.

WanderPlan aims to make travel planning easier, faster, and more personalized through generative artificial intelligence.

## 2. Introduction

Planning a trip involves researching destinations, selecting activities, organizing schedules, and estimating expenses. This process can be time-consuming, especially when travellers have different interests and budgets.

WanderPlan provides a simple platform where users can enter their travel preferences and generate an itinerary tailored to their requirements. Users can also save their plans and access them later through the My Trips section.

## 3. Problem Statement

Traditional travel planning often requires users to visit multiple websites and manually organize destinations, activities, and estimated expenses. Generic travel recommendations may not suit individual preferences or budgets.

Therefore, a system is needed that can generate personalized travel itineraries based on user inputs and provide a convenient way to save and manage travel plans.

## 4. Objectives

- To develop an AI-powered travel planning web application.
- To generate day-by-day itineraries based on user preferences.
- To consider travel dates, budget, travel style, and interests.
- To provide a simple and user-friendly interface.
- To enable users to save, view, refresh, and delete trips.
- To integrate a generative AI API with a backend service.
- To store trip information using a database.
- To deploy the application on cloud platforms.

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| React | Builds the interactive user interface |
| Vite | Frontend development and production builds |
| Python | Backend programming language |
| FastAPI | Provides backend API endpoints |
| Google Gemini AI | Generates personalized itinerary suggestions |
| Google GenAI SDK | Connects the backend to Gemini |
| Supabase | Stores and retrieves saved trip data |
| Vercel | Hosts the frontend |
| Render | Hosts the backend API |
| Git and GitHub | Version control and source-code management |

## 6. Main Features

### 6.1 Personalized Trip Planning

Users can enter:
- Destination
- Start date and end date
- Total budget in Indian rupees
- Travel style: Relaxed, Balanced, or Adventurous
- Interests: Food, Nature, Culture, Shopping, and History

### 6.2 AI-Based Itinerary Generation

The application sends the user's trip preferences to the FastAPI backend. The backend uses Google Gemini AI to generate a day-by-day itinerary with activities and estimated costs.

### 6.3 Save and Manage Trips

Users can save generated itineraries and view them in the My Trips section. Saved trip cards display information such as destination, duration, dates, budget, estimated cost, travel style, and interests.

Users can refresh the saved-trip list and delete trips when they are no longer needed.

### 6.4 Cloud Deployment

The application is available through a public website. The frontend, backend, and database are handled by separate services.

## 7. System Architecture

```text
              +----------------------+
              |        User          |
              +----------+-----------+
                         |
                         v
              +----------------------+
              | React + Vite         |
              | Frontend (Vercel)    |
              +----------+-----------+
                         |
                    API Requests
                         |
                         v
              +----------------------+
              | FastAPI Backend      |
              | (Render)             |
              +-----+-----------+----+
                    |           |
                    v           v
          +----------------+  +----------------+
          | Google Gemini  |  | Supabase       |
          | AI API          |  | Database       |
          +----------------+  +----------------+
```

### Working Process

1. The user enters trip details on the frontend.
2. The frontend sends the request to the backend API.
3. The backend processes the preferences and calls Gemini AI.
4. Gemini generates itinerary suggestions.
5. The backend returns the generated itinerary to the frontend.
6. The user can review and save the itinerary.
7. Saved trip information is stored in Supabase and retrieved for the My Trips section.

## 8. Database and Security

Supabase is used to store saved trip information. The backend communicates with Supabase to perform database operations.

Security measures include:

- API keys are stored in environment variables.
- The Supabase service-role key is used on the backend only.
- Secret files such as `.env` are excluded from version control.
- CORS settings control which frontend origins can access the API.
- Privileged database operations are handled by the backend rather than exposing service credentials to the browser.

**Important:** API keys and database credentials must never be committed to the public GitHub repository.

## 9. Installation and Local Setup

### 9.1 Prerequisites

Install the following tools:

- Git
- Node.js and npm
- Python
- Cursor or another code editor

You will also need a Supabase project and a Google Gemini API key.

### 9.2 Clone the Repository

Open PowerShell or a terminal and run:

```bash
git clone https://github.com/anvij61-collab/travel-itinerary-planner.git
cd travel-itinerary-planner
```

### 9.3 Set Up the Backend

Move into the backend folder:

```powershell
cd backend
```

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate the environment in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Configure the backend environment variables in a local `backend/.env` file. Supply your own Gemini API key, Gemini model setting, Supabase project URL, Supabase service-role key, and allowed CORS origins as required by the application.

Start the backend:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

The local API will be available at:

`http://127.0.0.1:8001`

### 9.4 Set Up the Frontend

Open a second terminal and navigate to the frontend directory from the project root:

```powershell
cd frontend
```

Install the frontend dependencies:

```powershell
npm install
```

Create a local `frontend/.env` file containing:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8001
```

Start the development server:

```powershell
npm run dev
```

Open the local URL printed by Vite, usually:

`http://localhost:5173`

**Note:** Keep environment files and all API keys private. Never upload them to GitHub.

## 10. Deployment

### 10.1 Frontend Deployment — Vercel

The React and Vite frontend is deployed using Vercel.

- **Production URL:** https://travel-itinerary-planner-sigma.vercel.app/
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Production environment variable: `VITE_API_BASE_URL=https://wanderplan-api.onrender.com`

### 10.2 Backend Deployment — Render

The FastAPI backend is deployed using Render.

- **Backend URL:** https://wanderplan-api.onrender.com
- Health endpoint: https://wanderplan-api.onrender.com/health
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

The backend environment must contain the required Gemini and Supabase configuration and the correct CORS origins.

### 10.3 Database — Supabase

Supabase stores saved trip data. The backend uses server-side credentials to access the database.

## 11. Testing and Results

The following functionality has been observed in the deployed application:

| Test | Observed Result |
|---|---|
| Open the live website | Successful |
| Backend health check | API online |
| Generate a personalized itinerary | Successful |
| Display estimated trip cost | Working |
| Save a trip | Successful |
| Display saved trips | Successful |
| Display multiple saved itineraries | Successful |

Example trips displayed in the application include Jaipur and Goa, with their travel dates, budgets, estimated costs, travel styles, and interests.

### Additional Recommended Tests

- Test different destinations and travel preferences.
- Check validation for missing or invalid inputs.
- Save a trip and refresh the browser to confirm persistence.
- Delete a test trip and verify that it disappears.
- Test the interface on desktop and mobile screens.
- Check that no secret files are tracked by Git.

## 12. Advantages

- Saves time during travel planning.
- Generates personalized travel suggestions.
- Supports different travel styles and interests.
- Displays estimated costs to help with budget planning.
- Allows users to save and manage trips.
- Uses a modular frontend and backend architecture.
- Is accessible through a public web application.

## 13. Limitations

- Generated costs are estimates and may not reflect current prices.
- AI-generated activities may require independent verification.
- Live transport availability, weather, opening hours, and bookings are not guaranteed.
- The quality of recommendations depends on the user inputs and AI output.
- Authentication and individual account ownership may require further development.

## 14. Future Scope

Possible future enhancements include:

- User registration and login.
- Personal trip history associated with individual accounts.
- Interactive maps and route planning.
- Live weather and transport information.
- Detailed accommodation, food, and transport cost breakdowns.
- PDF export of itineraries.
- Multilingual travel recommendations.
- Unit and integration testing.
- Improved accessibility and mobile responsiveness.
- More advanced AI output validation and error handling.

## 15. Conclusion

WanderPlan demonstrates the development and deployment of a full-stack, AI-powered travel planning application. It integrates React, FastAPI, Google Gemini AI, and Supabase to generate personalized itineraries and store saved trips.

The project provides practical experience in frontend development, backend API creation, generative AI integration, database persistence, environment configuration, version control, and cloud deployment.

WanderPlan can be further enhanced with real-time travel data, authentication, maps, and additional personalization features.

## 16. Project Links

- **Live application:** https://travel-itinerary-planner-sigma.vercel.app/
- **Backend health check:** https://wanderplan-api.onrender.com/health
- **Source code:** https://github.com/anvij61-collab/travel-itinerary-planner

