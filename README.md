[中文](README_CN.md) · **English**

---

# DailyCheck · Local Habit Tracker

A personal habit check-in app that runs entirely on your machine — no account, no internet connection, no cloud. Your data stays yours.

---

## Features

**Check-in Core**

- One check-in per day, with automatic streak counting (`day1`, `day2`, `day3` …)
- Missing a day or clicking "Skip" resets the streak back to `day0`
- Optional text notes when checking in or skipping
- Edit or delete any record — past or present — for corrections

**History**

- **List view** — all records in reverse-chronological order, with inline editing and deletion
- **Heatmap calendar** — GitHub-style contribution grid where deeper green means a longer streak
  - **Year view** — full 52-week grid, cell size adapts to container width
  - **Month view** — natural calendar grid with day numbers inside each cell
  - **Custom range** — `auto-fill` grid that adapts to any span of time
  - Toggle between Monday and Sunday week start
  - Hover tooltip showing status, streak, and note for any day
  - Live stats badge showing checked days out of total

**Data Management**

- One-click export of all records as a JSON file
- Import from JSON with **Merge** or **Replace** mode
- Migration script (`convert.py`) for converting legacy `.txt` records to the standard format

**Interface**

- Responsive layout: sidebar + two-column view on desktop, bottom tab bar on mobile
- Instant feedback with Toast notifications and loading overlay

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 · Flask · flask-cors |
| Frontend | Vue 3 (CDN) · Tailwind CSS (CDN) · Day.js · Font Awesome |
| Storage | Local JSON file (`checkin_data.json`) |
| Dependencies | No database · No cloud · No build tools |

---

## Quick Start

**1. Clone the repository**

```bash
git clone https://github.com/your-username/dailycheck.git
cd dailycheck
```

**2. Install backend dependencies**

```bash
pip install flask flask-cors
```

**3. Start the server**

```bash
python app.py
```

**4. Open your browser**

Visit [http://localhost:8191](http://localhost:8191) and start checking in.

---

## Project Structure

```
dailycheck/
├── app.py              # Flask backend — all REST API endpoints
├── checkin_data.json   # Data file (auto-created on first check-in)
├── convert.py          # Legacy format migration script
└── static/
    └── index.html      # Frontend single-file app
```

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/status` | Today's status and current streak |
| `GET` | `/api/records` | All records (optional `?start=` `?end=` filters) |
| `POST` | `/api/checkin` | Check in for today |
| `POST` | `/api/skip` | Skip today (resets streak) |
| `PUT` | `/api/records/:date` | Update a specific date's record |
| `DELETE` | `/api/records/:date` | Delete a specific date's record |
| `GET` | `/api/export` | Export all data as JSON |
| `POST` | `/api/import` | Import JSON data (`merge` / `replace`) |

---

## Data Format

`checkin_data.json` uses a straightforward structure you can read and edit with any text editor:

```json
{
  "records": {
    "2025-01-08": {
      "checked": true,
      "note": "Finished today's tasks",
      "streak": 7,
      "timestamp": "2025-01-08T09:30:00",
      "updated_at": null
    },
    "2025-01-09": {
      "checked": false,
      "note": "",
      "streak": 0,
      "timestamp": "2025-01-09T22:00:00",
      "updated_at": null
    }
  }
}
```

- `checked: true` — checked in that day
- `checked: false` — explicitly skipped that day
- Date absent from `records` — missed (no action taken)
- `streak` — consecutive check-in days up to and including that date; `0` means the streak was broken

---

## Migrating Legacy Data

If you have historical records in the following format (`input.txt`):

```
## 2024
10.01 day0
10.02 day1
10.03 day2（Finished today's tasks）

## 2025
01.01 day0
01.02 day1
```

Run the migration script to produce a standard `checkin_data.json`:

```bash
python convert.py
```

Format rules:

- `MM.DD dayN` — N > 0 means checked in; N = 0 means skipped
- `MM.DD dayN（note）` — note wrapped in **fullwidth parentheses** `（）`
- `MM.DD` with no day info — missing data, skipped during conversion

---

## License

[GPLv3](LICENSE)
