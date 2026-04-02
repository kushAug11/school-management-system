import os
import MySQLdb  # Used to create the database if it doesn't exist
from flask import Flask
from flask_mysqldb import MySQL
from config import Config

# Initialize the MySQL object
mysql = MySQL()

def load_sql_data():
    cursor = mysql.connection.cursor()
    sql_file = os.path.join(os.path.dirname(__file__), "table_scripts.sql")
    
    try:
        with open(sql_file, mode="r", encoding="utf-8") as f:
            content = f.read()
            commands = content.split(';')
            
            for command in commands:
                if command.strip():
                    cursor.execute(command)
                    
        mysql.connection.commit()
        print("GreenLeaf Database tables created/updated successfully.")
        
    except FileNotFoundError:
        print(f"Warning: Could not find {sql_file}. Please ensure the file exists.")
    except Exception as e:
        print(f"Error executing Nursery SQL scripts: {e}")
    finally:
        cursor.close()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    try:
        temp_conn = MySQLdb.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            passwd=app.config['MYSQL_PASSWORD']
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
        temp_conn.commit()
        temp_cursor.close()
        temp_conn.close()
    except Exception as e:
        print(f"Database creation check failed: {e}")
    mysql.init_app(app)
    with app.app_context():
        load_sql_data()
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app