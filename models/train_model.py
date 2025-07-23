import pymysql
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Flatten

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "shreya_janu_28",
    "database": "course_recommendation",
    "cursorclass": pymysql.cursors.DictCursor  # ✅ Ensures dictionary results
}



# Database Connection
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Load Data from Database
def load_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user-course interactions
    cursor.execute("SELECT user_id, course_id FROM enrollments")
    data = cursor.fetchall()
    conn.close()

    user_ids = np.array([row['user_id'] for row in data])
    course_ids = np.array([row['course_id'] for row in data])

    return user_ids, course_ids

# Build the Model
def build_model(num_users, num_courses, embedding_dim=16):
    model = Sequential([
        Embedding(input_dim=num_users, output_dim=embedding_dim, input_length=1),
        Flatten(),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')  # Predict user preference for a course
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Train the Model
def train_model():
    user_ids, course_ids = load_data()
    
    num_users = max(user_ids) + 1
    num_courses = max(course_ids) + 1

    model = build_model(num_users, num_courses)
    
    # Convert inputs to numpy arrays
    X = np.column_stack((user_ids, course_ids))
    y = np.ones(len(X))  # Assuming enrolled courses are positive samples
    
    model.fit(X, y, epochs=5, batch_size=32)

    # Save Model
    model.save("models/course_recommendation_model.h5")

if __name__ == "__main__":
    train_model()
