from base import mysql
import bcrypt

def fix_admin():
    try:
        # Connect to the database
        connection = mysql.connection
        cursor = connection.cursor()
        
        # Check current admin records
        cursor.execute("SELECT * FROM Admin")
        admins = cursor.fetchall()
        print(f"Found {len(admins)} admin records")
        
        for admin in admins:
            print(f"Record: {admin}")
        
        # Delete all existing admin records
        cursor.execute("DELETE FROM Admin")
        connection.commit()
        print("Deleted all existing admin records")
        
        # Create admin with proper credentials
        email = "prajapatijaydip591@gmail.com"
        name = "Jaydip Prajapati"
        password = "JAydip.m.p@2204"
        
        # Generate proper bcrypt hash
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')
        
        # Insert admin with proper hashed password
        cursor.execute("INSERT INTO Admin(Name, Email, Password) VALUES(%s, %s, %s)", 
                       (name, email, hashed_str))
        connection.commit()
        admin_id = cursor.lastrowid
        print(f"Created admin with ID: {admin_id}, Name: {name}, Email: {email}")
        
        # Also create a test admin
        test_email = "admin@test.com"
        test_name = "Test Admin"
        test_password = "admin123"
        test_hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        test_hashed_str = test_hashed.decode('utf-8')
        
        cursor.execute("INSERT INTO Admin(Name, Email, Password) VALUES(%s, %s, %s)", 
                       (test_name, test_email, test_hashed_str))
        connection.commit()
        test_id = cursor.lastrowid
        print(f"Created test admin with ID: {test_id}, Name: {test_name}, Email: {test_email}")
        
        # Verify the admins were created correctly
        cursor.execute("SELECT * FROM Admin")
        new_admins = cursor.fetchall()
        print(f"New admin records: {len(new_admins)}")
        
        for admin in new_admins:
            print(f"Record: {admin}")
        
        cursor.close()
        print("Admin credentials fixed successfully!")
        print("You can now log in with either:")
        print(f"1. Email: {email}, Password: {password}")
        print(f"2. Email: {test_email}, Password: {test_password}")
        
        return True
    except Exception as e:
        print(f"Error fixing admin credentials: {str(e)}")
        return False

if __name__ == "__main__":
    # This will run when the script is executed directly
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
    
    # Create application context
    with app.app_context():
        fix_admin() 