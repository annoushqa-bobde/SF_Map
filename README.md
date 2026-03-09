# SF Pulse 🌉

**Live San Francisco city intelligence map — updated every hour, automatically.**

> Built with Python · GitHub Actions · Leaflet.js · SF OpenData

---

## What It Shows

Real-time data from 5 official SF government streams:

| Layer | Source | Update Frequency |
|---|---|---|
| 🚨 Crime | SF Police Department | Hourly |
| 📞 311 Requests | SF 311 | Hourly |
| 🏗️ Permits | SF Building Inspection | Hourly |
| 🍽️ Inspections | SF Dept of Public Health | Hourly |
| 🚌 Muni Transit | SFMTA | Hourly |

---

## Live Demo

👉 **[sfpulse.github.io](https://YOUR_USERNAME.github.io/sf-pulse)**

---

## Setup (5 minutes)

### 1. Fork this repository

### 2. Enable GitHub Pages
- Go to **Settings → Pages**
- Source: **Deploy from branch**
- Branch: **main**, folder: **/ (root)**
- Save

### 3. Enable GitHub Actions
- Go to **Actions** tab
- Click **"I understand my workflows, go ahead and enable them"**

### 4. Run the first data fetch
- Go to **Actions → Update SF Live Data**
- Click **"Run workflow"**
- Wait ~30 seconds

### 5. Visit your live map
```
https://YOUR_USERNAME.github.io/sf-pulse
```

That's it. The map now updates automatically every hour via GitHub Actions — completely free.

---

## How It Works

```
┌─────────────────────────────────────────────────┐
│  GitHub Actions (runs every hour, free)          │
│                                                   │
│  fetch_data.py                                    │
│    → hits 5 SF OpenData APIs                     │
│    → cleans + normalizes records                 │
│    → saves to data/sf_live.json                  │
│    → commits + pushes to repo                    │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  GitHub Pages (serves static files, free)        │
│                                                   │
│  index.html                                       │
│    → loads data/sf_live.json                     │
│    → renders Leaflet map with colored markers    │
│    → filter by layer, search by keyword          │
│    → click any marker for details                │
└─────────────────────────────────────────────────┘
```

---

## Tech Stack

- **Python** — data fetching + cleaning
- **GitHub Actions** — free hourly scheduler
- **GitHub Pages** — free static hosting
- **Leaflet.js** — interactive maps
- **SF OpenData API** — free, no API key needed

---

## Skills Demonstrated

- Data pipeline engineering
- REST API integration
- Automated scheduling (CI/CD)
- Geospatial data processing
- Frontend development
- Production deployment

---

*Built by [Your Name] — [LinkedIn] · [GitHub]*
