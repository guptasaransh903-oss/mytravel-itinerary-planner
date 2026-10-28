# Wayfarer — Travel Itinerary Planner

A refreshed Wayfarer landing page based on the publicly visible layout of the reference deployment, combined with the original React/Vite trip planner and Python FastAPI backend. **This is a visual recreation, not an export of the deployed site's source code.**

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open the local address printed by Vite. The new homepage is at `/`; click **Plan a Trip** to open the original functional trip planner at `/planner`. The planner needs the backend to generate and save itineraries.

## Run the backend

```bash
cd backend
python -m venv .venv
# activate the virtual environment for your operating system
pip install -r requirements.txt
# configure environment variables from .env.example
uvicorn main:app --reload
```

Review `frontend/.env.example` and `backend/.env.example` for configuration. Do not commit real `.env` files.

## Notes

- The new homepage recreates the publicly visible design and destination content, but cannot reproduce the deployed site's private implementation.
- Destination cards lead to the original planner. Collaboration and invitation codes from the reference site are not implemented.
- Homepage destination photographs load from Unsplash and require internet access.
- The original planner's API and persistence features still require a configured backend.
- This repository is ready for GitHub upload, but deploying the full stack requires configuring both frontend and backend.
