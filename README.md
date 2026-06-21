# Nassau Candy Distributor — Shipping Route Efficiency Dashboard

Live Dashboard - https://duztv9srnemux5bc79izwt.streamlit.app/

## Running locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app (from this folder):
   ```
   streamlit run app.py
   ```

3. Open the URL Streamlit prints (usually http://localhost:8501).

## Files

- `app.py` — the Streamlit application
- `clean_data.csv` — cleaned, feature-engineered shipment data (output of the analysis pipeline)
- `factory_coords.json` — factory name → (latitude, longitude) lookup
- `requirements.txt` — Python dependencies

## Data note

Shipping "lead time" in this dashboard is represented by **Ship Mode** (Same Day / First
Class / Second Class / Standard Class), not by a computed day-level lead time. The source
Order Date and Ship Date fields are not reliably linked in this dataset (every record shows
a 900+ day gap), so a day-level lead-time metric would be fabricated. See the accompanying
research paper, Section 2.3, for full details.
