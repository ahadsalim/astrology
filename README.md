# Nojoom Atlas

Persian natal-chart and transit web app powered by **Swiss Ephemeris**. Built for real chart work: Jalali birth input, Iranian cities, house tables, aspects, chart-wheel rendering, and AI-assisted interpretation prompts.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-black.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-see%20repo-lightgrey.svg)](#license)

## Features

- Natal charts, solar return, and live transits
- Jalali → Gregorian/UTC conversion with Iran timezone / DST handling
- Traditional dignities, house meanings, aspects, and Vedic special states
- Circular chart wheel (matplotlib) and print-friendly HTML tables
- Built-in prompt builder for birth and transit analysis
- Optional OpenAI-compatible AI simplify / analysis (`API_KEY` + `API_URL`)
- SQLite archive for charts and Iranian city CRUD admin

## Stack

Python 3.10+ · Flask · pyswisseph · jdatetime / pytz · matplotlib / numpy · OpenAI-compatible client · SQLite

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # set API_KEY / SECRET_KEY as needed
python app.py
```

Open `http://localhost:5000`.

Core Swiss Ephemeris flows work without an API key. AI routes need `API_KEY` and `API_URL` in `.env`.

## Project layout

```text
app.py            Flask entrypoint and routes
config.py         Environment settings
database.py       SQLite layer
prompts.py        Analysis prompts
core/             Ephemeris engine, houses, dignities, chart render
utils/            Calculators, validators, formatters
services/         AI client
data/             Iranian cities seed data
templates/        Web UI (RTL / Persian)
static/           CSS and Vazirmatn fonts
doc/              Deeper docs and changelog
```

## Main routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Home |
| `POST` | `/calculate` | Natal + solar return |
| `POST` | `/calculate-transit` | Live transit vs natal |
| `POST` | `/view-prompt` | Build natal analysis prompt |
| `POST` | `/view-transit-prompt` | Build transit analysis prompt |
| `POST` | `/simplify` | Simplify analysis text (AI) |
| `POST` | `/save` | Persist chart |
| `GET` | `/charts`, `/chart/<id>` | Archive |
| `GET` | `/cities-admin` | City admin UI |
| `GET/POST/PUT/DELETE` | `/api/cities` | Cities API |

## Configuration

Copy `.env.example` to `.env`. Important keys:

- `API_KEY`, `API_URL` — OpenAI-compatible gateway
- `ASTRO_MODEL`, `SIMPLIFY_MODEL`
- `SECRET_KEY`, `HOST`, `PORT`, `FLASK_DEBUG`

Keep `FLASK_DEBUG=False` in production and never commit `.env`.

## Docs

- `doc/README.md`
- `doc/CHANGELOG.md`
- `doc/IRAN_DST_DOCUMENTATION.md`
- `doc/PROFESSIONAL_ASTRO_README.md`
- `doc/analysis.md`

## Author

[Ahad Salim](https://github.com/ahadsalim) · [Tejarat Chat](https://www.tejarat.chat) · [mihanict.com](https://www.mihanict.com)

## License

No license file yet. Add one (e.g. MIT) if you want others to reuse the code clearly.
