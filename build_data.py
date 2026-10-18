"""Save the shipment data and the assumptions for the U.S. market estimate."""

import json
from pathlib import Path

import pandas as pd

folder = Path(__file__).resolve().parent / "data"
folder.mkdir(exist_ok=True)
sources = json.loads((folder / "sources.json").read_text())

# Fiscal year, home/consumer robots shipped (thousands), reference ID.
# These are the full-year totals, not quarterly sales or revenue.
shipments = [
    (2005, 663, "S05"),
    (2006, 725, "S05"),
    (2007, 899, "S06"),
    (2008, 1054, "S07"),
    (2009, 988, "S07"),
    (2010, 1269, "S08"),
    (2011, 1371, "S08"),
    (2012, 1621, "S09"),
    (2013, 1933, "S09"),
    (2014, 2174, "S10"),
    (2015, 2436, "S10"),
    (2016, 2943, "S11"),
    (2017, 3698, "S11"),
    (2018, 4537, "S12"),
    (2019, 4989, "S12"),
    (2020, 5494, "S13"),
    (2021, 5602, "S14"),
    (2022, 4182, "S14"),
    (2023, 3034, "S15"),
    (2024, 2463, "S16")
]
data = pd.DataFrame(shipments, columns=["fiscal_year", "units_thousands", "source_id"])
data["reported_category"] = "Robot units shipped - Total"
data.loc[data.fiscal_year <= 2017, "reported_category"] = "Consumer units shipped"
data.loc[data.fiscal_year <= 2015, "reported_category"] = "Home Robots"
data["source_url"] = data.source_id.map(lambda key: sources[key]["url"])
data.to_csv(folder / "irobot_shipments.csv", index=False)

# Household count: 2024 ACS, table S1101 (S17).
# The segment and capture shares below are Fermi assumptions, not survey results.
households = 132_737_146
segment_share = 0.20
capture_shares = {"Low": 0.05, "Base": 0.10, "High": 0.20}
rows = []
for scenario, capture in capture_shares.items():
    rows.append({
        "scenario": scenario,
        "us_households": households,
        "premium_segment_share_assumed": segment_share,
        "x50_capture_share_assumed": capture,
        "market_potential_households": round(households * segment_share * capture),
        "household_count_source": sources["S17"]["url"]
    })
pd.DataFrame(rows).to_csv(folder / "us_market_potential.csv", index=False)
print("Saved shipment data and market assumptions.")
