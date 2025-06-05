from flask import Flask, render_template, abort
import pandas as pd

app = Flask(__name__)

# Cargar el excel
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

df = df.dropna(subset=['codigo', 'descripcion','status', 'marca', 'fecha', 'precio', 'preciom2'])
df['codigo'] = df['codigo'].astype(str)

@app.route('/<codigo>')
def producto(codigo):
    producto = df[df['codigo'] == codigo]

# Convertir a string formateado si es datetime
    if 'ultima_fecha' in df.columns:
        df['ultima_fecha'] = pd.to_datetime(df['ultima_fecha'], errors='coerce').dt.strftime('%d/%m/%Y')
    if producto.empty:

        return render_template('error.html', codigo=codigo), 404

    item = producto.iloc[0]
    return render_template('producto.html', item=item)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
	