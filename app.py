from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

# 1. URL Query Parameter Method (GET)
@app.route('/users', methods=['GET'])
def add_user_via_query():
    name = request.args.get('name')
    email = request.args.get('email')

    if not name or not email:
        return jsonify({"error": "Missing query parameters. Provide name and email."}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_user(user_name, user_email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": f"User '{name}' added via URL successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. JSON Body Payload Method (POST) - Renamed route to keep it distinct if needed
@app.route('/save/users', methods=['POST'])
def add_user_via_json():
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Missing JSON body data."}), 400
        
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_user(user_name, user_email) VALUES (%s, %s)", (data['name'], data['email']))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "User added via JSON successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
