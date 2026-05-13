# app.py
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tbl_user(user_name, user_email) VALUES (%s, %s)", (data['name'], data['email']))
    mysql.connection.commit()
    return jsonify({"message": "User added successfully!"}), 201

@app.route('/')
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/users', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_user")
    rows = cur.fetchall()
    return jsonify(rows)

@app.route('/setdb')
def set_db():
    try:
        cur = mysql.connection.cursor()
        print('connection start')
        # 1. Create Database (if it doesn't exist)
        cur.execute("CREATE DATABASE IF NOT EXISTS crud_db")
         print('DB created')
        # 2. Switch to the database
        cur.execute("USE crud_db")
         print('using DB')
        # 3. Create Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tbl_user (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(45) NOT NULL,
                user_email VARCHAR(45) NOT NULL
            )
        """)
         print('table created')
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Database and Table created successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
