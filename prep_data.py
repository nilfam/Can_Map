import pandas as pd

INPUT_CSV = "contacts_with_area.csv"
OUT_CSV = "company_area_points.csv"

df = pd.read_csv(INPUT_CSV, dtype=str, low_memory=False)

# Clean
df["company"] = df["company"].astype(str).str.strip()
df["area"] = df["area"].astype(str).str.strip()
df["project_id"] = df["project_id"].astype(str).str.strip()

# If area contains comma-separated lists, split & explode
df["area"] = df["area"].str.split(r"\s*,\s*")
df = df.explode("area")
df["area"] = df["area"].astype(str).str.strip()

# NZ area coords (covers your labels from earlier)
AREA_COORDS = {
    "Auckland City": (-36.8485, 174.7633),
    "Auckland North Shore": (-36.8000, 174.7500),
    "Auckland South": (-36.9920, 174.8800),
    "Auckland West": (-36.8640, 174.6010),
    "Auckland East": (-36.8800, 174.9000),

    "Canterbury": (-43.5321, 172.6362),
    "Waikato": (-37.7870, 175.2793),
    "Otago": (-45.8788, 170.5028),
    "Wellington": (-41.2866, 174.7756),
    "Bay of Plenty": (-37.6878, 176.1651),
    "Northland": (-35.7251, 174.3237),
    "Taranaki": (-39.0556, 174.0752),
    "Southland": (-46.4132, 168.3538),
    "West Coast": (-42.4500, 171.2100),
    "Wairarapa": (-41.2100, 175.4600),
    "Manawatu/Whanganui": (-40.3523, 175.6082),
    "Hawkes Bay/Gisborne": (-39.4928, 176.9120),
    "Nelson/Marlborough": (-41.5134, 173.9610),
}

# Company-area aggregation
summary = (
    df.dropna(subset=["company", "area", "project_id"])
      .groupby(["company", "area"])["project_id"]
      .nunique()
      .reset_index(name="n_projects")
)

summary["lat"] = summary["area"].map(lambda a: AREA_COORDS.get(a, (None, None))[0])
summary["lon"] = summary["area"].map(lambda a: AREA_COORDS.get(a, (None, None))[1])
summary = summary.dropna(subset=["lat", "lon"])

summary.to_csv(OUT_CSV, index=False)
print("Saved:", OUT_CSV, "rows:", len(summary))
