from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

@app.route('/users', methods=['GET'])
def add_user_via_query():
    name = request.args.get('name')
    email = request.args.get('email')

    try:
        cur = mysql.connection.cursor()
        
        # 1. Insert the new user entry from URL parameters
        cur.execute("INSERT INTO tbl_user(user_name, user_email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        
        # 2. Fetch the entire updated user list from the database
        cur.execute("SELECT user_id, user_name, user_email FROM tbl_user")
        rows = cur.fetchall() # Returns a tuple of records
        cur.close()
        
        # 3. Format database records into a clean JSON serializable list
        user_list = []
        for row in rows:
            user_list.append({
                "user_id": row[0],
                "user_name": row[1],
                "user_email": row[2]
            })
            
        # 4. Append the instruction block as the LAST row of the JSON array
        user_list.append({
            "instruction": "To add more users, modify your URL parameters like this: /users?name=abc&email=abc.com"
        })
        
        return jsonify(user_list), 201

    except Exception as e:
        return jsonify({
            "error": str(e),
            "instruction": "Verify that your MySQL server is running and the 'crud_db' database is fully initialized."
        }), 500


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
