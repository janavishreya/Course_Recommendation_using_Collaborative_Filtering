from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from models.collaborative_filtering import recommend_courses
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Connection
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()  # This returns a dictionary because of DictCursor
        conn.close()

        if user:
            session['user_id'] = user['id']  # Access the user ID using the column name
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password"  # Handle login failure

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

# Course Enrollment (List Courses & Enroll)
@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        user_id = session['user_id']

        # Ensure course_id is not empty and is an integer
        if not course_id or not user_id:
            flash("Invalid Data: Course ID or User ID missing", "danger")
            return redirect(url_for('dashboard'))
        
        try:
            course_id = int(course_id)  # Convert course_id to integer

            # Check if user is already enrolled
            cursor.execute("SELECT * FROM enrollments WHERE user_id=%s AND course_id=%s", (user_id, course_id))
            existing_enrollment = cursor.fetchone()

            if not existing_enrollment:
                cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (%s, %s)", (user_id, course_id))
                conn.commit()
                flash("You have successfully enrolled in the course!", "success")
            else:
                flash("You are already enrolled in this course.", "warning")

        except ValueError:
            flash("Invalid Data: Course ID must be an integer", "danger")

        conn.close()
        return redirect(url_for('dashboard'))

    # Fetch available courses
    cursor.execute("SELECT id, name FROM courses")
    courses = cursor.fetchall()
    

    print("Courses from DB:", courses)
    conn.close()
    return render_template('enroll.html', courses=courses)


# Course Enrollment (Direct Enrollment via Course ID)
@app.route('/enroll/<int:course_id>', methods=['GET', 'POST'])
def enroll_course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        user_id = session['user_id']
        
        # Check if user is already enrolled
        cursor.execute("SELECT * FROM enrollments WHERE user_id=%s AND course_id=%s", (user_id, course_id))
        existing_enrollment = cursor.fetchone()

        if not existing_enrollment:
            cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (%s, %s)", (user_id, course_id))
            conn.commit()
            flash("You have successfully enrolled in the course!", "success")
        else:
            flash("You are already enrolled in this course.", "warning")

        conn.close()
        return redirect(url_for('dashboard'))

    # Fetch course details
    cursor.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
    course = cursor.fetchone()
    conn.close()

    return render_template('enroll.html', course=course)

# Course Recommendations
@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    recommended_courses = recommend_courses(user_id)
    print("Courses being sent to frontend:", recommended_courses)

    return render_template('recommendations.html', recommendations=recommended_courses)

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
