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
  - `/muestra/<codigo>` or `/muestras/<codigo>` → `templates/producto_muestra.html` — sample label, only renders if `Muestra == "SI"` and `precio_muestra` is set. Simpler than the main label: no promo banners, no "antes/con_descuento" branch — shows base fields, `stock_muestra` (as "Stock Disponible Muestra"), the regular current price, then `descuento_muestra` and `precio_muestra`.

**Excel data source**: `etiquetas.xlsm` — this file is updated regularly (daily stock commits, see below). Column mappings are defined in the `df.rename()` call at the top of `app.py`. If the Excel adds new columns, add them to that rename dict.

**Templates** use Jinja2 with Bootstrap 5.3 and a black background. Promotional banners (Promo Julio, Casacor 2026) are conditionally shown based on the `promo` and `casacor` flags from the Excel.

## Key Data Flags (from Excel)

| Excel column | Python name | Values |
|---|---|---|
| `CON DESCUENTO` | `con_descuento` | `"SI"` / `"-"` — no longer used to trigger the Precio Antes/Actual block in `producto.html` (condition is commented out, kept for possible future reuse) |
| `STATUS` | `status` | e.g. `"PRODUCTO DESCONTINUADO"`, `"PRODUCTO DE LINEA"`, `"PRODUCTO BAJO PEDIDO"` — when `"PRODUCTO DESCONTINUADO"`, forces the Precio Antes/Actual + % Descuento block in `producto.html` |
| `PROMO` | `promo` | `"PROMO JULIO"` / `"NO"` — when `"PROMO JULIO"`, also forces the Precio Antes/Actual + % Descuento block (same trigger as `status == "PRODUCTO DESCONTINUADO"`) |
| `CASACOR` | `casacor` | `"SI"` / `"-"` |
| `muestra` | `muestra` | `"SI"` / `"-"` |
| `precio muestra` | `precio_muestra` | number, formatted via `formatear_precio` |
| `descuento muestra` | `descuento_muestra` | number/percent, formatted via `formatear_porcentaje` |
| `stock muestra` | `stock_muestra` | number; negative values are blanked out, same as `stock` |

## Stock Update Automation

`actualizar_stock.py` (run via `ejecutar_actualizacion.bat`) is a local Windows-only workflow, not part of the Flask app, that keeps `etiquetas.xlsm` and the deployment in sync:

1. Opens `etiquetas.xlsm` via COM automation (`win32com.client`), runs the update macro/button on the `DISEÑO` sheet, and waits for Excel's background query to finish.
2. Finds the `ULTIMA ACTUALIZACION DE STOCK` column by its header text (not a fixed column letter — this previously broke when columns were reordered), stamps it (rows `2:n`) with the current date/time as a real Excel date value (avoids day/month locale-parsing bugs from writing plain text), and saves the workbook.
3. Runs `git add . && git commit -m "Stock {day}/{month} {hour}" && git push origin main` (see recent commit history for this pattern).

These files are gitignored (local-only) but present in the working directory; `log_actualizacion.txt` is the run log. Since `app.py` only loads the Excel at startup, a push via this script requires a Render redeploy/restart to take effect (see Deployment below).

## Deployment

Hosted on Render (inferred from `gunicorn` + `host='0.0.0.0', port=10000`). The app reloads Excel only on restart — after updating `etiquetas.xlsm`, redeploy or restart the server.
