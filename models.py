from flask_mysqldb import MySQL
from flask import current_app as app

mysql = MySQL()

def get_user_by_email(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user

def register_user(name, email, password):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    mysql.connection.commit()
    cursor.close()

def get_recommended_courses(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.description FROM courses c
        JOIN user_courses uc ON c.id = uc.course_id
        WHERE uc.user_id = %s
    """, (user_id,))
    courses = cursor.fetchall()
    cursor.close()
    return courses
