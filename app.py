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
    'DESCUENTO' : 'descuento',
    'UNIDAD MEDIDA': 'unidad',
    'CONV-PZ-TONO': 'detalle',
    'DISPONIBLE VENTA M2/PZA': 'stock',
    'ULTIMA ACTUALIZACION DE STOCK': 'stock_actualizado',
    'CON DESCUENTO': 'con_descuento',
    'PROMO': 'promo' 
})
# Asegurar que las nuevas columnas existan aunque el Excel no las tenga
for col in ['con_descuento', 'promo']:
    if col not in df.columns:
        df[col] = "-"
    else:
        # Rellenar valores vacíos con "-"
        df[col] = df[col].fillna("-").astype(str).str.strip()

# Conversión de columnas
df['codigo'] = df['codigo'].astype(str)
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df['stock_actualizado'] = pd.to_datetime(df['stock_actualizado'], errors='coerce')

@app.route('/<codigo>')
def producto(codigo):
    producto = df[df['codigo'] == codigo]

    if producto.empty:
        return render_template('error.html', codigo=codigo), 404

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


    # Formatear el campo 'descuento' como "30%" (entero con símbolo)
    if item['descuento'] != "-":
        try:
            valor = float(item['descuento'])
            item['descuento'] = f"{valor:.0f}%"
        except:
            item['descuento'] = "-"

    # Formateo de fecha de ingreso
    item_fecha_str = None
    if item['fecha'] != "-" and pd.notna(item['fecha']):
        try:
            fecha_timestamp = pd.to_datetime(item['fecha'], errors='coerce')
            if pd.notna(fecha_timestamp):
                item_fecha_str = fecha_timestamp.strftime('%d/%m/%Y')
        except Exception:
            item_fecha_str = None

    # Formateo de fecha de stock actualizado (con hora)
    item_stock_fecha_str = None
    if item.get('stock_actualizado') != "-" and pd.notna(item.get('stock_actualizado')):
        try:
            stock_fecha_timestamp = pd.to_datetime(item['stock_actualizado'], errors='coerce', dayfirst=True)
            if pd.notna(stock_fecha_timestamp):
                item_stock_fecha_str = stock_fecha_timestamp.strftime('%d/%m/%Y %H:%M')
        except:
            item_stock_fecha_str = None


    return render_template('producto.html', item=item, item_fecha_str=item_fecha_str, item_stock_fecha_str=item_stock_fecha_str)

# Descomentar estas lineas para hacer pruebas locales
#if __name__ == '__main__':
#   app.run(host='0.0.0.0', port=10000, debug=True)