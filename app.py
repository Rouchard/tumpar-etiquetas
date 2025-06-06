from flask import Flask, render_template, abort
import pandas as pd

app = Flask(__name__)

# Cargar el Excel
df = pd.read_excel('etiquetas.xlsm', engine='openpyxl')

# Renombrar columnas para uso en código
df.columns = df.columns.str.strip()  # elimina espacios
df = df.rename(columns={
    'COD. ARTICULO': 'codigo',
    'DESCRIPCION': 'descripcion',
    'MARCA': 'marca',
    'STATUS': 'status', 
    'Ultima fecha de ingreso': 'fecha',
    'PRECIO RETAIL CAJA': 'precio',
    'PRECIO RETAIL M2/PZA': 'preciom2'
})

# No eliminamos las filas con NaN en fecha
df = df.dropna(subset=['codigo', 'descripcion','status', 'marca', 'precio', 'preciom2'])

# Conversión de columnas
df['codigo'] = df['codigo'].astype(str)
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

@app.route('/<codigo>')
def producto(codigo):
    producto = df[df['codigo'] == codigo]

    if producto.empty:
        return render_template('error.html', codigo=codigo), 404

    item = producto.iloc[0]

    # Formatear la fecha como string segura para Jinja2
    if pd.isna(item.fecha):
        item_fecha_str = None
    else:
        # Convertir a Timestamp seguro
        fecha_timestamp = pd.to_datetime(item.fecha, errors='coerce')
        if pd.isna(fecha_timestamp):
            item_fecha_str = None
        else:
            item_fecha_str = fecha_timestamp.strftime('%d/%m/%Y')

    return render_template('producto.html', item=item, item_fecha_str=item_fecha_str)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)

