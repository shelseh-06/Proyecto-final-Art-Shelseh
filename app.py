import os
import pymysql
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.urandom(24).hex()

ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'shelseh123')

DB_CONFIG = {
    'host': os.environ.get('MYSQLHOST', 'localhost'),
    'user': os.environ.get('MYSQLUSER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD', ''),
    'database': os.environ.get('MYSQLDATABASE', 'art_shelseh'),
    'port': int(os.environ.get('MYSQLPORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


def get_db():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.err.OperationalError as e:
        print(f"ERROR: No se pudo conectar a MySQL. Asegúrate de que XAMPP/MAMP/MySQL esté corriendo.")
        print(f"Detalle: {e}")
        return None


def init_db():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS art_shelseh CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()
    except pymysql.err.OperationalError:
        pass

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL UNIQUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                precio DECIMAL(10,2) NOT NULL,
                categoria_id INT,
                imagen VARCHAR(300),
                badge VARCHAR(50),
                FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                email VARCHAR(200) NOT NULL,
                tipo VARCHAR(100),
                descripcion TEXT,
                telefono VARCHAR(20),
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado VARCHAR(20) DEFAULT 'pendiente'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

        try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN telefono VARCHAR(20) AFTER descripcion")
        except pymysql.err.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE pedidos DROP COLUMN presupuesto")
        except pymysql.err.OperationalError:
            pass

        cursor.execute('SELECT COUNT(*) AS total FROM categorias')
        if cursor.fetchone()['total'] == 0:
            cursor.execute("INSERT INTO categorias (nombre) VALUES ('Maquetas'), ('Manualidades')")

            productos = [
                ('Maqueta del Sistema Solar', 'Maqueta educativa del sistema solar con planetas pintados a mano y detalles orbitales.', 85000.00, 1, 'img/Maqueta del sistema solar.jpeg', 'Popular'),
                ('Cartelera: El Romanticismo', 'Cartelera decorativa sobre el movimiento romántico con ilustraciones y textos detallados.', 42000.00, 2, 'img/Cartelera sobre el romanticismo.jpeg', 'Nuevo'),
                ('Cartelera: Buenos Modales', 'Cartelera educativa sobre etiqueta y buenos modales con diseño colorido y llamativo.', 38000.00, 2, 'img/Cartelera sobre los buenos modales.jpeg', None),
                ('Cartelera: Paulo Freire', 'Cartelera dedicada al pedagogo Paulo Freire con sus principales ideas y aportes.', 40000.00, 2, 'img/Cartelera sobre Paulo Freire.jpeg', None),
                ('Lapbook: Querido Hijo', 'Lapbook interactivo sobre la obra "Querido hijo estamos en huelga" con solapas y textos.', 55000.00, 1, 'img/Lapbook sobre la obra-Querido hijo estamos en huelga.jpeg', None),
                ('Lapbook: Querido Hijo II', 'Segunda parte del lapbook con más detalles, ilustraciones y contenido literario.', 60000.00, 1, 'img/Lapbook sobre la obra-Querido hijo estamos en huelga 2.jpeg', 'Encargo'),
                ('Portadas de Cuadernos', 'Portadas decorativas y personalizadas para cuadernos, hechas con técnicas manuales.', 25000.00, 2, 'img/Portadas de cuadernos.jpeg', None),
                ('Maqueta Sistema Solar II', 'Vista detallada de la maqueta del sistema solar con acabados en relieve y colores vibrantes.', 90000.00, 1, 'img/Maqueta del sistema solar  2.jpeg', 'Popular'),
            ]
            cursor.executemany(
                'INSERT INTO productos (nombre, descripcion, precio, categoria_id, imagen, badge) VALUES (%s, %s, %s, %s, %s, %s)',
                productos
            )

    conn.commit()
    conn.close()


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM categorias')
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)


@app.route('/api/productos', methods=['GET'])
def get_productos():
    conn = get_db()
    with conn.cursor() as cursor:
        categoria = request.args.get('categoria')
        if categoria:
            cursor.execute('''
                SELECT p.*, c.nombre AS categoria
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
                WHERE c.nombre = %s
            ''', (categoria,))
        else:
            cursor.execute('''
                SELECT p.*, c.nombre AS categoria
                FROM productos p
                JOIN categorias c ON p.categoria_id = c.id
            ''')
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)


@app.route('/api/productos/<int:producto_id>', methods=['GET'])
def get_producto(producto_id):
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('''
            SELECT p.*, c.nombre AS categoria
            FROM productos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE p.id = %s
        ''', (producto_id,))
        row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({'error': 'Producto no encontrado'}), 404


@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    email = data.get('email', '').strip()
    if not nombre or not email:
        return jsonify({'error': 'Nombre y email son requeridos'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'No hay conexión con la base de datos. Verifica que MySQL esté corriendo.'}), 500
    with conn.cursor() as cursor:
        cursor.execute(
            'INSERT INTO pedidos (nombre, email, tipo, descripcion, telefono) VALUES (%s, %s, %s, %s, %s)',
            (nombre, email, data.get('tipo'), data.get('descripcion'), data.get('telefono'))
        )
    conn.commit()
    conn.close()
    return jsonify({'mensaje': f'Gracias, {nombre}! Tu pedido fue registrado.'}), 201


@app.route('/api/pedidos', methods=['GET'])
def get_pedidos():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM pedidos ORDER BY fecha DESC')
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)


@app.route('/api/pedidos/<int:pedido_id>/estado', methods=['PUT'])
def actualizar_estado(pedido_id):
    data = request.get_json()
    estado = data.get('estado')
    if estado not in ('pendiente', 'en_proceso', 'completado', 'cancelado'):
        return jsonify({'error': 'Estado no válido'}), 400
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('UPDATE pedidos SET estado = %s WHERE id = %s', (estado, pedido_id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Estado actualizado'})


# ---------- ADMIN PANEL ----------

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('user', '')
        pwd = request.form.get('pass', '')
        if user == ADMIN_USER and pwd == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return '''
            <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin - ART SHELSEH</title>
            <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;500&display=swap" rel="stylesheet">
            <style>
              *{margin:0;padding:0;box-sizing:border-box}
              body{font-family:'Inter',sans-serif;background:#fdf7f4;display:flex;align-items:center;justify-content:center;min-height:100vh}
              .card{background:#fff;border-radius:20px;padding:40px;box-shadow:0 10px 40px rgba(201,137,154,.15);max-width:380px;width:100%;text-align:center}
              h1{font-family:'Playfair Display',serif;color:#c9899a;font-size:1.6rem;margin-bottom:4px}
              p{color:#8d7280;font-size:.85rem;margin-bottom:24px}
              .error{background:#fdeeee;color:#a34a4a;padding:10px;border-radius:10px;font-size:.8rem;margin-bottom:16px}
              input{width:100%;padding:12px 14px;border:1px solid #f0dfd8;border-radius:10px;font-family:'Inter',sans-serif;font-size:.9rem;margin-bottom:14px;outline:none;background:#fdf7f4}
              input:focus{border-color:#c9899a;background:#fff}
              button{width:100%;padding:12px;background:#c9899a;color:#fff;border:none;border-radius:10px;font-family:'Inter',sans-serif;font-size:.85rem;font-weight:500;cursor:pointer}
              button:hover{background:#b97285}
            </style></head><body>
            <div class="card">
              <h1>ART SHELSEH</h1>
              <p>Panel de administración</p>
              <div class="error">Usuario o contraseña incorrectos</div>
              <form method="post">
                <input type="text" name="user" placeholder="Usuario" required>
                <input type="password" name="pass" placeholder="Contraseña" required>
                <button type="submit">Ingresar</button>
              </form>
            </div></body></html>
        '''
    return '''
        <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin - ART SHELSEH</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;500&display=swap" rel="stylesheet">
        <style>
          *{margin:0;padding:0;box-sizing:border-box}
          body{font-family:'Inter',sans-serif;background:#fdf7f4;display:flex;align-items:center;justify-content:center;min-height:100vh}
          .card{background:#fff;border-radius:20px;padding:40px;box-shadow:0 10px 40px rgba(201,137,154,.15);max-width:380px;width:100%;text-align:center}
          h1{font-family:'Playfair Display',serif;color:#c9899a;font-size:1.6rem;margin-bottom:4px}
          p{color:#8d7280;font-size:.85rem;margin-bottom:24px}
          input{width:100%;padding:12px 14px;border:1px solid #f0dfd8;border-radius:10px;font-family:'Inter',sans-serif;font-size:.9rem;margin-bottom:14px;outline:none;background:#fdf7f4;transition:.2s}
          input:focus{border-color:#c9899a;background:#fff}
          button{width:100%;padding:12px;background:#c9899a;color:#fff;border:none;border-radius:10px;font-family:'Inter',sans-serif;font-size:.85rem;font-weight:500;cursor:pointer;transition:.2s}
          button:hover{background:#b97285}
        </style></head><body>
        <div class="card">
          <h1>ART SHELSEH</h1>
          <p>Panel de administración</p>
          <form method="post">
            <input type="text" name="user" placeholder="Usuario" required>
            <input type="password" name="pass" placeholder="Contraseña" required>
            <button type="submit">Ingresar</button>
          </form>
        </div></body></html>
    '''


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = get_db()
    if not conn:
        return '<p>Error de conexión a la base de datos.</p>'

    with conn.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) AS total FROM productos')
        total_productos = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM productos WHERE categoria_id = 1')
        total_maquetas = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM productos WHERE categoria_id = 2')
        total_manualidades = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM pedidos')
        total_pedidos = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM pedidos WHERE estado = "pendiente"')
        pendientes = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM pedidos WHERE estado = "en_proceso"')
        en_proceso = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM pedidos WHERE estado = "completado"')
        completados = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) AS total FROM pedidos WHERE estado = "cancelado"')
        cancelados = cursor.fetchone()['total']

        cursor.execute('SELECT * FROM pedidos ORDER BY fecha DESC LIMIT 20')
        pedidos = cursor.fetchall()

        cursor.execute('SELECT * FROM productos ORDER BY nombre')
        productos = cursor.fetchall()

    conn.close()

    cards = f'''
    <div class="stats-grid">
      <div class="stat-card"><div class="num">{total_maquetas}</div><div class="lbl">Maquetas disponibles</div></div>
      <div class="stat-card"><div class="num">{total_manualidades}</div><div class="lbl">Manualidades disponibles</div></div>
      <div class="stat-card"><div class="num">{total_productos}</div><div class="lbl">Productos totales</div></div>
      <div class="stat-card"><div class="num">{total_pedidos}</div><div class="lbl">Pedidos totales</div></div>
      <div class="stat-card" style="border-left:4px solid #e9c3cd"><div class="num">{pendientes}</div><div class="lbl">Pendientes</div></div>
      <div class="stat-card" style="border-left:4px solid #b98a5e"><div class="num">{en_proceso}</div><div class="lbl">En proceso</div></div>
      <div class="stat-card" style="border-left:4px solid #5a9e5a"><div class="num">{completados}</div><div class="lbl">Completados</div></div>
      <div class="stat-card" style="border-left:4px solid #a08491"><div class="num">{cancelados}</div><div class="lbl">Cancelados</div></div>
    </div>'''

    pedidos_html = ''
    for p in pedidos:
        opts = ''
        for est in ['pendiente','en_proceso','completado','cancelado']:
            sel = 'selected' if p['estado'] == est else ''
            opts += f'<option value="{est}" {sel}>{est}</option>'
        pedidos_html += f'''
        <tr>
          <td>{p['id']}</td>
          <td>{p['nombre']}</td>
          <td>{p['email']}</td>
          <td>{p['telefono'] or ''}</td>
          <td>{p['tipo'] or ''}</td>
          <td>
            <select class="estado-select" data-id="{p['id']}" onchange="cambiarEstado(this)">
              {opts}
            </select>
          </td>
          <td style="font-size:.8rem">{p['fecha'].strftime('%d/%m/%Y') if p['fecha'] else ''}</td>
        </tr>'''

    productos_html = ''
    for prod in productos:
        precio = f"${prod['precio']:,.0f}".replace(',', '.')
        prod_cat = 'Maquetas' if prod['categoria_id'] == 1 else 'Manualidades'
        badge = f'<span style="font-size:.65rem;color:#c9899a">{prod["badge"]}</span>' if prod.get('badge') else ''
        productos_html += f'''
        <div class="product-card">
          <h4>{prod['nombre']}</h4>
          <div class="precio">{precio}</div>
          <div style="font-size:.7rem;color:#8d7280;margin-top:4px">{prod_cat} {badge}</div>
        </div>'''

    return f'''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Admin ART SHELSEH</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;500;600&display=swap" rel="stylesheet">
    <style>
      *{{margin:0;padding:0;box-sizing:border-box}}
      body{{font-family:'Inter',sans-serif;background:#fdf7f4;color:#3b2430}}
      .header{{background:#fff;border-bottom:1px solid #f0dfd8;padding:16px 32px;display:flex;align-items:center;justify-content:space-between}}
      .header h1{{font-family:'Playfair Display',serif;color:#c9899a;font-size:1.2rem;letter-spacing:2px}}
      .header a{{color:#8d7280;font-size:.8rem;text-decoration:none}}
      .header a:hover{{color:#c9899a}}
      .container{{max-width:1200px;margin:0 auto;padding:32px}}
      .stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:16px;margin-bottom:32px}}
      .stat-card{{background:#fff;border-radius:12px;padding:20px;border-left:4px solid #c9899a;box-shadow:0 2px 10px rgba(201,137,154,.08)}}
      .stat-card .num{{font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:#3b2430}}
      .stat-card .lbl{{font-size:.75rem;color:#8d7280;text-transform:uppercase;letter-spacing:1px}}
      h2{{font-family:'Playfair Display',serif;font-size:1.3rem;margin-bottom:16px;color:#3b2430}}
      table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(201,137,154,.08)}}
      th{{text-align:left;padding:12px 14px;font-size:.7rem;text-transform:uppercase;letter-spacing:1px;color:#8d7280;border-bottom:1px solid #f0dfd8}}
      td{{padding:10px 14px;font-size:.85rem;border-bottom:1px solid #fdf7f4}}
      tr:hover{{background:#fdf7f4}}
      .badge-pendiente{{background:#fff3cd;color:#856404;padding:3px 10px;border-radius:999px;font-size:.7rem;text-transform:uppercase}}
      .badge-en_proceso{{background:#e8d5b7;color:#7a5a2e;padding:3px 10px;border-radius:999px;font-size:.7rem;text-transform:uppercase}}
      .badge-completado{{background:#d4edda;color:#3f7a42;padding:3px 10px;border-radius:999px;font-size:.7rem;text-transform:uppercase}}
      .badge-cancelado{{background:#f8d7da;color:#a34a4a;padding:3px 10px;border-radius:999px;font-size:.7rem;text-transform:uppercase}}
      .estado-select{{font-size:.75rem;padding:4px 8px;border:1px solid #f0dfd8;border-radius:6px;background:#fff;color:#3b2430;cursor:pointer}}
      .estado-select[value="pendiente"]{{border-left:3px solid #e9c3cd}}
      .estado-select[value="en_proceso"]{{border-left:3px solid #b98a5e}}
      .estado-select[value="completado"]{{border-left:3px solid #5a9e5a}}
      .estado-select[value="cancelado"]{{border-left:3px solid #a08491}}
      .product-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin-top:16px}}
      .product-card{{background:#fff;border-radius:10px;padding:16px;border:1px solid #f0dfd8;font-size:.85rem}}
      .product-card h4{{font-family:'Playfair Display',serif;font-size:.95rem;margin-bottom:4px}}
      .product-card .precio{{color:#c9899a;font-weight:600;font-size:.9rem}}
    </style></head><body>
    <div class="header">
      <h1>ART SHELSEH · Admin</h1>
      <a href="/admin/logout">Cerrar sesión</a>
    </div>
    <div class="container">
      <h2>Resumen</h2>
      {cards}
      <h2>Últimos pedidos</h2>
      <table>
        <thead><tr><th>ID</th><th>Cliente</th><th>Email</th><th>Teléfono</th><th>Tipo</th><th>Estado</th><th>Fecha</th></tr></thead>
        <tbody>{pedidos_html}</tbody>
      </table>
      <h2 style="margin-top:32px">Catálogo de productos</h2>
      <div class="product-grid">{productos_html}<script>
    async function cambiarEstado(sel){{
      const id=sel.dataset.id, est=sel.value;
      try{{
        const res=await fetch(`/api/pedidos/${{id}}/estado`,{{method:'PUT',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{estado:est}})}});
        if(!res.ok) throw 0;
      }}catch{{sel.value=sel.getAttribute('data-old'); alert('Error al actualizar');}}
      sel.setAttribute('data-old',est);
    }}
    document.querySelectorAll('.estado-select').forEach(s=>s.setAttribute('data-old',s.value));
    </script>
    </body></html>'''


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
