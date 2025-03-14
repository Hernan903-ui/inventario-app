from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config["TEMPLATES_AUTO_RELOAD"] = True
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Configuración de MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

# =============================================
# RUTAS PRINCIPALES
# =============================================

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['nombre'] = account[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        negocio = request.form['negocio']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, correo, negocio, password)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nombre, apellido, correo, negocio, password))
        mysql.connection.commit()
        flash('Registro exitoso! Por favor inicia sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# =============================================
# GESTIÓN DE INVENTARIO
# =============================================

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT id, producto, cantidad, cantidad_minima, fecha_actualizacion
        FROM inventario 
        WHERE user_id = %s
        ORDER BY fecha_actualizacion DESC
    ''', (session['id'],))
    inventario = cursor.fetchall()
    
    alertas = [item for item in inventario if item[2] < item[3]]
    
    return render_template('dashboard.html', 
                         inventario=inventario, 
                         alertas=alertas, 
                         nombre=session['nombre'])

@app.route('/agregar-producto', methods=['GET', 'POST'])
def agregar_producto():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        producto = request.form['producto']
        cantidad = int(request.form['cantidad'])
        minima = int(request.form['minima'])
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO inventario (user_id, producto, cantidad, cantidad_minima)
            VALUES (%s, %s, %s, %s)
        ''', (session['id'], producto, cantidad, minima))
        mysql.connection.commit()
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('agregar_producto.html')

@app.route('/editar-producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    
    if request.method == 'POST':
        producto = request.form['producto']
        cantidad = int(request.form['cantidad'])
        minima = int(request.form['minima'])
        
        cursor.execute('''
            UPDATE inventario 
            SET producto = %s, cantidad = %s, cantidad_minima = %s 
            WHERE id = %s AND user_id = %s
        ''', (producto, cantidad, minima, id, session['id']))
        mysql.connection.commit()
        flash('Producto actualizado', 'success')
        return redirect(url_for('dashboard'))
    
    cursor.execute('SELECT * FROM inventario WHERE id = %s AND user_id = %s', (id, session['id']))
    producto = cursor.fetchone()
    return render_template('editar_producto.html', producto=producto)

@app.route('/eliminar-producto/<int:id>')
def eliminar_producto(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM inventario WHERE id = %s AND user_id = %s', (id, session['id']))
    mysql.connection.commit()
    flash('Producto eliminado', 'warning')
    return redirect(url_for('dashboard'))

# =============================================
# EJECUCIÓN DE LA APLICACIÓN
# =============================================

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False  # Necesario para evitar errores en Windows
    )