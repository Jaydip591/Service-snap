from base import mysql
from com.VO import ServiceProviderVO
import bcrypt

class ServiceProviderDAO:
    def create(self, provider):
        cursor = mysql.connection.cursor()
        hashed_password = bcrypt.hashpw(provider.s_pass.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO service_provider(S_Name, S_Email, S_Pass, S_Skills, S_Mobile, S_City) VALUES(%s, %s, %s, %s, %s, %s)",
                      (provider.s_name, provider.s_email, hashed_password, provider.s_skills, provider.s_mobile, provider.s_city))
        mysql.connection.commit()
        cursor.close()

    def get_by_email(self, email):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM service_provider WHERE S_Email=%s", (email,))
        provider = cursor.fetchone()
        cursor.close()
        if provider:
            return ServiceProviderVO(s_id=provider[0], s_name=provider[1], s_email=provider[2],
                                   s_pass=provider[3], s_skills=provider[4], s_mobile=provider[5],
                                   s_city=provider[6])
        return None

    def get_by_id(self, provider_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM service_provider WHERE S_id=%s", (provider_id,))
        provider = cursor.fetchone()
        cursor.close()
        if provider:
            return ServiceProviderVO(s_id=provider[0], s_name=provider[1], s_email=provider[2],
                                   s_pass=provider[3], s_skills=provider[4], s_mobile=provider[5],
                                   s_city=provider[6])
        return None

    def get_all(self):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM service_provider")
        providers = cursor.fetchall()
        cursor.close()
        return [ServiceProviderVO(s_id=p[0], s_name=p[1], s_email=p[2],
                                s_pass=p[3], s_skills=p[4], s_mobile=p[5],
                                s_city=p[6]) for p in providers]

    def get_by_city(self, city):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM service_provider WHERE S_City=%s", (city,))
        providers = cursor.fetchall()
        cursor.close()
        return [ServiceProviderVO(s_id=p[0], s_name=p[1], s_email=p[2],
                                s_pass=p[3], s_skills=p[4], s_mobile=p[5],
                                s_city=p[6]) for p in providers]

    def get_count(self):
        """Get the total number of service providers"""
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM service_provider")
        count = cursor.fetchone()[0]
        cursor.close()
        return count 