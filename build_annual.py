"""Create reproducible annual totals from published monthly API history.
Annual values are derived sums, not an independently validated annual publication.
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = ROOT / "data" / "history.csv"
dest = ROOT / "data" / "annual.csv"
sums = defaultdict(int)
months = defaultdict(set)

with source.open(encoding="utf-8-sig", newline="") as fh:
    for row in csv.DictReader(fh):
        year, month = int(row["Ar"]), int(row["Manad"])
        country = row["Hemland"].strip()
        value = int(float(row["Gastnatter"]))
        if not country or not 1 <= month <= 12 or value < 0:
            raise ValueError(f"Invalid history row: {row}")
        sums[(year, country)] += value
        months[year].add(month)

dest.parent.mkdir(parents=True, exist_ok=True)
with dest.open("w", encoding="utf-8-sig", newline="") as fh:
    wr = csv.writer(fh)
    wr.writerow(["Ar", "Hemland", "Gastnatter", "Manader_i_underlaget", "Komplett_ar", "Kalla"])
    for (year, country), amount in sorted(sums.items()):
        wr.writerow([year, country, amount, len(months[year]), int(len(months[year]) == 12), "Summering av GuestNights_Country_Month"])
print(f"Annual file updated: {len(sums)} country-year rows ({len(months)} years)")
