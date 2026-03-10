import pandas as pd
import numpy as np
import re

PROJECTS_PATH = r"C:\Users\naflaki\Downloads\resiliencehub-main\resiliencehub-main\company_map_app\Projects_combined.csv"
CONTACTS_PATH = r"C:\Users\naflaki\Downloads\resiliencehub-main\resiliencehub-main\company_map_app\Contacts_combined.csv"
OUTPUT_CSV= r"C:\Users\naflaki\Downloads\resiliencehub-main\resiliencehub-main\company_map_app\company_area_points_with_type_value.csv"


def main():
    projects = pd.read_csv(PROJECTS_PATH, dtype=str, low_memory=False)
    contacts = pd.read_csv(CONTACTS_PATH, dtype=str, low_memory=False)

    project_id_col = "project_id"
    add_cols = ["area", "type_description", "estimated_value", "estimated_range"]

    # Validate columns exist
    missing_projects = [c for c in [project_id_col] + add_cols if c not in projects.columns]
    if missing_projects:
        raise ValueError(
            f"Missing columns in projects file: {missing_projects}\n"
            f"Projects columns are:\n{list(projects.columns)}"
        )

    if project_id_col not in contacts.columns:
        raise ValueError(
            f"Contacts file is missing '{project_id_col}'. Contacts columns are:\n{list(contacts.columns)}"
        )

    # Keep one row per project_id from projects
    projects_sub = projects[[project_id_col] + add_cols].drop_duplicates(subset=[project_id_col])

    # Merge into contacts (keeps ALL contact rows)
    result = contacts.merge(projects_sub, on=project_id_col, how="left")

    # Save to CSV
    result.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Saved CSV: {OUTPUT_CSV}")
    print(f"Rows in contacts: {len(contacts)}")
    for c in add_cols:
        print(f"Rows with matched {c}: {result[c].notna().sum()}")


if __name__ == "__main__":
    main()