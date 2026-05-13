from flask import Flask, request, jsonify, render_template_string
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

# Helper function to fetch the complete formatted user list
def get_all_users_list(cursor):
    cursor.execute("SELECT user_id, user_name, user_email FROM tbl_user")
    rows = cursor.fetchall()
    
    user_list = []
    for row in rows:
        user_list.append({
            "user_id": row[0],
            "user_name": row[1],
            "user_email": row[2]
        })
    return user_list

# HTML/CSS/JS Dashboard Template String
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask CRUD Dashboard</title>
    <!-- Tailwind CSS for a modern, clean look -->
    <script src="tailwindcss.com"></script>
</head>
<body class="bg-gray-50 font-sans antialiased text-gray-900">
    <div class="max-w-5xl mx-auto px-4 py-8">
        <!-- Header -->
        <header class="mb-8 border-b pb-4 flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-extrabold text-blue-600 tracking-tight">Database Dashboard</h1>
                <p class="text-sm text-gray-500 mt-1">Live interface connected to MySQL (crud_db)</p>
            </div>
            <span class="inline-flex items-center gap-1.5 py-1.5 px-3 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <span class="size-1.5 inline-block rounded-full bg-green-500"></span> Live Status: Connected
            </span>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Left Side Actions Column -->
            <div class="space-y-6 md:col-span-1">
                <!-- Create User Box -->
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                        ➕ Add User <span class="text-xs text-blue-500 font-normal">(/userc)</span>
                    </h3>
                    <form action="/userc" method="GET" class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold uppercase text-gray-500 mb-1">Full Name</label>
                            <input type="text" name="name" required placeholder="John Doe" 
                                class="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold uppercase text-gray-500 mb-1">Email Address</label>
                            <input type="email" name="email" required placeholder="john@example.com" 
                                class="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg text-sm transition shadow-sm">
                            Add via URL Redirect
                        </button>
                    </form>
                </div>

                <!-- Delete User Box -->
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                        🗑️ Delete User <span class="text-xs text-red-500 font-normal">(/userd)</span>
                    </h3>
                    <form action="/userd" method="GET" class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold uppercase text-gray-500 mb-1">User Name</label>
                            <input type="text" name="name" required placeholder="Exact username to delete" 
                                class="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
                        </div>
                        <button type="submit" class="w-full bg-red-500 hover:bg-red-600 text-white font-medium py-2 rounded-lg text-sm transition shadow-sm">
                            Delete via URL Redirect
                        </button>
                    </form>
                </div>
            </div>

            <!-- Right Side User Directory Table Column -->
            <div class="md:col-span-2">
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                        <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
                            📋 Active User Database <span class="text-xs text-gray-400 font-normal">(/users)</span>
                        </h3>
                        <a href="/users" target="_blank" class="text-xs font-medium text-blue-600 hover:underline">
                            View Raw JSON ↗
                        </a>
                    </div>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse text-sm">
                            <thead>
                                <tr class="bg-gray-100 border-b border-gray-200 text-xs font-semibold uppercase text-gray-600 tracking-wider">
                                    <th class="px-6 py-3">ID</th>
                                    <th class="px-6 py-3">User Name</th>
                                    <th class="px-6 py-3">User Email</th>
                                    <th class="px-6 py-3 text-right">Quick Action</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                {% for user in users %}
                                <tr class="hover:bg-gray-50 transition">
                                    <td class="px-6 py-4 font-semibold text-gray-500">#{{ user.user_id }}</td>
                                    <td class="px-6 py-4 font-medium text-gray-900">{{ user.user_name }}</td>
                                    <td class="px-6 py-4 text-gray-600">{{ user.user_email }}</td>
                                    <td class="px-6 py-4 text-right">
                                        <a href="/userd?name={{ user.user_name }}" 
                                           class="inline-flex items-center text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 px-2.5 py-1 rounded-md transition">
                                            Remove
                                        </a>
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="4" class="px-6 py-12 text-center text-gray-400 italic">
                                        No entries found in tbl_user. Use the sidebar to append data records.
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# 1. LIST ALL USERS FROM DATABASE (RAW JSON)
@app.route('/users', methods=['GET'])
def list_all_users():
    try:
        cur = mysql.connection.cursor()
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": "To add a user, go to /userc?name=abc&email=abc.com. To delete a user, go to /userd?name=abc"
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. ADD USER VIA URL QUERY PARAMETERS
@app.route('/userc', methods=['GET'])
def add_user_via_url():
    name = request.args.get('name')
    email = request.args.get('email')

    if not name or not email:
        return jsonify({
            "error": "Missing query parameters.",
            "instruction": "Please build your URL target exactly like this: /userc?name=abc&email=abc.com"
        }), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_user(user_name, user_email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": "User added successfully! Modify your parameters to add more users: /userc?name=abc&email=abc.com"
        })
        return jsonify(user_list), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. DELETE USER BY URL QUERY PARAMETER (BY NAME)
@app.route('/userd', methods=['GET'])
def delete_user_via_url():
    name = request.args.get('name')

    if not name:
        return jsonify({
            "error": "Missing target query parameter.",
            "instruction": "Please pass the user name to remove like this: /userd?name=abc"
        }), 400

    try:
        cur = mysql.connection.cursor()
        
        cur.execute("SELECT user_id FROM tbl_user WHERE user_name = %s", (name,))
        if not cur.fetchone():
            user_list = get_all_users_list(cur)
            cur.close()
            user_list.append({
                "error": f"User '{name}' not found.",
                "instruction": "Verify spelling or review active profiles at /users"
            })
            return jsonify(user_list), 404
            
        cur.execute("DELETE FROM tbl_user WHERE user_name = %s", (name,))
        mysql.connection.commit()
        
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": f"User '{name}' deleted successfully! View changes above or use /userc to append values."
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. HOME ROUTE SERVING THE RESPONSIVE GUI
@app.route('/', methods=['GET'])
def home_dashboard():
    try:
        cur = mysql.connection.cursor()
        current_users = get_all_users_list(cur)
        cur.close()
        # Render the template string and feed database data into the HTML loop
        return render_template_string(DASHBOARD_HTML, users=current_users)
    except Exception as e:
        return f"<h3>Database Connection Error:</h3><p>{str(e)}</p><p>Ensure your pipeline's MySQL initialization step executed successfully.</p>", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
