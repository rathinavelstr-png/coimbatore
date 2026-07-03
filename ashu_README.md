# Kovai SkyWatch

A Streamlit app showing live weather for Coimbatore, Tamil Nadu — current
conditions, an hourly temperature/humidity chart (next 48 hrs), rain
probability, and a 7-day outlook.

Data comes from **Open-Meteo** (https://open-meteo.com) — free, no API key
needed, so there's nothing to configure or hide in secrets.

## Files

- `app.py` — the Streamlit app
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — theme + server config

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repo (keep `app.py`, `requirements.txt`,
   and `.streamlit/config.toml` at the repo root, or note the subfolder
   path when deploying).
2. Go to https://share.streamlit.io → "New app".
3. Select your repo, branch, and set **Main file path** to `app.py`.
4. Click **Deploy**. No secrets/API keys needed for this app.

## Common deployment issues (based on past experience)

- **"ModuleNotFoundError"** → double-check `requirements.txt` is at the
  same folder level as `app.py` that you set as the app's root in the
  Streamlit Cloud settings.
- **App stuck on "Please wait..."** → usually a dependency version
  conflict; try removing the pinned versions in `requirements.txt` and
  let Streamlit Cloud resolve the latest compatible ones.
- **Blank chart / KeyError** → Open-Meteo occasionally changes field
  names; if that happens, print `data.keys()` in a debug block to check
  the response shape before parsing.

## Notes

- The dashboard caches data for 5 minutes (`st.cache_data(ttl=300)`) to
  avoid hitting the API on every widget interaction, but you can force
  an immediate refresh with the "🔄 Refresh now" button.
- Coordinates are hardcoded to Coimbatore (11.0168° N, 76.9558° E). To
  reuse this for another city, just change `LATITUDE` and `LONGITUDE` in
  `app.py`.
