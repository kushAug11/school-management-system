from flask import flash, session
from app import mysql

def validate_login(email, password):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM staff_details WHERE email = %s AND password = %s', (email, password))
    account = cursor.fetchone()
    cursor.close()
    if account:
        session['loggedin'] = True
        session['user_name'] = account['name'] 
        session['user_email'] = account['email']
        return True
    return False

def get_nursery_sections():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT nursery_section FROM plant_inventory")
    data = cursor.fetchall()
    cursor.close()
    return [item['nursery_section'] for item in data]

def get_inventory(section_name):
    cursor = mysql.connection.cursor()
    if section_name and section_name.strip() != "" and section_name.lower() != "none":
        cursor.execute("SELECT * FROM plant_inventory WHERE nursery_section = %s AND stock_count > 0", (section_name,))
    else:
        cursor.execute("SELECT * FROM plant_inventory WHERE stock_count > 0")
    data = cursor.fetchall()
    cursor.close()
    return data

def process_purchase(email, plant_name, quantity, selected_section):
    if not plant_name or not quantity:
        flash("Details missing.")
        return False
        
    qty = int(quantity)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM plant_inventory WHERE plant_name = %s", (plant_name,))
    item = cursor.fetchone()

    if not item:
        flash("Plant not found")
        return False

    if item['nursery_section'] != selected_section:
        flash(f"Item is in {item['nursery_section']}, not {selected_section}.")
        return False

    if item['stock_count'] < qty:
        flash(f"Only {item['stock_count']} items remaining.")
        return False

    total = item['price'] * qty
    new_stock = item['stock_count'] - qty

    cursor.execute("INSERT INTO order_records (email, plant_id, quantity, total_cost) VALUES (%s, %s, %s, %s)",
                   (email, item['plant_id'], qty, total))
    cursor.execute("UPDATE plant_inventory SET stock_count = %s WHERE plant_id = %s", (new_stock, item['plant_id']))
    mysql.connection.commit()
    cursor.close()
    flash(f"Order Success! Total: Rs.{total}")
    return True

def get_history(email):
    cursor = mysql.connection.cursor()
    query = """
        SELECT o.order_id, p.plant_name, p.nursery_section, o.quantity, o.total_cost 
        FROM order_records o
        JOIN plant_inventory p ON o.plant_id = p.plant_id
        WHERE o.email = %s ORDER BY o.order_id DESC
    """
    cursor.execute(query, [email])
    data = cursor.fetchall()
    cursor.close()
    return data