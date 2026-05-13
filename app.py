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

# Redesigned Bootstrap 5 SPA Dashboard UI Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Bootstrap SPA Dashboard</title>
    <!-- Bootstrap 5 CSS CDN -->
    <link href="jsdelivr.net" rel="stylesheet">
    <!-- Bootstrap Icons CDN -->
    <link href="jsdelivr.net" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .card { border: none; border-radius: 12px; }
        .table-container { border-radius: 12px; overflow: hidden; }
    </style>
</head>
<body>
    <div class="container py-5">
        
        <!-- Header -->
        <header class="d-flex flex-column flex-md-row justify-content-between align-items-md-center border-b pb-3 mb-4">
            <div>
                <h1 class="fw-black text-primary display-6 mb-1"><i class="bi bi-layers-half"></i> Single Page Application</h1>
                <p class="text-muted mb-0">Manage your MySQL database directory cleanly on a single page.</p>
            </div>
            <div class="mt-2 mt-md-0">
                <span class="badge bg-success-subtle text-success border border-success-subtle rounded-pill px-3 py-2">
                    <i class="bi bi-circle-fill me-1 small"></i> Live SPA Mode
                </span>
            </div>
        </header>

        <!-- Dynamic Status Alerts -->
        <div id="statusAlert" class="alert d-none mb-4" role="alert"></div>

        <div class="row g-4">
            <!-- Left Sidebars Forms -->
            <div class="col-12 col-md-4">
                
                <!-- Add User Card -->
                <div class="card shadow-sm border p-4 mb-4 bg-white">
                    <h5 class="card-title fw-bold text-dark mb-3">
                        <i class="bi bi-person-plus-fill text-primary"></i> Add New User
                    </h5>
                    <form id="addForm">
                        <div class="mb-3">
                            <label class="form-label text-uppercase text-muted fw-bold small">Full Name</label>
                            <input type="text" id="addName" required placeholder="Pankaj Kumar" class="form-control form-control-lg fs-6">
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-uppercase text-muted fw-bold small">Email Address</label>
                            <input type="email" id="addEmail" required placeholder="pankaj@example.com" class="form-control form-control-lg fs-6">
                        </div>
                        <button type="submit" class="btn btn-primary w-100 fw-semibold py-2">
                            <i class="bi bi-check-circle-fill"></i> Save User
                        </button>
                    </form>
                </div>

                <!-- Delete User Card -->
                <div class="card shadow-sm border p-4 bg-white">
                    <h5 class="card-title fw-bold text-dark mb-3">
                        <i class="bi bi-person-x-fill text-danger"></i> Delete User by Name
                    </h5>
                    <form id="deleteForm">
                        <div class="mb-3">
                            <label class="form-label text-uppercase text-muted fw-bold small">User Name</label>
                            <input type="text" id="deleteName" required placeholder="Exact name to delete" class="form-control form-control-lg fs-6">
                        </div>
                        <button type="submit" class="btn btn-danger w-100 fw-semibold py-2">
                            <i class="bi bi-trash3-fill"></i> Delete User
                        </button>
                    </form>
                </div>
                
            </div>

            <!-- Right User List Table -->
            <div class="col-12 col-md-8">
                <div class="card shadow-sm border bg-white table-container">
                    <div class="card-header bg-light border-0 px-4 py-3 d-flex justify-content-between align-items-center">
                        <h5 class="mb-0 fw-bold text-dark"><i class="bi bi-table"></i> Active Database Directory</h5>
                        <a href="/users" target="_blank" class="btn btn-sm btn-link text-decoration-none fw-semibold">
                            Raw JSON Engine <i class="bi bi-box-arrow-up-right"></i>
                        </a>
                    </div>
                    
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light text-uppercase fs-7 text-muted border-bottom">
                                <tr>
                                    <th class="px-4 py-3">ID</th>
                                    <th class="py-3">User Name</th>
                                    <th class="py-3">User Email</th>
                                    <th class="px-4 py-3 text-end">Action</th>
                                </tr>
                            </thead>
                            <tbody id="userTableBody">
                                <!-- Asynchronous script appends rows here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- AJAX JavaScript Engine -->
    <script>
        const dashboardHeaders = { 'X-Requested-From': 'Dashboard' };

        function displayAlert(message, isSuccess = true) {
            const alertBox = document.getElementById('statusAlert');
            alertBox.className = `alert mb-4 d-block ${isSuccess ? 'alert-success' : 'alert-danger'}`;
            alertBox.innerHTML = isSuccess ? `<i class="bi bi-check-circle-fill me-2"></i> ${message}` : `<i class="bi bi-exclamation-triangle-fill me-2"></i> ${message}`;
            
            // Auto hide after 4 seconds
            setTimeout(() => { alertBox.className = 'alert d-none'; }, 4000);
        }

        // 1. FETCH ASYNC: Load users into bootstrap rows
        async function fetchUsers() {
            try {
                const response = await fetch('/users', { headers: dashboardHeaders });
                const users = await response.json();
                const tbody = document.getElementById('userTableBody');
                tbody.innerHTML = '';

                if(users.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" class="text-center py-5 text-muted italic"><i class="bi bi-folder-symlink h3 d-block text-muted"></i>No user profiles found on disk.</td></tr>`;
                    return;
                }

                users.forEach(user => {
                    tbody.innerHTML += `
                        <tr>
                            <td class="px-4 font-monospace text-muted fw-bold">#${user.user_id}</td>
                            <td class="fw-semibold text-dark">${user.user_name}</td>
                            <td class="text-secondary">${user.user_email}</td>
                            <td class="px-4 text-end">
                                <button onclick="quickDelete('${user.user_name}')" class="btn btn-sm btn-outline-danger px-3">
                                    <i class="bi bi-trash"></i> Remove
                                </button>
                            </td>
                        </tr>
                    `;
                });
            } catch (err) {
                displayAlert("Could not connect to database directory pipeline.", false);
            }
        }

        // 2. POST ASYNC: Add entries 
        document.getElementById('addForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('addName').value;
            const email = document.getElementById('addEmail').value;

            const res = await fetch(`/userc?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}`, { headers: dashboardHeaders });
            if(res.ok) {
                displayAlert(`User "${name}" has been appended to active records.`);
                document.getElementById('addForm').reset();
                fetchUsers();
            } else {
                const data = await res.json();
                displayAlert(data.error || "Failed to append user.", false);
            }
        });

        // 3. DELETE ASYNC: Wipe line records
        document.getElementById('deleteForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('deleteName').value;
            await quickDelete(name);
            document.getElementById('deleteForm').reset();
        });

        async function quickDelete(name) {
            const res = await fetch(`/userd?name=${encodeURIComponent(name)}`, { headers: dashboardHeaders });
            if(res.ok) {
                displayAlert(`User "${name}" has been wiped from data maps.`);
                fetchUsers();
            } else {
                displayAlert(`User "${name}" could not be located in database.`, false);
            }
        }

        window.onload = fetchUsers;
    </script>
    <!-- Bootstrap Bundle JS CDN -->
    <script src="jsdelivr.net"></script>
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
        
        if request.headers.get('X-Requested-From') == 'Dashboard':
            return jsonify(user_list), 200
            
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
        
        if request.headers.get('X-Requested-From') == 'Dashboard':
            return jsonify(user_list), 201
            
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
