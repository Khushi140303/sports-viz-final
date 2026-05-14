<h1 align="center">Does Money Buy Wins? 🏀</h1>
<p align="center">
  <b>An interactive multi-view dashboard exploring the payroll-performance relationship across the NFL, NBA, and MLB (1990–2022), with an LLM chat interface for natural-language Q&A.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Plotly_Dash-3F4F75?style=flat&logo=plotly&logoColor=white">
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white">
  <img src="https://img.shields.io/badge/Groq-F55036?style=flat&logo=groq&logoColor=white">
  <img src="https://img.shields.io/badge/Llama_3.3-0467DF?style=flat&logoColor=white">
</p>

---

## What it does

An interactive dashboard that investigates whether financial investment translates into competitive success across three major US sports leagues over three decades. Five coordinated views, a 3D rotatable scatter plot, and an AI chat interface powered by Llama 3.3-70B let users drill into the data through both visual and conversational interfaces.

---

## Five views

| View | Description |
|---|---|
| **View 1** | Scatter plot — Payroll Rank vs. Win % with per-league regression overlays |
| **View 2** | Dual-axis time series — team payroll and win % over time (click-linked from View 1) |
| **View 3** | Heatmap — playoff rate by payroll quintile and league |
| **View 4** | 3D scatter — Payroll Rank × Season × Win % (rotatable, drag-to-explore) |
| **View 5** | AI chat — natural-language questions about the data, powered by Groq's Llama 3.3-70B |

---

## Tech stack

| Layer | Technology |
|---|---|
| Framework | Plotly Dash |
| Visualization | Plotly (incl. 3D scatter) |
| Data | NBA Payroll, NBA Player Stats, NBA Salaries, NFL Salary by Position, MLB Team Stats |
| Compute | Pandas |
| LLM | Llama 3.3-70B via the Groq API |

---

## What's interesting about this build

**LLM integration for data Q&A.** View 5 lets users ask natural-language questions about the dataset and get grounded responses powered by Llama 3.3-70B via Groq's inference API. Suggested-question pills make it easy to get started; the chat is integrated directly into the Dash app rather than living in a separate page.

**Click-linked coordinated views.** Clicking a dot in View 1 (Payroll Rank vs. Win %) updates View 2 (the team's payroll and win % over time) so the user can drill into a single team's history without losing context.

**3D dimension.** View 4 adds the temporal dimension to the payroll-performance relationship, letting users rotate the scatter to see how the NBA's payroll effect has strengthened over time vs. the NFL's salary cap flattening it.

---

## Key findings

- **NBA** shows the strongest payroll-performance correlation: top spenders win **76%** of games vs. **27%** for the lowest-spending teams
- **NFL** shows the weakest correlation (**70%** vs. **34%**), thanks to its hard salary cap
- **MLB** sits in the middle (**69%** vs. **31%**) with a soft luxury tax structure
- The 3D view reveals that the NBA's payroll effect has **strengthened over time** while the NFL's has remained flat

---

## Run it locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Groq API key (free at console.groq.com)
export GROQ_API_KEY="your_groq_api_key_here"
# On Windows: set GROQ_API_KEY=your_groq_api_key_here

# 3. Make sure all CSV/XLSX data files are in the same folder

# 4. Run
python sports_viz.py
```

Open `http://localhost:8050`.

---

## Data sources

| File | Source |
|---|---|
| `NBA Payroll(1990-2023).csv` | Kaggle: `loganlauton/nba-players-and-team-data` |
| `Games.csv` | Kaggle: `loganlauton/nba-players-and-team-data` |
| `NFL Salary By Position Group.xlsx` | Kaggle: NFL salary dataset |
| `mlb_teams.csv` | Kaggle: MLB team stats dataset |

---

## Built for

NYU **CS-GY 6313 — Information Visualization** · Final Project · *Author: Khushi Agarwal*
