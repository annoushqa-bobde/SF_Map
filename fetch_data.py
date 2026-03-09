"""
SF Pulse — Data Fetcher
Runs every hour via GitHub Actions.
Pulls fresh data from SF OpenData and saves as JSON for the map.
"""

import requests
import json
import os
from datetime import datetime, timedelta, timezone

SF_BASE = "https://data.sfgov.org/resource"

def fetch(dataset_id, limit=300, where=None, order=None):
    url = f"{SF_BASE}/{dataset_id}.json"
    params = {"$limit": limit}
    if where:
        params["$where"] = where
    if order:
        params["$order"] = order
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def safe_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def fetch_crime():
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
    rows = fetch("wg3w-h783", limit=300,
                 where=f"report_datetime > '{since}'",
                 order="report_datetime DESC")
    out = []
    for r in rows:
        lat = safe_float(r.get("latitude"))
        lng = safe_float(r.get("longitude"))
        if not lat or not lng:
            continue
        out.append({
            "type": "crime",
            "lat": lat, "lng": lng,
            "title": r.get("incident_category", "Unknown"),
            "detail": r.get("incident_description", ""),
            "neighborhood": r.get("analysis_neighborhood", ""),
            "time": r.get("report_datetime", ""),
            "district": r.get("police_district", ""),
        })
    return out

def fetch_311():
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
    rows = fetch("vw6y-z8j6", limit=300,
                 where=f"requested_datetime > '{since}'",
                 order="requested_datetime DESC")
    out = []
    for r in rows:
        lat = safe_float(r.get("lat"))
        lng = safe_float(r.get("long"))
        if not lat or not lng:
            continue
        out.append({
            "type": "311",
            "lat": lat, "lng": lng,
            "title": r.get("service_name", "Service Request"),
            "detail": r.get("service_subtype", ""),
            "neighborhood": r.get("neighborhoods_sffind_boundaries", ""),
            "time": r.get("requested_datetime", ""),
            "status": r.get("status_description", ""),
        })
    return out

def fetch_permits():
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    rows = fetch("i98e-djp9", limit=300,
                 where=f"filed_date > '{since}'",
                 order="filed_date DESC")
    out = []
    for r in rows:
        loc = r.get("location", {})
        if isinstance(loc, dict):
            lat = safe_float(loc.get("latitude"))
            lng = safe_float(loc.get("longitude"))
        else:
            lat = lng = None
        if not lat or not lng:
            continue
        cost = safe_float(r.get("estimated_cost"))
        out.append({
            "type": "permit",
            "lat": lat, "lng": lng,
            "title": r.get("permit_type_definition", "Permit"),
            "detail": r.get("description", ""),
            "neighborhood": r.get("neighborhoods_analysis_boundaries", ""),
            "time": r.get("filed_date", ""),
            "cost": f"${cost:,.0f}" if cost else "N/A",
            "status": r.get("status", ""),
        })
    return out

def fetch_inspections():
    rows = fetch("pyih-qa8i", limit=200, order="inspection_date DESC")
    out = []
    for r in rows:
        lat = safe_float(r.get("business_latitude"))
        lng = safe_float(r.get("business_longitude"))
        if not lat or not lng:
            lat = safe_float(r.get("latitude"))
            lng = safe_float(r.get("longitude"))
        if not lat or not lng:
            continue
        score = safe_float(r.get("inspection_score"))
        out.append({
            "type": "inspection",
            "lat": lat, "lng": lng,
            "title": r.get("business_name", "Restaurant"),
            "detail": r.get("inspection_type", ""),
            "neighborhood": r.get("business_city", "SF"),
            "time": r.get("inspection_date", ""),
            "score": score,
            "score_label": f"{int(score)}/100" if score else "N/A",
        })
    return out

def fetch_transit():
    rows = fetch("ygmz-vaxd", limit=200)
    out = []
    for r in rows:
        lat = safe_float(r.get("vehicle_lat") or r.get("latitude"))
        lng = safe_float(r.get("vehicle_lon") or r.get("longitude"))
        if not lat or not lng:
            continue
        out.append({
            "type": "transit",
            "lat": lat, "lng": lng,
            "title": f"Muni {r.get('route_tag', r.get('line', 'Vehicle'))}",
            "detail": r.get("direction_tag", r.get("direction", "")),
            "neighborhood": "",
            "time": r.get("epoch_time", r.get("insertion_time", "")),
            "vehicle_id": r.get("vehicle_tag", r.get("vehicle_id", "")),
        })
    return out

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching SF data...")

    all_features = []
    fetch_jobs = [
        ("Crime",        fetch_crime),
        ("311",          fetch_311),
        ("Permits",      fetch_permits),
        ("Inspections",  fetch_inspections),
        ("Transit",      fetch_transit),
    ]

    counts = {}
    for label, fn in fetch_jobs:
        try:
            items = fn()
            all_features.extend(items)
            counts[label] = len(items)
            print(f"  ✓ {label}: {len(items)} records")
        except Exception as e:
            print(f"  ✗ {label}: {e}")
            counts[label] = 0

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_at_local": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "counts": counts,
        "total": len(all_features),
        "features": all_features,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/sf_live.json", "w") as f:
        json.dump(output, f)

    print(f"\n✓ Saved {len(all_features)} total features → data/sf_live.json")
    print(f"  Counts: {counts}")

if __name__ == "__main__":
    main()
