from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# PostgreSQL Connection
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "2102"

def get_db_connection():
    return psycopg2.connect(
        host = DB_HOST,
        database = DB_NAME,
        user =DB_USER,
        password =DB_PASSWORD
    )
# CREATE TODO_TABLE
def create_todo_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute(""" CREATE TABLE IF NOT EXISTS todo_table (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
    connection.commit() 
    cur.close()
    connection.close()

create_todo_table()

# CREATE TASK

@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.json['title']
    description = request.json['description']
    status = request.json['status']
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        INSERT INTO todo_table(title, description, status) VALUES (%s,%s,%s)
    """, (title, description, status))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message": "Task added successfully"}), 201

# VIEW ALL TASKS

@app.route('/view_tasks', methods=['GET'])
def view_tasks():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        SELECT * FROM todo_table
    """)
    data = cur.fetchall()
    task_list = []
    for task in data:
        task_list.append({
            "id": task[0],
            "title": task[1],
            "status": task[3],
            "created_at": str(task[4])
        })
    cur.close()
    connection.close()
    return jsonify(task_list), 200

# UPDATE TASK

@app.route('/update_task/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    title = data['title']
    status = data['status']
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        UPDATE todo_table
        SET title=%s,
            status=%s
        WHERE id=%s
    """, (title, status, id))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message": "Task updated successfully"}), 200
# DELETE TASK

@app.route('/delete_task/<int:id>', methods=['DELETE'])
def delete_task(id):
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""DELETE FROM todo_table WHERE id=%s
    """, (id,))
    connection.commit()
    if cur.rowcount == 0:
        cur.close()
        connection.close()
        return jsonify({"message": "Task not found"}), 404
    cur.close()
    connection.close()
    return jsonify({"message": "Task deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)