from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.text import MIMEText
import os

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='.')
app.secret_key = 'supersecretkey'


DATABASE = 'users.db'

# ---------- Database Handling ----------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            adress TEXT,
            email TEXT UNIQUE,
            password TEXT
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            status TEXT
        );
        CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        item TEXT
        );

        CREATE TABLE IF NOT EXISTS courier (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
        );

        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item TEXT
        );
        """)
        db.commit()

# ---------- Routes ----------

@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html', username=session.get('username'))

@app.route('/about.html')
def about():
    return render_template('about.html', username=session.get('username'))

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    return render_template("contact.html", username=session.get("username"))


@app.route('/login.html', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        # Check users table
        user = db.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['email'] = user['email']
            session['role'] = 'user'
            return redirect(url_for('home'))

        courier = db.execute("SELECT * FROM courier WHERE name = ?", (username,)).fetchone()
        if courier and check_password_hash(courier['password'], password):
            session['user_id'] = courier['id']
            session['username'] = courier['name']
            session['email'] = courier['email']
            session['role'] = 'courier'
            return redirect(url_for('courier_home'))

        error = "Incorrect credentials"

    return render_template("login.html", error=error, username=session.get("username"))

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        adress = request.form['adress']

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name, email, adress, password) VALUES (?, ?, ?, ?)",
                (name, email, adress, hashed_password)
            )
            db.commit()
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['email'] = user['email']
            session['role'] = 'user'
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            error = "Email already registered"
    return render_template('register.html', error=error, username=session.get('username'))


@app.route('/menu.html')
def menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', username=session.get('username'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = request.form['item']
    db = get_db()
    db.execute("INSERT INTO cart (user_id, item) VALUES (?, ?)", (session['user_id'], item))
    db.commit()
    return redirect(url_for('menu'))

@app.route('/cart.html')
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    items = db.execute("SELECT * FROM cart WHERE user_id = ?", (session['user_id'],)).fetchall()
    image_map = {
    "Crispy Chicken": "image1.jpeg",
    "Spicy Wings": "image2.jpeg",
    "Chicken Sandwich": "image3.jpeg"
}
    return render_template('cart.html', items=items, username=session.get('username'), image_map=image_map)


@app.route('/buy', methods=['POST'])
def buy():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()

    # Create new order
    db.execute("INSERT INTO orders (user_id, status) VALUES (?, ?)", (session['user_id'], 'pending'))
    order_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Get all cart items
    items = db.execute("SELECT item FROM cart WHERE user_id = ?", (session['user_id'],)).fetchall()

    # Insert into order_items
    for item in items:
        db.execute("INSERT INTO order_items (order_id, item) VALUES (?, ?)", (order_id, item['item']))

    # Clear cart
    db.execute("DELETE FROM cart WHERE user_id = ?", (session['user_id'],))
    db.commit()

    return redirect(url_for('view_cart'))

@app.route('/orders.html')
def user_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    orders = db.execute("""
        SELECT o.id AS order_id, o.status, u.adress AS address
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.user_id = ?
    """, (session['user_id'],)).fetchall()

    return render_template('orders.html', orders=orders, username=session.get("username"))

@app.route('/courier_home.html')
def courier_home():
    if session.get('role') != 'courier':
        return redirect(url_for('login'))

    db = get_db()
    orders = db.execute("""
        SELECT o.id, u.name, u.adress
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.status = 'approved'
    """).fetchall()

    return render_template('courier_home.html', orders=orders, username=session.get("username"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin.html')
def admin():
    if session.get('username') != 'admin':
        return redirect(url_for('login'))

    db = get_db()

    # Get all orders
    orders = db.execute("""
        SELECT o.id AS order_id, u.name AS username, u.adress AS address, o.status
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.status = 'pending'
    """).fetchall()

    # Fetch items for each order
    order_data = []
    for order in orders:
        items = db.execute("SELECT item FROM order_items WHERE order_id = ?", (order['order_id'],)).fetchall()
        item_list = [item['item'] for item in items]
        order_data.append({
            'id': order['order_id'],
            'username': order['username'],
            'address': order['address'],
            'status': order['status'],
            'items': item_list
        })

    return render_template('admin.html', orders=order_data, username=session.get("username"))

@app.route('/deliver/<int:order_id>')
def deliver(order_id):
    if session.get('role') != 'courier':
        return redirect(url_for('login'))
    db = get_db()
    db.execute("UPDATE orders SET status = 'delivered' WHERE id = ?", (order_id,))
    db.commit()
    return redirect(url_for('courier_home'))

@app.route('/admin/approve/<int:order_id>')
def approve_order(order_id):
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    db.execute("UPDATE orders SET status = 'approved' WHERE id = ?", (order_id,))
    db.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:order_id>')
def delete_order(order_id):
    if session.get('username') != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
    db.commit()
    return redirect(url_for('admin'))

# ---------- Initialize ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
