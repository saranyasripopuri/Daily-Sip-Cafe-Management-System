from flask import Flask, render_template, request, jsonify
import sqlite3



app = Flask(__name__)

DATABASE = "database.db"
def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    # Enable foreign key support in SQLite
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

def create_tables():

    connection = get_db_connection()

    cursor = connection.cursor()


    # ======================================
    # ORDERS TABLE
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_type TEXT NOT NULL,

            table_number TEXT,

            token_number INTEGER,

            subtotal REAL NOT NULL,

            gst REAL NOT NULL,

            grand_total REAL NOT NULL,

            status TEXT NOT NULL DEFAULT 'Pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,

            item_name TEXT NOT NULL,

            price REAL NOT NULL,

            quantity INTEGER NOT NULL,

            subtotal REAL NOT NULL,

            FOREIGN KEY (order_id)
            REFERENCES orders (id)

        )
    """)


    # ======================================
    # PAYMENTS TABLE
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL UNIQUE,

            payment_method TEXT NOT NULL,

            amount REAL NOT NULL,

            payment_status TEXT NOT NULL DEFAULT 'Paid',

            paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (order_id)
            REFERENCES orders (id)

        )
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS menu_items (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    price REAL NOT NULL,

    available INTEGER DEFAULT 1

)
""")



    connection.commit()

    connection.close()


# ==========================================
# DASHBOARD PAGE
# ==========================================

@app.route("/")
def dashboard():

    return render_template("dashboard.html")


# ==========================================
# NEW ORDER PAGE
# ==========================================

@app.route("/order")
def order():

    return render_template("order.html")


# ==========================================
# KITCHEN PAGE
# ==========================================

@app.route("/kitchen")
def kitchen():

    return render_template("kitchen.html")


# ==========================================
# BILLING PAGE
# ==========================================

@app.route("/billing")
def billing():

    return render_template("billing.html")


# ==========================================
# SAVE NEW ORDER
# ==========================================

@app.route("/api/orders", methods=["POST"])
def save_order():

    data = request.get_json(silent=True)


    # CHECK REQUEST DATA

    if not data:

        return jsonify({

            "success": False,

            "message": "No order data received."

        }), 400


    # READ ORDER DATA

    order_type = data.get("order_type")

    table_number = data.get("table_number")

    token_number = data.get("token_number")

    subtotal = data.get("subtotal")

    gst = data.get("gst")

    grand_total = data.get("grand_total")

    items = data.get("items", [])


    # ======================================
    # VALIDATION
    # ======================================

    if order_type not in ["Dine In", "Take Away"]:

        return jsonify({

            "success": False,

            "message": "Invalid order type."

        }), 400


    if order_type == "Dine In" and not table_number:

        return jsonify({

            "success": False,

            "message": "Table number is required."

        }), 400


    if order_type == "Take Away" and token_number is None:

        return jsonify({

            "success": False,

            "message": "Token number is required."

        }), 400


    if not items:

        return jsonify({

            "success": False,

            "message": "Order must contain at least one item."

        }), 400


    connection = get_db_connection()

    cursor = connection.cursor()


    try:

        # ==================================
        # INSERT ORDER
        # ==================================

        cursor.execute("""
            INSERT INTO orders (

                order_type,

                table_number,

                token_number,

                subtotal,

                gst,

                grand_total,

                status

            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

        """, (

            order_type,

            table_number,

            token_number,

            subtotal,

            gst,

            grand_total,

            "Pending"

        ))


        order_id = cursor.lastrowid


        # ==================================
        # INSERT ORDER ITEMS
        # ==================================

        for item in items:

            item_name = item.get("name")

            price = item.get("price")

            quantity = item.get("quantity")


            if (

                not item_name

                or price is None

                or quantity is None

                or quantity <= 0

            ):

                raise ValueError(

                    "Invalid order item data."

                )


            item_subtotal = price * quantity


            cursor.execute("""
                INSERT INTO order_items (

                    order_id,

                    item_name,

                    price,

                    quantity,

                    subtotal

                )

                VALUES (?, ?, ?, ?, ?)

            """, (

                order_id,

                item_name,

                price,

                quantity,

                item_subtotal

            ))


        connection.commit()


        return jsonify({

            "success": True,

            "message": "Order saved successfully.",

            "order_id": order_id

        })


    except Exception as error:

        connection.rollback()


        return jsonify({

            "success": False,

            "message": str(error)

        }), 500


    finally:

        connection.close()


# ==========================================
# GET KITCHEN ORDERS
# ==========================================

@app.route("/api/kitchen/orders", methods=["GET"])
def get_kitchen_orders():

    connection = get_db_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *

        FROM orders

        WHERE status IN ('Pending', 'Preparing')

        ORDER BY id ASC
    """)


    orders = cursor.fetchall()

    kitchen_orders = []


    for order in orders:


        cursor.execute("""
            SELECT *

            FROM order_items

            WHERE order_id = ?

            ORDER BY id ASC
        """, (

            order["id"],

        ))


        items = cursor.fetchall()


        order_data = {

            "id":
                order["id"],

            "order_type":
                order["order_type"],

            "table_number":
                order["table_number"],

            "token_number":
                order["token_number"],

            "grand_total":
                order["grand_total"],

            "status":
                order["status"],

            "created_at":
                order["created_at"],

            "items": []

        }


        for item in items:

            order_data["items"].append({

                "name":
                    item["item_name"],

                "quantity":
                    item["quantity"]

            })


        kitchen_orders.append(order_data)


    connection.close()


    return jsonify(kitchen_orders)


# ==========================================
# UPDATE ORDER STATUS
# ==========================================

@app.route(
    "/api/orders/<int:order_id>/status",
    methods=["PUT"]
)
def update_order_status(order_id):


    data = request.get_json(silent=True)


    if not data:

        return jsonify({

            "success": False,

            "message": "No status received."

        }), 400


    new_status = data.get("status")


    allowed_statuses = [

        "Pending",

        "Preparing",

        "Ready"

    ]


    if new_status not in allowed_statuses:

        return jsonify({

            "success": False,

            "message": "Invalid order status."

        }), 400


    connection = get_db_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT status

        FROM orders

        WHERE id = ?
    """, (

        order_id,

    ))


    existing_order = cursor.fetchone()


    if existing_order is None:

        connection.close()


        return jsonify({

            "success": False,

            "message": "Order not found."

        }), 404


    current_status = existing_order["status"]


    # VALID STATUS TRANSITIONS

    valid_transitions = {

        "Pending": "Preparing",

        "Preparing": "Ready"

    }


    if (

        current_status not in valid_transitions

        or valid_transitions[current_status] != new_status

    ):

        connection.close()


        return jsonify({

            "success": False,

            "message":

                "Invalid status transition."

        }), 400


    cursor.execute("""
        UPDATE orders

        SET status = ?

        WHERE id = ?
    """, (

        new_status,

        order_id

    ))


    connection.commit()

    connection.close()


    return jsonify({

        "success": True,

        "message": "Order status updated."

    })


# ==========================================
# GET READY ORDERS FOR BILLING
# ==========================================

@app.route("/api/billing/orders", methods=["GET"])
def get_billing_orders():


    connection = get_db_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *

        FROM orders

        WHERE status = 'Ready'

        ORDER BY id ASC
    """)


    orders = cursor.fetchall()

    billing_orders = []


    for order in orders:


        cursor.execute("""
            SELECT *

            FROM order_items

            WHERE order_id = ?

            ORDER BY id ASC
        """, (

            order["id"],

        ))


        items = cursor.fetchall()


        order_data = {

            "id":
                order["id"],

            "order_type":
                order["order_type"],

            "table_number":
                order["table_number"],

            "token_number":
                order["token_number"],

            "subtotal":
                order["subtotal"],

            "gst":
                order["gst"],

            "grand_total":
                order["grand_total"],

            "created_at":
                order["created_at"],

            "items": []

        }


        for item in items:

            order_data["items"].append({

                "name":
                    item["item_name"],

                "price":
                    item["price"],

                "quantity":
                    item["quantity"],

                "subtotal":
                    item["subtotal"]

            })


        billing_orders.append(order_data)


    connection.close()


    return jsonify(billing_orders)


# ==========================================
# COMPLETE PAYMENT
# ==========================================

@app.route(
    "/api/orders/<int:order_id>/payment",
    methods=["POST"]
)
def complete_payment(order_id):


    data = request.get_json(silent=True)


    if not data:

        return jsonify({

            "success": False,

            "message":
                "No payment data received."

        }), 400


    payment_method =data.get("payment_method")


    allowed_payment_methods = [

        "Cash",

        "UPI",

        "Card"

    ]


    if payment_method not in allowed_payment_methods:

        return jsonify({

            "success": False,

            "message":
                "Invalid payment method."

        }), 400


    connection = get_db_connection()

    cursor = connection.cursor()


    try:


        # ==================================
        # GET ORDER
        # ==================================

        cursor.execute("""
            SELECT *

            FROM orders

            WHERE id = ?
        """, (

            order_id,

        ))


        order = cursor.fetchone()


        if order is None:

            return jsonify({

                "success": False,

                "message": "Order not found."

            }), 404


        if order["status"] != "Ready":

            return jsonify({

                "success": False,

                "message":

                    "Only Ready orders can be paid."

            }), 400


        # ==================================
        # SAVE PAYMENT
        # ==================================

        cursor.execute("""
            INSERT INTO payments (

                order_id,

                payment_method,

                amount,

                payment_status

            )

            VALUES (?, ?, ?, ?)

        """, (

            order_id,

            payment_method,

            order["grand_total"],

            "Paid"

        ))


        # ==================================
        # UPDATE ORDER TO PAID
        # ==================================

        cursor.execute("""
            UPDATE orders

            SET status = 'Paid'

            WHERE id = ?
        """, (

            order_id,

        ))


        connection.commit()


        return jsonify({

            "success": True,

            "message":
                "Payment completed successfully.",

            "order_id":
                order_id

        })


    except sqlite3.IntegrityError:

        connection.rollback()


        return jsonify({

            "success": False,

            "message":
                "This order has already been paid."

        }), 400


    except Exception as error:

        connection.rollback()


        return jsonify({

            "success": False,

            "message": str(error)

        }), 500


    finally:

        connection.close()


# ==========================================
# START APPLICATION
# ==========================================
# ==========================================
# REPORTS API
# ==========================================

@app.route("/api/reports", methods=["GET"])
def get_reports():

    connection = get_db_connection()
    cursor = connection.cursor()

    # Total Orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    # Pending Orders
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'")
    pending = cursor.fetchone()[0]

    # Preparing Orders
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Preparing'")
    preparing = cursor.fetchone()[0]

    # Ready Orders
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Ready'")
    ready = cursor.fetchone()[0]

    # Paid Orders
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Paid'")
    paid = cursor.fetchone()[0]

    # Revenue
    cursor.execute("""
        SELECT IFNULL(SUM(grand_total),0)
        FROM orders
        WHERE status='Paid'
    """)
    revenue = cursor.fetchone()[0]

    # GST
    cursor.execute("""
        SELECT IFNULL(SUM(gst),0)
        FROM orders
        WHERE status='Paid'
    """)
    gst = cursor.fetchone()[0]

    # Recent Orders
    cursor.execute("""
        SELECT id,
               order_type,
               grand_total,
               status,
               created_at
        FROM orders
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()

    recent_orders = []

    for row in rows:

        recent_orders.append({

            "id": row["id"],
            "order_type": row["order_type"],
            "grand_total": row["grand_total"],
            "status": row["status"],
            "created_at": row["created_at"]

        })

    connection.close()

    return jsonify({

        "total_orders": total_orders,
        "pending": pending,
        "preparing": preparing,
        "ready": ready,
        "paid": paid,
        "revenue": revenue,
        "gst": gst,
        "recent_orders": recent_orders

    })

@app.route("/reports")
def reports():
    return render_template("reports.html")
@app.route("/menu")
def menu():
    return render_template("menu.html")
# ==========================================
# GET MENU ITEMS
# ==========================================

@app.route("/api/menu", methods=["GET"])
def get_menu():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM menu_items
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    menu_items = []

    for row in rows:

        menu_items.append({
            "id": row["id"],
            "name": row["name"],
            "price": row["price"],
            "available": row["available"]
        })

    return jsonify(menu_items)
# ==========================================
# ADD MENU ITEM
# ==========================================

@app.route("/api/menu", methods=["POST"])
def add_menu_item():

    data = request.get_json()

    name = data.get("name")
    price = data.get("price")

    if not name or price is None:

        return jsonify({
            "message": "Name and price are required."
        }), 400


    connection = get_db_connection()
    cursor = connection.cursor()


    cursor.execute("""

        INSERT INTO menu_items
        (name, price, available)

        VALUES (?, ?, ?)

    """, (

        name,
        price,
        1

    ))


    connection.commit()

    connection.close()


    return jsonify({

        "message": "Menu item added successfully."

    }), 201
# ==========================================
# DELETE MENU ITEM
# ==========================================

@app.route("/api/menu/<int:item_id>", methods=["DELETE"])
def delete_menu_item(item_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM menu_items WHERE id = ?",
        (item_id,)
    )

    connection.commit()

    connection.close()

    return jsonify({
        "message": "Menu item deleted successfully."
    })

if __name__ == "__main__":
    create_tables()
    app.run(debug=True, use_reloader=False)