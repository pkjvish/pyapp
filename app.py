from flask import Flask, request, jsonify, render_template_string
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

def get_all_users_list(cursor):
    """Helper to fetch and parse the raw database records."""
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

# SPA Dashboard UI Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask SPA Dashboard</title>
    <script src="jsdelivr.net"></script>
</head>
<body class="bg-slate-50 font-sans text-slate-900 antialiased">
    <div class="mx-auto max-w-5xl px-4 py-8">
        
        <!-- Header -->
        <header class="mb-8 flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
                <h1 class="text-3xl font-black tracking-tight text-indigo-600">Single Page Application</h1>
                <p class="mt-1 text-sm text-slate-500">Add or remove users instantly without page reloads</p>
            </div>
            <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-600/20">
                <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span> Live SPA Mode
            </span>
        </header>

        <!-- Status Toast Notifications -->
        <div id="toast" class="hidden mb-6 p-4 rounded-xl text-sm font-medium transition shadow-sm border"></div>

        <div class="grid grid-cols-1 gap-8 md:grid-cols-3">
            <!-- Sidebar Actions Column -->
            <div class="space-y-6 md:col-span-1">
                <!-- Add User Form -->
                <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h3 class="mb-4 text-base font-bold text-slate-800">➕ Add New User</h3>
                    <form id="addForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Full Name</label>
                            <input type="text" id="addName" required placeholder="Pankaj Kumar" 
                                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                        </div>
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Email Address</label>
                            <input type="email" id="addEmail" required placeholder="pankaj@example.com" 
                                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                        </div>
                        <button type="submit" class="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition">
                            Save User
                        </button>
                    </form>
                </div>

                <!-- Delete User Form -->
                <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h3 class="mb-4 text-base font-bold text-slate-800">🗑️ Delete User by Name</h3>
                    <form id="deleteForm" class="space-y-4">
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">User Name</label>
                            <input type="text" id="deleteName" required placeholder="Exact name to delete" 
                                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-rose-500 focus:outline-none focus:ring-1 focus:ring-rose-500">
                        </div>
                        <button type="submit" class="w-full rounded-lg bg-rose-600 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-rose-700 transition">
                            Delete User
                        </button>
                    </form>
                </div>
            </div>

            <!-- SPA Live User Directory Table -->
            <div class="md:col-span-2">
                <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
                    <div class="border-b border-slate-100 bg-slate-50/70 px-6 py-4 flex justify-between items-center">
                        <h3 class="text-base font-bold text-slate-800">📋 Active Database Directory</h3>
                        <a href="/users" target="_blank" class="text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:underline">Raw JSON Engine ↗</a>
                    </div>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse text-sm">
                            <thead>
                                <tr class="border-b border-slate-200 bg-slate-50 text-xs font-bold uppercase tracking-wider text-slate-500">
                                    <th class="px-6 py-3">ID</th>
                                    <th class="px-6 py-3">User Name</th>
                                    <th class="px-6 py-3">User Email</th>
                                    <th class="px-6 py-3 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody id="userTableBody" class="divide-y divide-slate-100">
                                <!-- JavaScript dynamically renders rows here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- AJAX SPA Engine Logic -->
    <script>
        // Shared Headers config so Flask recognizes the Dashboard Client
        const dashboardHeaders = { 'X-Requested-From': 'Dashboard' };

        function showToast(message, isSuccess = true) {
            const toast = document.getElementById('toast');
            toast.className = `p-4 mb-6 rounded-xl text-sm font-medium transition shadow-sm border ${
                isSuccess ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-rose-50 text-rose-800 border-rose-200'
            }`;
            toast.innerText = message;
        }

        // 1. ASYNC FETCH: Load Users Into Table Without Refreshing
        async function fetchUsers() {
            try {
                const response = await fetch('/users', { headers: dashboardHeaders });
                const users = await response.json();
                const tbody = document.getElementById('userTableBody');
                tbody.innerHTML = '';

                if(users.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" class="px-6 py-10 text-center text-slate-400 italic">No user profiles found on disk.</td></tr>`;
                    return;
                }

                users.forEach(user => {
                    tbody.innerHTML += `
                        <tr class="hover:bg-slate-50/80 transition">
                            <td class="px-6 py-4 font-mono font-bold text-slate-400">#${user.user_id}</td>
                            <td class="px-6 py-4 font-semibold text-slate-900">${user.user_name}</td>
                            <td class="px-6 py-4 text-slate-600">${user.user_email}</td>
                            <td class="px-6 py-4 text-right">
                                <button onclick="quickDelete('${user.user_name}')" class="rounded-md bg-rose-50 px-2.5 py-1 text-xs font-bold text-rose-600 hover:bg-rose-100 transition">Remove</button>
                            </td>
                        </tr>
                    `;
                });
            } catch (err) {
                showToast("Could not sync data directory.", false);
            }
        }

        // 2. ASYNC POST: Add user instantly
        document.getElementById('addForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('addName').value;
            const email = document.getElementById('addEmail').value;

            const res = await fetch(`/userc?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}`, { headers: dashboardHeaders });
            if(res.ok) {
                showToast(`User "${name}" saved successfully!`);
                document.getElementById('addForm').reset();
                fetchUsers();
            } else {
                const data = await res.json();
                showToast(data.error || "Failed to add user.", false);
            }
        });

        // 3. ASYNC DELETE: Remove user instantly
        document.getElementById('deleteForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('deleteName').value;
            await quickDelete(name);
            document.getElementById('deleteForm').reset();
        });

        async function quickDelete(name) {
            const res = await fetch(`/userd?name=${encodeURIComponent(name)}`, { headers: dashboardHeaders });
            if(res.ok) {
                showToast(`User "${name}" removed successfully.`);
                fetchUsers();
            } else {
                showToast(`User "${name}" could not be found.`, false);
            }
        }

        // Initial Load on bootup
        window.onload = fetchUsers;
    </script>
</body>
</html>
"""

# 1. LIST ALL USERS FROM DATABASE
@app.route('/users', methods=['GET'])
def list_all_users():
    try:
        cur = mysql.connection.cursor()
        user_list = get_all_users_list(cur)
        cur.close()
        
        # If the request comes from the Web Dashboard SPA, don't append instructional string
        if request.headers.get('X-Requested-From') == 'Dashboard':
            return jsonify(user_list), 200
            
        # Otherwise, append layout rules for direct URL lookups
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
        
        # If it's a dashboard background request, return clean data right away
        if request.headers.get('X-Requested-From') == 'Dashboard':
            return jsonify(user_list), 201
            
        # If run directly via address bar URL, append instruction block
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
            
            if request.headers.get('X-Requested-From') == 'Dashboard':
                return jsonify({"error": f"User '{name}' not found"}), 404
                
            user_list.append({
                "error": f"User '{name}' not found.",
                "instruction": "Verify spelling or review active profiles at /users"
            })
            return jsonify(user_list), 404
            
        cur.execute("DELETE FROM tbl_user WHERE user_name = %s", (name,))
        mysql.connection.commit()
        
        user_list = get_all_users_list(cur)
        cur.close()
        
        if request.headers.get('X-Requested-From') == 'Dashboard':
            return jsonify(user_list), 200
            
        user_list.append({
            "instruction": f"User '{name}' deleted successfully! View changes above or use /userc to append values."
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. HOME ROUTE SERVING THE RESPONSIVE SPA
@app.route('/', methods=['GET'])
def home_dashboard():
    return render_template_string(DASHBOARD_HTML)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
