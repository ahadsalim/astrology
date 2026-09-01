# Nojoom Atlas

Persian natal-chart and transit web app powered by **Swiss Ephemeris**. Built for real chart work: Jalali birth input, Iranian cities, house tables, aspects, chart-wheel rendering, and AI-assisted house-by-house interpretation.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-black.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-see%20repo-lightgrey.svg)](#license)

## Features

- Cosmic RTL UI (Persian-first) with natal, solar return, and live transits
- Jalali → Gregorian/UTC conversion with Iran timezone / DST handling
- Traditional dignities, house meanings, aspects, and Vedic special states
- Circular chart wheel (matplotlib) and print-friendly HTML tables
- House-by-house prompt builder (houses 1–12, occupants, cusp rulers)
- Optional OpenAI-compatible AI analysis via Agnes (default) or GapGPT Luna
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

Core Swiss Ephemeris flows work without an API key. The app boots even if `API_KEY` is unset; AI buttons then show a Persian “add your key” message.

## Project layout

```text
app.py            Flask entrypoint and routes
config.py         Environment settings
database.py       SQLite layer
prompts.py        House-by-house analysis prompts
core/             Ephemeris engine, houses, dignities, chart render
utils/            Calculators, validators, formatters
services/         AI client (lazy OpenAI-compatible)
data/             Iranian cities seed data
templates/        Web UI (RTL / Persian, cosmic theme)
static/           CSS and Vazirmatn fonts
doc/              Deeper docs and changelog
```

## Main routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Home |
| `POST` | `/calculate` | Natal + solar return |
| `POST` | `/calculate-transit` | Live transit vs natal |
| `POST` | `/view-prompt` | Build natal house-by-house prompt |
| `POST` | `/view-transit-prompt` | Build transit house-by-house prompt |
| `POST` | `/analyze` | AI natal analysis (JSON; needs `API_KEY`) |
| `POST` | `/analyze-transit` | AI transit analysis (JSON; needs `API_KEY`) |
| `POST` | `/simplify` | Simplify analysis text (AI; keeps house structure) |
| `POST` | `/save` | Persist chart |
| `GET` | `/charts`, `/chart/<id>` | Archive |
| `GET` | `/cities-admin` | City admin UI |
| `GET/POST/PUT/DELETE` | `/api/cities` | Cities API |

## Configuration

Copy `.env.example` to `.env`. Important keys:

- `API_KEY`, `API_URL` — OpenAI-compatible gateway
- `ASTRO_MODEL`, `SIMPLIFY_MODEL`
- `SECRET_KEY`, `HOST`, `PORT`, `FLASK_DEBUG`

Default provider is **Agnes AI** (free): `API_URL=https://apihub.agnes-ai.com/v1` with `agnes-2.0-flash`. Get a key at https://platform.agnes-ai.com/.

To use **GapGPT Luna** for simplification instead:

```env
API_URL=https://api.gapgpt.app/v1
ASTRO_MODEL=gpt-5.2
SIMPLIFY_MODEL=gpt-5.6-luna
```

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
