from flask import Flask
from base import mysql

app = Flask(__name__)
# Configure MySQL from your app's configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jaydip.m.p@2204'
app.config['MYSQL_DB'] = 'register'

# Initialize MySQL
mysql.init_app(app)

with app.app_context():
    try:
        # Connect to the database
        connection = mysql.connection
        cursor = connection.cursor()
        
        # Check table structure
        cursor.execute("DESCRIBE Admin")
        columns = cursor.fetchall()
        print("Admin table structure:")
        for column in columns:
            print(f"Column: {column[0]}, Type: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}, Extra: {column[5]}")
        
        # Check existing data
        cursor.execute("SELECT * FROM Admin")
        admins = cursor.fetchall()
        print(f"\nExisting admin records ({len(admins)}):")
        for admin in admins:
            print(f"Record: {admin}")
        
        cursor.close()
    except Exception as e:
        print(f"Error: {str(e)}") 