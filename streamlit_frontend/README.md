# Mkulima Streamlit frontend

This frontend is organized like the React app, with reusable UI in `src/components`,
pages in `src/pages`, and backend calls in `src/services`.

Run the `backend/app` API and the Streamlit frontend from separate terminals:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

```powershell
cd streamlit_frontend
streamlit run app.py
```

The frontend uses `http://localhost:8000` by default. Set `MUKULIMA_API_URL` to
the backend base URL when it is hosted elsewhere.

The farm analysis and yield prediction pages require existing farm and crop
cycle IDs in the backend database. Collect farm features before generating a
yield prediction.
