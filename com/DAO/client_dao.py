from base import mysql
from com.VO import ClientVO
import bcrypt

class ClientDAO:
    def create(self, client):
        cursor = mysql.connection.cursor()
        hashed_password = bcrypt.hashpw(client.password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO client(Username, Password, Email, Mobile_no) VALUES(%s,%s,%s,%s)",
                      (client.username, hashed_password, client.email, client.mobile_no))
        mysql.connection.commit()
        cursor.close()

    def get_by_email(self, email):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM client WHERE Email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return ClientVO(id=user[0], username=user[1], password=user[2], 
                          email=user[3], mobile_no=user[4], city=user[5])
        return None

    def get_by_id(self, user_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM client WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return ClientVO(id=user[0], username=user[1], password=user[2], 
                          email=user[3], mobile_no=user[4], city=user[5])
        return None

    def get_all(self):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM client")
        users = cursor.fetchall()
        cursor.close()
        return [ClientVO(id=user[0], username=user[1], password=user[2], 
                        email=user[3], mobile_no=user[4], city=user[5]) for user in users]
    
    def get_count(self):
        """Get the total number of clients"""
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM client")
        count = cursor.fetchone()[0]
        cursor.close()
        return count 