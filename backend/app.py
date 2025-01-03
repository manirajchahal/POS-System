from flask import Flask, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('../database/pos_system.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        items TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        special_instructions TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# Menu Endpoints
@app.route('/menu', methods=['GET'])
def get_menu():
    conn = sqlite3.connect('../database/pos_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()
    conn.close()
    return {"menu": menu}, 200

@app.route('/menu', methods=['POST'])
def add_menu_item():
    data = request.get_json()
    name = data['name']
    price = data['price']

    conn = sqlite3.connect('../database/pos_system.db')
    cursor = conn.cursor()

    # Check for duplicate menu items
    cursor.execute("SELECT 1 FROM menu WHERE name = ?", (name,))
    if cursor.fetchone():
        conn.close()
        return {"error": "Menu item already exists."}, 400

    cursor.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

    return {"message": "Menu item added successfully!"}, 201

@app.route('/menu/<int:menu_id>', methods=['DELETE'])
def delete_menu_item(menu_id):
    conn = sqlite3.connect('../database/pos_system.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE id = ?", (menu_id,))
    conn.commit()
    conn.close()

    return {"message": "Menu item deleted successfully!"}, 200

# Order Endpoints
@app.route('/orders', methods=['GET'])
def get_orders():
    status = request.args.get('status')  # Retrieve the status filter
    start_date = request.args.get('start')  # Retrieve the start timestamp filter
    end_date = request.args.get('end')  # Retrieve the end timestamp filter

    conn = sqlite3.connect('../database/pos_system.db')
    cursor = conn.cursor()

    # Base query
    query = "SELECT * FROM orders WHERE 1=1"
    params = []

    # Add status filter if provided
    if status:
        query += " AND status = ?"
        params.append(status)

    # Add timestamp range filter if provided
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)

    cursor.execute(query, params)
    orders = cursor.fetchall()
    conn.close()

    return {"orders": orders}, 200

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    items = data['items']
    special_instructions = data.get('special_instructions', '')

    conn = sqlite3.connect('../database/pos_system.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (items, special_instructions) VALUES (?, ?)",
        (items, special_instructions),
    )
    conn.commit()
    conn.close()

    return {"message": "Order added successfully!"}, 201

@app.route('/orders/<int:order_id>', methods=['PATCH'])
def update_order_status(order_id):
    data = request.get_json()
    status = data['status']

    conn = sqlite3.connect('../database/pos_system.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

    return {"message": "Order status updated successfully!"}, 200

if __name__ == '__main__':
    app.run(debug=True)
