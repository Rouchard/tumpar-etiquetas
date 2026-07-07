from flask import Flask, render_template, abort
import pandas as pd

app = Flask(__name__)

# Cargar el Excel
df = pd.read_excel('etiquetas.xlsm', engine='openpyxl')

# Renombrar columnas para uso en código
df.columns = df.columns.str.strip()
df = df.rename(columns={
    'COD. ARTICULO': 'codigo',
    'DESCRIPCION': 'descripcion',
    'MARCA': 'marca',
    'STATUS': 'status', 
    'Ultima fecha de ingreso': 'fecha',
    'PRECIO RETAIL CAJA ANTES': 'precio_antes',
    'PRECIO RETAIL M2/PZA ANTES': 'preciom2_antes',
    'PRECIO RETAIL CAJA ACTUAL': 'precio',
    'PRECIO RETAIL M2/PZA ACTUAL': 'preciom2',
    'DESCUENTO': 'descuento',
    'UNIDAD MEDIDA': 'unidad',
    'CONV-PZ-TONO': 'detalle',
    'DISPONIBLE VENTA M2/PZA': 'stock',
    'ULTIMA ACTUALIZACION DE STOCK': 'stock_actualizado',
    'CON DESCUENTO': 'con_descuento',
    'PROMO': 'promo',
    'CASACOR': 'casacor',

    # Nuevas columnas para etiqueta de muestra
    'muestra': 'muestra',
    'precio muestra': 'precio_muestra',
    'descuento muestra': 'descuento_muestra',
    'stock muestra': 'stock_muestra'
})

# Asegurar que las columnas existan aunque el Excel no las tenga
for col in ['con_descuento', 'promo', 'muestra', 'precio_muestra', 'descuento_muestra', 'stock_muestra', 'casacor']:
    if col not in df.columns:
        df[col] = "-"
    else:
        df[col] = df[col].fillna("-").astype(str).str.strip()

# Conversión de columnas
df['codigo'] = df['codigo'].astype(str)
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df['stock_actualizado'] = pd.to_datetime(df['stock_actualizado'], errors='coerce')


def formatear_porcentaje(valor_original):
    try:
        if valor_original == "-":
            return "-"

        valor_txt = str(valor_original).strip()

        if valor_txt == "" or valor_txt.lower() == "nan":
            return "-"

        # Soporta valores como "70%", "70", "0.7", "0,7"
        valor_txt = valor_txt.replace("%", "").strip()
        valor_txt = valor_txt.replace(",", ".")

        valor = float(valor_txt)

        # Si viene como 0.7, se convierte a 70%
        if valor <= 1:
            valor = valor * 100

        return f"{valor:.0f}%"
    except:
        return "-"


def formatear_precio(valor_original):
    try:
        if valor_original == "-":
            return "-"

        valor_txt = str(valor_original).strip()

        if valor_txt == "" or valor_txt.lower() == "nan":
            return "-"

        valor_txt = valor_txt.replace(",", ".")
        valor = float(valor_txt)

        return f"{valor:.1f}"
    except:
        return "-"


def preparar_item(codigo):
    producto = df[df['codigo'] == codigo]

    if producto.empty:
        return None, None, None

    item = producto.iloc[0]

    # Reemplazar NaN con "-" excepto fechas
    item = item.where(pd.notna(item), "-")

    # Si el stock es negativo, mostrar campo vacío
    if 'stock' in item and item['stock'] != "-":
        try:
            valor_stock = float(item['stock'])
            if valor_stock < 0:
                item['stock'] = ""
        except:
            item['stock'] = ""

    # Si el stock de muestra es negativo, mostrar campo vacío
    if 'stock_muestra' in item and item['stock_muestra'] != "-":
        try:
            valor_stock_muestra = float(item['stock_muestra'])
            if valor_stock_muestra < 0:
                item['stock_muestra'] = ""
        except:
            item['stock_muestra'] = ""

    # Formatear descuento normal
    item['descuento'] = formatear_porcentaje(item.get('descuento', '-'))

    # Formatear descuento de muestra
    item['descuento_muestra'] = formatear_porcentaje(item.get('descuento_muestra', '-'))

    # Formatear precio muestra
    item['precio_muestra'] = formatear_precio(item.get('precio_muestra', '-'))

    # Formateo de fecha de ingreso
    item_fecha_str = None
    if item['fecha'] != "-" and pd.notna(item['fecha']):
        try:
            fecha_timestamp = pd.to_datetime(item['fecha'], errors='coerce')
            if pd.notna(fecha_timestamp):
                item_fecha_str = fecha_timestamp.strftime('%d/%m/%Y')
        except Exception:
            item_fecha_str = None

    # Formateo de fecha de stock actualizado con hora
    item_stock_fecha_str = None
    if item.get('stock_actualizado') != "-" and pd.notna(item.get('stock_actualizado')):
        try:
            stock_fecha_timestamp = pd.to_datetime(item['stock_actualizado'], errors='coerce', dayfirst=True)
            if pd.notna(stock_fecha_timestamp):
                item_stock_fecha_str = stock_fecha_timestamp.strftime('%d/%m/%Y %H:%M')
        except:
            item_stock_fecha_str = None

    return item, item_fecha_str, item_stock_fecha_str


@app.route('/<codigo>')
def producto(codigo):
    item, item_fecha_str, item_stock_fecha_str = preparar_item(codigo)

    if item is None:
        return render_template('error.html', codigo=codigo), 404

    return render_template(
        'producto.html',
        item=item,
        item_fecha_str=item_fecha_str,
        item_stock_fecha_str=item_stock_fecha_str
    )


@app.route('/muestra/<codigo>')
@app.route('/muestras/<codigo>')
def producto_muestra(codigo):
    item, item_fecha_str, item_stock_fecha_str = preparar_item(codigo)

    if item is None:
        return render_template('error.html', codigo=codigo), 404

    # Validar columna Muestra
    muestra = str(item.get('muestra', '-')).strip().upper()

    if muestra != "SI":
        return render_template('error.html', codigo=codigo), 404

    # Validar Precio muestra
    if not item.get('precio_muestra') or item.get('precio_muestra') == "-":
        return render_template('error.html', codigo=codigo), 404

    return render_template(
        'producto_muestra.html',
        item=item,
        item_fecha_str=item_fecha_str,
        item_stock_fecha_str=item_stock_fecha_str
    )


# Descomentar estas lineas para hacer pruebas locales
#if __name__ == '__main__':
#   app.run(host='0.0.0.0', port=10000, debug=True)