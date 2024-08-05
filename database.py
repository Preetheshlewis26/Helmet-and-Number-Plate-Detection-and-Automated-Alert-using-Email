db_config = {
    'user': 'root',
    'password': 'pjl126',
    'host': 'localhost',
    'database': 'vehicle_db'
}

def get_email(vehicle_number):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT email FROM vehicle_owners_list WHERE vehicle_number = %s"
        cursor.execute(query, (vehicle_number,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0]
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Ensure the database and tables are created
def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles_with_helmet (
        id INT AUTO_INCREMENT PRIMARY KEY,
        vehicle_number VARCHAR(20)
        )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles_without_helmet (
        id INT AUTO_INCREMENT PRIMARY KEY,
        vehicle_number VARCHAR(20)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_owners_list (
        id INT AUTO_INCREMENT PRIMARY KEY,
        vehicle_number VARCHAR(20) NOT NULL UNIQUE,
        owner_name VARCHAR(100),
        email VARCHAR(30),
        phone_number VARCHAR(10)
        )
        ''')
    conn.commit()
    cursor.close()
    conn.close()

import mysql.connector

# Function to insert a vehicle with a helmet
def insert_with_helmet(vehicle_number):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO vehicles_with_helmet (vehicle_number) VALUES (%s)"
        cursor.execute(query, (vehicle_number,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to insert a vehicle without a helmet
def insert_without_helmet(vehicle_number):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO vehicles_without_helmet (vehicle_number) VALUES (%s)"
        cursor.execute(query, (vehicle_number,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
