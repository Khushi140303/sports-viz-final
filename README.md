# Does Money Buy Wins?
### Visualizing the Payroll-Performance Relationship in NFL, NBA & MLB
**CS-GY 6313: Information Visualization - Final Project**
**Author: Khushi Agarwal | NYU Tandon School of Engineering**

---

## Overview

An interactive multi-view dashboard that explores whether financial investment
translates into competitive success across three major US sports leagues (NFL,
NBA, MLB) from 1990–2022. The system features coordinated views, a 3D
visualization, and an AI-powered chat interface for natural language queries.

---

## Features

| View | Description |
|------|-------------|
| View 1 | Scatter plot - Payroll Rank vs Win % with per-league regression overlays |
| View 2 | Dual-axis time series - team payroll and win % over time (click-linked) |
| View 3 | Heatmap - playoff rate by payroll quintile and league |
| View 4 | 3D scatter - Payroll Rank × Season × Win % (rotatable) |
| View 5 | AI chat - ask natural language questions about the data (powered by Groq) |

---

## Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies

---

## Installation

```bash
# 1. Clone or download this project folder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Groq API key (free at console.groq.com)
export GROQ_API_KEY="your_groq_api_key_here"

# On Windows:
set GROQ_API_KEY=your_groq_api_key_here
```

---

## Data Setup

Place the following files in the **same folder** as `sports_viz.py`:

| File | Source |
|------|--------|
| `NBA Payroll(1990-2023).csv` | Kaggle: loganlauton/nba-players-and-team-data |
| `Games.csv` | Kaggle: loganlauton/nba-players-and-team-data |
| `NFL Salary By Position Group.xlsx` | Kaggle: NFL salary dataset |
| `mlb_teams.csv` | Kaggle: MLB team stats dataset |

---

## Running the App

```bash
python sports_viz.py
```

Then open your browser and go to: **http://localhost:8050**

---

## Usage

- **Filter by League** - use checkboxes to show/hide NBA, NFL, MLB
- **Season Range** - drag the slider to filter by year range
- **Click a dot** in View 1 to update View 2 with that team's history
- **Team dropdown** in View 2 to manually select any team
- **Rotate** the 3D chart by clicking and dragging
- **Ask AI** - click a suggested question or type your own

---

## Project Structure

```
sports_viz/
├── sports_viz.py              # Main dashboard application
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── NBA Payroll(1990-2023).csv
├── Games.csv
├── NFL Salary By Position Group.xlsx
└── mlb_teams.csv
```

---

## Dependencies

```
dash==2.14.0
plotly==5.18.0
pandas==2.1.0
requests==2.31.0
openpyxl==3.1.2
```

---

## Key Findings

- **NBA** shows the strongest payroll-performance correlation: top spenders
  win 76% of games vs 27% for lowest spenders
- **NFL** shows the weakest correlation (70% vs 34%) due to its hard salary cap
- **MLB** sits in the middle (69% vs 31%) with a soft luxury tax structure
- The 3D view reveals that the NBA's payroll effect has strengthened over time

---

## Bonus Features

- **3D Visualization** (View 4): interactive rotatable scatter plot adding
  the time dimension
- **AI Integration** (View 5): natural language Q&A powered by
  Llama 3.3-70B via Groq API
