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

@app.route('/users', methods=['GET'])
def add_user():
    # Extract query parameters from the URL string
    name = request.args.get('name')
    email = request.args.get('email')

    # Safety validation check to make sure both values are present
    if not name or not email:
        return jsonify({"error": "Missing query parameters. Please provide name and email."}), 400

    try:
        cur = mysql.connection.cursor()
        # Insert extracted URL parameters into the database
        cur.execute("INSERT INTO tbl_user(user_name, user_email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": f"User '{name}' added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
