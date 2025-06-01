import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta


st.set_page_config(page_title="NASA Near-Earth Object Tracker", layout="wide")

API_KEY = "bapvdxi4D7DlnjAoIisgo3T6NWP0ZTyF7SPYyFOF"
BASE_URL = "https://api.nasa.gov/neo/rest/v1/feed"


st.sidebar.header("Select Date Range")
today = datetime.today()
default_start = today - timedelta(days=6)
start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", today)


if (end_date - start_date).days > 7:
    st.sidebar.warning("NASA API only supports a 7-day date range. Please select a range within 7 days.")

st.title("🌑 NASA Near-Earth Object (Asteroid) Tracker")

if st.sidebar.button("Fetch NEO Data"):
    with st.spinner("Fetching data from NASA..."):
        url = (
            f"{BASE_URL}?start_date={start_date}&end_date={end_date}&api_key={API_KEY}"
        )
        try:
            resp = requests.get(url)
            data = resp.json()
            if "near_earth_objects" not in data:
                st.error("No data returned. Try different dates or check your API key.")
            else:
                neos = []
                for date_str in data["near_earth_objects"]:
                    for obj in data["near_earth_objects"][date_str]:
                        neos.append({
                            "Name": obj['name'],
                            "Date": date_str,
                            "Diameter (min, m)": obj['estimated_diameter']['meters']['estimated_diameter_min'],
                            "Diameter (max, m)": obj['estimated_diameter']['meters']['estimated_diameter_max'],
                            "Miss Distance (km)": float(obj['close_approach_data'][0]['miss_distance']['kilometers']),
                            "Velocity (km/h)": float(obj['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']),
                            "Hazardous?": obj['is_potentially_hazardous_asteroid'],
                            "NASA JPL Link": obj['nasa_jpl_url']
                        })
                df = pd.DataFrame(neos)
                if not df.empty:
                    st.write(f"### Near-Earth Objects from {start_date} to {end_date}")
                    st.dataframe(df)
                    st.write("#### Largest Asteroids (by max diameter)")
                    largest = df.sort_values("Diameter (max, m)", ascending=False).head(10)
                    st.bar_chart(largest[["Name", "Diameter (max, m)"]].set_index("Name"))
                    st.write("#### Closest Approaches")
                    closest = df.sort_values("Miss Distance (km)").head(10)
                    st.table(closest[["Name", "Date", "Miss Distance (km)", "Hazardous?"]])
                else:
                    st.info("No NEOs found in this range.")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("""
---
Built with [NASA NeoWs API](https://api.nasa.gov/) • Made with Streamlit  
*Project by Yassir Errami*
""")