# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask web app that generates product label pages for Tumpar LTDA. It reads product data from `etiquetas.xlsm` at startup and serves dynamically rendered HTML labels at `/<codigo>` and `/muestra/<codigo>`.

## Running the App

```bash
# Development (uncomment the last 2 lines in app.py first)
python app.py

# Production
gunicorn app:app
```

Install dependencies: `pip install -r requirements.txt`

## Architecture

**Single file app** — all logic is in `app.py`:

- **Startup**: Excel is loaded once into a global `df` DataFrame. Columns are renamed, flag columns are guaranteed to exist, and date columns are parsed.
- **`preparar_item(codigo)`**: Core helper that looks up a product by code, sanitizes NaN values, formats prices/percentages/dates, and returns `(item, fecha_str, stock_fecha_str)`.
- **Routes**:
  - `/<codigo>` → `templates/producto.html` — main label
  - `/muestra/<codigo>` or `/muestras/<codigo>` → `templates/producto_muestra.html` — sample label, only renders if `Muestra == "SI"` and `precio_muestra` is set

**Excel data source**: `etiquetas.xlsm` — this file is updated regularly (daily stock commits). Column mappings are defined in the `df.rename()` call at the top of `app.py`. If the Excel adds new columns, add them to that rename dict.

**Templates** use Jinja2 with Bootstrap 5.3 and a black background. Promotional banners (Galponazo, Casacor 2026) are conditionally shown based on the `promo` and `casacor` flags from the Excel.

## Key Data Flags (from Excel)

| Excel column | Python name | Values |
|---|---|---|
| `CON DESCUENTO` | `con_descuento` | `"SI"` / `"-"` |
| `PROMO` | `promo` | `"GALPONAZO"` / `"-"` |
| `CASACOR` | `casacor` | `"SI"` / `"-"` |
| `Muestra` | `muestra` | `"SI"` / `"-"` |

## Deployment

Hosted on Render (inferred from `gunicorn` + `host='0.0.0.0', port=10000`). The app reloads Excel only on restart — after updating `etiquetas.xlsm`, redeploy or restart the server.
