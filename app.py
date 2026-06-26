from flask import Flask, request, jsonify
import psycopg2
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "2102"


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def create_users_table():
    connection = get_db_connection()
    cur = connection.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_table(
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone_number VARCHAR(15) NOT NULL,
            college VARCHAR(100) NOT NULL
        );
    """)
    connection.commit()
    cur.close()
    connection.close()
    
create_users_table()
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    phone_number = data.get("phone_number")
    college = data.get("college")

    if not username or not email or not password or not phone_number or not college:
        return jsonify({"error": "All fields are required"}), 400
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        SELECT * FROM users_table
        WHERE username=%s OR email=%s
    """, (username, email))
    existing_user = cur.fetchone()
    if existing_user:
        cur.close()
        connection.close()
        return jsonify({
            "error": "Username or Email already exists"
        }), 400
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cur.execute("""
        INSERT INTO users_table
        (username, email, password, phone_number, college)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        username,
        email,
        hashed_password,
        phone_number,
        college
    ))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({
        "message": "User Registered Successfully"
    }), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not username or not email or not password:
        return jsonify({
            "error": "All fields are required"
        }), 400
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        SELECT user_id, username, email, password
        FROM users_table
        WHERE username=%s AND email=%s
    """, (username, email))
    user = cur.fetchone()
    cur.close()
    connection.close()
    if not user:
        return jsonify({
            "error": "Username and Email do not match"
        }), 401
    user_id, username, email, hashed_password = user
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({
            "error": "Invalid Password"
        }), 401
        return jsonify({
        "message": "Login Successful",
        "user": {
            "user_id": user_id,
            "username": username,
            "email": email
        }
    }), 200

if __name__ == "__main__":
    app.run(debug=True)