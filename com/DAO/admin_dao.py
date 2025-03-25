from base import mysql
from com.VO import AdminVO
import bcrypt
import re

class AdminDAO:
    def create(self, admin):
        """Create a new admin user with hashed password."""
        cursor = mysql.connection.cursor()
        
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(admin.password.encode('utf-8'), bcrypt.gensalt())
        
        # Convert binary hash to string for storage
        hashed_password_str = hashed_password.decode('utf-8')
        
        cursor.execute("INSERT INTO Admin(Name, Email, Password) VALUES(%s, %s, %s)",
                      (admin.name, admin.email, hashed_password_str))
        mysql.connection.commit()
        
        # Get the ID of the inserted admin
        admin_id = cursor.lastrowid
        cursor.close()
        
        return admin_id
        
    def get_by_email(self, email):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Admin WHERE Email=%s", (email,))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            return AdminVO(id=admin[0], name=admin[1], email=admin[2], password=admin[3])
        return None

    def get_by_id(self, admin_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Admin WHERE ID=%s", (admin_id,))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            return AdminVO(id=admin[0], name=admin[1], email=admin[2], password=admin[3])
        return None
    
    def get_all(self):
        """Get all admin users."""
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Admin")
        admins_data = cursor.fetchall()
        cursor.close()
        
        # Convert to list of AdminVO objects
        admins = []
        for admin in admins_data:
            admins.append(AdminVO(id=admin[0], name=admin[1], email=admin[2], password=admin[3]))
        
        return admins
    
    def update(self, admin):
        """Update an admin's information (except password)."""
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE Admin SET Name=%s, Email=%s WHERE ID=%s",
                      (admin.name, admin.email, admin.id))
        mysql.connection.commit()
        cursor.close()
        
    def update_password(self, admin_id, new_password):
        """Update an admin's password."""
        cursor = mysql.connection.cursor()
        
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Convert binary hash to string for storage
        hashed_password_str = hashed_password.decode('utf-8')
        
        cursor.execute("UPDATE Admin SET Password=%s WHERE ID=%s",
                      (hashed_password_str, admin_id))
        mysql.connection.commit()
        cursor.close()
        
    def delete(self, admin_id):
        """Delete an admin user."""
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Admin WHERE ID=%s", (admin_id,))
        mysql.connection.commit()
        cursor.close()
        
    def verify_password(self, stored_password, input_password):
        """Safely verify password against stored hash"""
        try:
            # If stored password is a string, convert to bytes
            if isinstance(stored_password, str):
                # Check if it's a valid bcrypt hash
                if re.match(r'^\$2[aby]\$\d+\$.{53}$', stored_password):
                    stored_password = stored_password.encode('utf-8')
                else:
                    return False
                    
            return bcrypt.checkpw(input_password.encode('utf-8'), stored_password)
        except ValueError:
            # If there's any error, return False for safety
            return False 