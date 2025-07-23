import pymysql
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# ✅ Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "shreya_janu_28",
    "database": "course_recommendation",
    "cursorclass": pymysql.cursors.DictCursor
}

# ✅ Function to Connect to Database
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# ✅ Function to Recommend Courses
def recommend_courses(user_id):
    try:
        # Load trained model
        model = load_model("models/course_recommendation_model.h5")
        print("✅ Model Loaded Successfully")

        # Get the list of all course IDs from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT course_id FROM enrollments")
        courses = cursor.fetchall()
        conn.close()

        course_ids = np.array([row['course_id'] for row in courses], dtype=np.int32)
        print("📌 Courses in Database:", course_ids)

        if len(course_ids) == 0:
            return "No recommendations available at the moment."

        # ✅ Prepare input data for prediction
        user_input = np.full_like(course_ids, user_id, dtype=np.int32)
        course_input = course_ids

        print("📌 User Input Shape:", user_input.shape)
        print("📌 Course IDs Shape:", course_ids.shape)

        # ✅ Fix shape issue by reshaping input
        X_test = np.column_stack((user_input, course_input)).astype(np.float32)
        print("📌 X_test Shape (Before Prediction):", X_test.shape)

        # ✅ Ensure valid indices for embedding layers
        input_dim = model.input_shape[1]
        X_test = np.clip(X_test, 0, input_dim - 1)

        # ✅ Predict course recommendations
        predictions = model.predict(X_test).flatten()
        print("📌 Predictions:", predictions)

        # ✅ Get top recommended courses
        recommended_indices = np.argsort(predictions)[::-1]  # Sort in descending order
        top_recommended_courses = course_ids[recommended_indices][:5]  # Get top 5 recommendations

        print("✅ Final Recommended Courses:", top_recommended_courses)
        return top_recommended_courses.tolist()  # Convert NumPy array to Python list

    except Exception as e:
        print("❌ Error:", str(e))
        return f"An error occurred: {str(e)}"

