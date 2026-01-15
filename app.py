from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Configuración de la base de datos
def conectar():
    conn = sqlite3.connect('informatica.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear las tablas (Solo se ejecuta una vez)
def crear_tablas():
    db = conectar()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS profesores (id INTEGER PRIMARY KEY, nombre TEXT);
        CREATE TABLE IF NOT EXISTS estudiantes (id INTEGER PRIMARY KEY, cedula TEXT, nombre TEXT);
        CREATE TABLE IF NOT EXISTS materias (id INTEGER PRIMARY KEY, nombre TEXT, id_prof INTEGER);
        CREATE TABLE IF NOT EXISTS laboratorios (id INTEGER PRIMARY KEY, nombre TEXT);
        CREATE TABLE IF NOT EXISTS inscripciones (id INTEGER PRIMARY KEY, id_est INTEGER, id_mat INTEGER, id_lab INTEGER);
    ''')
    # Insertar un profesor y materia base si no existen
    if not db.execute("SELECT * FROM profesores").fetchone():
        db.execute("INSERT INTO profesores (nombre) VALUES ('Dr. Garcia')")
        db.execute("INSERT INTO materias (nombre, id_prof) VALUES ('Programacion', 1)")
        db.execute("INSERT INTO laboratorios (nombre) VALUES ('Lab A')")
    db.commit()
    db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    db = conectar()
    # AGREGAR: Si el usuario envía el formulario
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        cur = db.cursor()
        cur.execute("INSERT INTO estudiantes (cedula, nombre) VALUES (?, ?)", (cedula, nombre))
        db.execute("INSERT INTO inscripciones (id_est, id_mat, id_lab) VALUES (?, 1, 1)", (cur.lastrowid,))
        db.commit()
        return redirect('/')

    # MOSTRAR: Unimos las tablas para ver la lista
    query = ''' SELECT i.id, e.nombre as est, m.nombre as mat, p.nombre as prof 
                FROM inscripciones i 
                JOIN estudiantes e ON i.id_est = e.id 
                JOIN materias m ON i.id_mat = m.id 
                JOIN profesores p ON m.id_prof = p.id '''
    datos = db.execute(query).fetchall()
    db.close()
    return render_template('index.html', lista=datos)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db = conectar()
    db.execute("DELETE FROM inscripciones WHERE id = ?", (id,))
    db.commit()
    db.close()
    return redirect('/')

if __name__ == '__main__':
    crear_tablas()
    app.run(host='0.0.0.0', port=5000, debug=True)