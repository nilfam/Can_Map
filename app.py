import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

DATA_CSV = "company_area_points.csv"

st.set_page_config(page_title="Company Areas Map", layout="wide")
st.title("Company operating areas")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)

    # Normalize expected columns
    if "company" not in df.columns:
        raise ValueError(f"Missing 'company' column. Found columns: {list(df.columns)}")
    if "area" not in df.columns:
        raise ValueError(f"Missing 'area' column. Found columns: {list(df.columns)}")
    if "lat" not in df.columns or "lon" not in df.columns:
        raise ValueError("Missing 'lat'/'lon' columns. Did you run prep_data.py?")

    # Clean
    df["company"] = df["company"].fillna("").astype(str).str.strip()
    df["area"] = df["area"].fillna("").astype(str).str.strip()

    # Remove empty company rows
    df = df[df["company"] != ""].copy()

    # Precompute lowercase for fast search
    df["company_lc"] = df["company"].str.lower()
    return df

df = load_data(DATA_CSV)

# ----------------- Debug panel -----------------
with st.expander("Debug (open if search shows nothing)"):
    st.write("Rows:", len(df))
    st.write("Unique companies:", df["company"].nunique())
    st.write("Sample companies:", df["company"].drop_duplicates().head(20).tolist())
    st.write("Columns:", list(df.columns))

# ----------------- Search UI -----------------
q = st.text_input("Search company (type part of the name):", "")
q_norm = q.strip().lower()

# Show match count + preview (this makes it obvious if search is working)
matches = []
if len(q_norm) >= 1:  # allow 1+ chars (you can switch back to 2 if you want)
    hits = (
        df.loc[df["company_lc"].str.contains(q_norm, regex=False, na=False), "company"]
          .drop_duplicates()
          .head(200)   # cap to keep UI fast
    )
    matches = hits.tolist()

st.caption(f"Matches found: {len(matches)} (showing up to 200)")

selected = st.selectbox("Select a company from matches:", [""] + matches)

# ----------------- Mapping helpers -----------------
def make_company_map(company_name: str):
    data = df[df["company"] == company_name].copy()

    view = (
        data.groupby("area")
            .agg(n_projects=("n_projects", "sum"), lat=("lat", "first"), lon=("lon", "first"))
            .reset_index()
    )

    # Safety: drop any NaN coords
    view = view.dropna(subset=["lat", "lon"])
    if view.empty:
        st.warning("No mappable areas for this company (missing coordinates).")
        return None, None

    center = [view["lat"].astype(float).mean(), view["lon"].astype(float).mean()]
    m = folium.Map(location=center, zoom_start=6)

    cluster = MarkerCluster().add_to(m)
    bounds = []

    for _, row in view.iterrows():
        lat = float(row["lat"]); lon = float(row["lon"])
        bounds.append([lat, lon])
        tooltip = f"{company_name} — {row['area']} (projects: {int(row['n_projects'])})"
        folium.CircleMarker([lat, lon], radius=10, tooltip=tooltip, popup=tooltip).add_to(cluster)

    if bounds:
        m.fit_bounds(bounds)

    return m, view.sort_values("n_projects", ascending=False)

# ----------------- Layout -----------------
col1, col2 = st.columns([2, 1])

with col2:
    st.metric("Total companies", int(df["company"].nunique()))
    st.metric("Total areas", int(df["area"].nunique()))
    st.caption("Tip: start typing; the list updates automatically.")

with col1:
    if selected:
        st.subheader(f"Map for: {selected}")
        m, table = make_company_map(selected)
        if m is not None:
            st_folium(m, width=1100, height=650)
            st.subheader("Areas for this company")
            st.dataframe(table, use_container_width=True)
    else:
        st.info("Type in the search box to see matches, then select a company.")
