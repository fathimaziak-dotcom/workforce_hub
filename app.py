from flask import Flask, request,render_template, request, redirect, url_for, session
import mysql.connector
import base64
from flask import flash

app = Flask(__name__)

app.secret_key = "super_secret_key_change_this_later"


# --- SUBMIT ROUTE ---
@app.route('/submit', methods=['POST'])
def submit():
    empcode =request.form.get('emp_code')
    employee = request.form.get('employee_name') 
    phone = request.form.get('phone_number')
    email = request.form.get('email_id')
    gender =request.form.get('gender')
    dateofbirth = request.form.get('dob')
    dateofjoining = request.form.get('date_join')
    temper = request.form.get('tem_per')
    password = request.form.get('password')
    role =request.form.get('role')
    photo_file = request.files.get('photo_data')
    photo = photo_file.read() if photo_file and photo_file.filename !='' else None
    if not employee:
        return "Error: No name provided!", 400
        
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Zia@2008",
            database="absent_db"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employee_absences (emp_code,employee_name,phone_number,email_id,gender,dob,date_join,tem_per,photo_data,password,role) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (empcode,employee,phone,email,gender,dateofbirth,dateofjoining,temper,photo,password,role))
        conn.commit()
        cursor.close()
        conn.close()

        return f"<h3>The {employee} has been saved!</h3><br><button onclick='window.history.back()'>Go Back</button>"
    except Exception as e:
        error_msg = str(e)
        if "Duplicate entry" in error_msg:
            if "employee_name" in error_msg:
                return "<h3>Error: This Employee Name already exists!</h3><br><button onclick='window.history.back()'>Go Back</button>"
            elif "phone_number" in error_msg:
                return "<h3>Error: This Phone Number is already registered!</h3><br><button onclick='window.history.back()'>Go Back</button>"
            elif "email_id" in error_msg:
                return "<h3>Error: This Email ID is already registered!</h3><br><button onclick='window.history.back()'>Go Back</button>"
            else:
                return "<h3>Error: This Employee Code is already assigned!</h3><br><button onclick='window.history.back()'>Go Back</button>"
        
        return f"Database Error: {error_msg}"
    
# --- VIEW ROUTE ---
# --- VIEW ROUTE ---
@app.route('/view')
def view_names():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Zia@2008",
            database="absent_db"
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, emp_code, employee_name, phone_number, email_id,
                   gender, dob, date_join, tem_per, photo_data, password, role
            FROM employee_absences
        """)
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        rows = []
        for row in records:
            if row[9]:
                b64_photo = base64.b64encode(row[9]).decode('utf-8')
                photo_tag = f'<img src="data:image/jpeg;base64,{b64_photo}" width="48" height="48" style="border-radius:6px;object-fit:cover;">'
            else:
                photo_tag = "—"

            rows.append({
                "id": row[0],
                "emp_code": row[1],
                "name": row[2],
                "phone": row[3],
                "email": row[4],
                "gender": row[5],
                "dob": row[6],
                "date_join": row[7],
                "status": row[8],
                "photo_tag": photo_tag,
                "password" :row[10],
                "role": row[11]
            })

        return render_template('view.html', rows=rows)

    except Exception as e:
        return f"Database Error: {str(e)}"


# --- EDIT ROUTE ---
@app.route('/edit/<int:emp_id>', methods=['GET', 'POST'])
def edit_employee(emp_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Zia@2008",
        database="absent_db"
    )
    cursor = conn.cursor()

    if request.method == 'POST':
        emp_code = request.form.get('emp_code')
        employee_name = request.form.get('employee_name')
        phone = request.form.get('phone_number')
        email = request.form.get('email_id')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        date_join = request.form.get('date_join')
        tem_per = request.form.get('tem_per')
        password = request.form.get('password')
        role = request.form.get('role')

        cursor.execute("""
            UPDATE employee_absences
            SET emp_code=%s, employee_name=%s, phone_number=%s, email_id=%s,
                gender=%s, dob=%s, date_join=%s, tem_per=%s,password=%s, role=%s
            WHERE id=%s
        """, (emp_code, employee_name, phone, email, gender, dob, date_join, tem_per, password , role, emp_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_names'))

    else:
        cursor.execute("""
            SELECT id, emp_code, employee_name, phone_number, email_id,
                   gender, dob, date_join, tem_per,password ,role
            FROM employee_absences WHERE id=%s
        """, (emp_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return "Employee not found", 404

        employee = {
            "id": row[0], "emp_code": row[1], "name": row[2], "phone": row[3],
            "email": row[4], "gender": row[5], "dob": row[6],
            "date_join": row[7], "status": row[8],"password":row[9], "role": row[10],
        }
        return render_template('edit.html', employee=employee)

       
@app.route('/')
@app.route('/login')
def login_page():
    return render_template('login.html')

# 2. Processes the username/password and checks the database
@app.route('/login_check', methods=['POST'])
def login_check():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Zia@2008",
                database="absent_db"
            )
            cursor = conn.cursor()
            
            query = "SELECT employee_name, role, emp_code, tem_per FROM employee_absences WHERE email_id = %s AND password = %s"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if user:
                session['user_name'] = user[0]
                session['user_role'] = user[1] 
                session['emp_code'] = user[2]
                session['tem_per'] =user[3]
                
                # Redirect based on the database role column
                if session['user_role'] == 'admin':
                    return redirect('/admin') # Bounces admin to your master table view
                elif session['user_role'] == 'manager':
                    return redirect('/manager/dashboard')
                elif session['user_role'] == 'employee':
                    return redirect('/employee/dashboard')
            else:
                return "<h3>Error: Invalid Email or Password. Please try again.</h3>"
                
        except Exception as e:
            return f"<h3>Database Connection Error: {str(e)}</h3>"


# ==========================================
# SECTION 4: TEMPORARY DASHBOARD ROUTE WORKAROUNDS
# ==========================================
@app.route('/employee/dashboard')
def employee_dashboard():
    if 'user_role' not in session or session['user_role'] != 'employee':
        return "<h3>Access Denied!</h3>", 403
        
    user_name = session.get('user_name')
    
    # Connect to your database
    connection = mysql.connector.connect(host="localhost", user="root", password="Zia@2008", database="absent_db")
    cursor = connection.cursor()
    
    # CORRECTED QUERY: Using 'action_type' and 'timestamp' from your schema
    cursor.execute("SELECT action_type FROM attendance WHERE employee_name = %s ORDER BY timestamp DESC LIMIT 1", (user_name,))
    last_punch = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    # Check if their last action in the database was "Punch In"
    is_checked_in = True if (last_punch and last_punch[0] == "Punch In") else False
    
    # Send this true/false status to your HTML template
    return render_template('employee.html', checked_in=is_checked_in)

@app.route('/admin')
def admin_page():
    # This tells Flask to load and display your form file
    return render_template('admin.html')



   
import mysql.connector
from datetime import datetime
from flask import flash, redirect, url_for, session, request

@app.route('/checkin', methods=['POST'])
def checkin():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    try:
        connection = mysql.connector.connect(host="localhost", user="root", password="Zia@2008", database="absent_db")
        cursor = connection.cursor()
        
        query = "INSERT INTO attendance (employee_name, action_type, timestamp) VALUES (%s, %s, %s)"
        values = (session['user_name'], "Punch In", datetime.now())
        
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        
        flash("Success! Your Punch In timestamp has been securely recorded.", "success")
    except Exception as e:
        flash(f"Database Error: {str(e)}", "danger")
        
    return redirect(url_for('employee_dashboard'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_name' not in session:
        return redirect(url_for('login'))
        
    try:
        connection = mysql.connector.connect(host="localhost", user="root", password="Zia@2008", database="absent_db")
        cursor = connection.cursor()
        
        query = "INSERT INTO attendance (employee_name, action_type, timestamp) VALUES (%s, %s, %s)"
        values = (session['user_name'], "Punch Out", datetime.now())
        
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        
        flash("Success! Your Punch Out timestamp has been securely recorded.", "success")
    except Exception as e:
        flash(f"Database Error: {str(e)}", "danger")
        
    return redirect(url_for('employee_dashboard'))

@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    if 'user_name' not in session:
        return redirect(url_for('login'))

    leave_date = request.form.get('leave_date')
    reason = request.form.get('reason')
    tem_per = session.get('tem_per')

    try:
        connection = mysql.connector.connect(host="localhost", user="root", password="Zia@2008", database="absent_db")
        cursor = connection.cursor()

        # Count this employee's approved leaves in the same month as the requested date
        cursor.execute(
            "SELECT COUNT(*) FROM leave_requests WHERE employee_name = %s AND status = 'Approved' "
            "AND MONTH(leave_date) = MONTH(%s) AND YEAR(leave_date) = YEAR(%s)",
            (session['user_name'], leave_date, leave_date)
        )
        used = cursor.fetchone()[0]

        cursor.execute("SELECT monthly_limit FROM leave_policies WHERE employee_type = %s", (tem_per,))
        row = cursor.fetchone()
        limit = row[0] if row else 0
        exceeded = used >= limit

        query = "INSERT INTO leave_requests (employee_name, leave_date, reason, status, exceeds_limit) VALUES (%s, %s, %s, %s, %s)"
        values = (session['user_name'], leave_date, reason, 'Pending', exceeded)

        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

        flash("Success! Your absence request has been logged.", "success")
    except Exception as e:
        flash(f"Database Error: {str(e)}", "danger")

    return redirect(url_for('employee_dashboard'))


@app.route('/attendance_history')
def attendance_history():
    if 'user_name' not in session:
        return redirect(url_for('login'))
        
    try:
        connection = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="Zia@2008", 
            database="absent_db"
        )
        cursor = connection.cursor(dictionary=True) # Returns data as a clean dictionary list
        
        # Pull records specifically matching the logged-in employee
        query = "SELECT action_type, timestamp FROM attendance WHERE employee_name = %s ORDER BY timestamp DESC"
        cursor.execute(query, (session['user_name'],))
        records = cursor.fetchall()
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error fetching history: {e}")
        records = []
        
    return render_template('attendance_history.html', history=records)

@app.route('/leave_history')
def leave_history():
    if 'user_name' not in session:
        return redirect(url_for('login'))
        
    try:
        connection = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="Zia@2008", 
            database="absent_db"
        )
        cursor = connection.connector.cursor(dictionary=True) if hasattr(connection, 'connector') else connection.cursor(dictionary=True)
        
        # Pull leave requests matching the logged-in employee
        query = "SELECT leave_date, reason, status, exceeds_limit FROM leave_requests WHERE employee_name = %s ORDER BY id DESC"
        cursor.execute(query, (session['user_name'],))
        records = cursor.fetchall()
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error fetching leave history: {e}")
        records = []
        
    return render_template('leave_history.html', leaves=records)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_name' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        try:
            connection = mysql.connector.connect(
                host="localhost", 
                user="root", 
                password="Zia@2008", 
                database="absent_db"
            )
            cursor = connection.cursor(dictionary=True)
            
            # 1. Fetch the password for the specific employee currently logged in
            # Note: If your name column is called something else (like 'name'), change 'employee_name' below.
            query_find = "SELECT password FROM employee_absences WHERE employee_name = %s"
            cursor.execute(query_find, (session['user_name'],))
            user = cursor.fetchone()
            
            if user:
                # 2. Check if the current password they typed matches the database
                if user['password'] == current_password:
                    # 3. Update the password row for this employee only
                    query_update = "UPDATE employee_absences SET password = %s WHERE employee_name = %s"
                    cursor.execute(query_update, (new_password, session['user_name']))
                    connection.commit()
                    flash("Password updated successfully!", "success")
                else:
                    flash("Incorrect current password.", "danger")
            else:
                flash("Employee profile record not found.", "danger")
                
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"!!! SETTINGS DATABASE ERROR: {e}")
            flash(f"Database Error: {e}", "danger")
            
        return redirect(url_for('settings'))
        
    return render_template('settings.html')


 

@app.route('/manager/dashboard')
def manager_dashboard():
    # 1. Security Check
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    # 2. Database Connection Initialization
    import pymysql
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Zia@2008",  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database="absent_db",
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Count total employees — only role = 'employee', excludes admin/manager
            cursor.execute("SELECT COUNT(*) AS total FROM employee_absences WHERE role = 'employee'")
            total_employees = cursor.fetchone()['total']

            # Count present today — distinct employees who punched in today
            cursor.execute("""
                SELECT COUNT(DISTINCT employee_name) AS count
                FROM attendance
                WHERE action_type = 'Punch In' AND DATE(timestamp) = CURDATE()
            """)
            present_count = cursor.fetchone()['count']

            # Count on leave (approved leave requests)
            # Replace your existing on_leave_count query in manager_dashboard() with this:

            cursor.execute("SELECT COUNT(*) AS count FROM leave_requests ""WHERE status='Approved' AND leave_date = CURDATE()")
            on_leave_count = cursor.fetchone()['count']

# NEW — add this so you can actually show who's on leave today
            cursor.execute("SELECT employee_name AS name FROM leave_requests ""WHERE status='Approved' AND leave_date = CURDATE()")
            on_leave_list = cursor.fetchall()



            # Pending approvals
            cursor.execute("SELECT COUNT(*) AS count FROM leave_requests WHERE status='Pending'")
            pending_approvals_count = cursor.fetchone()['count']

            # Calculate absent
            absent_count = max(0, total_employees - present_count - on_leave_count)

            # Late arrivals today — first Punch In after 9:30 AM
            cursor.execute("""
                SELECT employee_name AS name, MIN(timestamp) AS check_in_time
                FROM attendance
                WHERE action_type = 'Punch In' AND DATE(timestamp) = CURDATE()
                GROUP BY employee_name
                HAVING MIN(timestamp) > CONCAT(CURDATE(), ' 09:30:00')
            """)
            late_arrivals = cursor.fetchall()
            

            # Pending leave requests, for the Quick Leave Approvals panel
            cursor.execute("""
                SELECT employee_name, reason
                FROM leave_requests
                WHERE status = 'Pending'
            """)
            pending_leaves_list = cursor.fetchall()

            # Approved leaves that haven't started yet
            cursor.execute("""
                SELECT employee_name AS name, leave_date AS start_date
                FROM leave_requests
                WHERE status = 'Approved' AND leave_date >= CURDATE()
                ORDER BY leave_date
            """)
            upcoming_absences = cursor.fetchall()

    except Exception as e:
        print(f"Database Error: {e}")
        # If the database fails, default everything to 0 so the page still loads!
        total_employees = present_count = on_leave_count = absent_count = pending_approvals_count = 0
        late_arrivals = pending_leaves_list = upcoming_absences = []
    finally:
        connection.close()

    # Calculate percentage safely
    present_percentage = f"{int((present_count / total_employees) * 100)}%" if total_employees > 0 else "0%"

    # 3. Handing the variables over to the HTML
    return render_template(
        'manager.html',
        total_employees=total_employees,
        present_count=present_count,
        on_leave_count=on_leave_count,
        on_leave_list=on_leave_list,
        absent_count=absent_count,
        pending_approvals_count=pending_approvals_count,
        present_percentage=present_percentage,
        late_arrivals=late_arrivals,
        pending_leaves_list=pending_leaves_list,
        upcoming_absences=upcoming_absences
    )


 


import mysql.connector
from datetime import datetime, date, timedelta
from collections import defaultdict
from flask import render_template, request


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # <-- replace with your actual MySQL user
        password="Zia@2008",          # <-- replace with your actual MySQL password
        database="absent_db"
    )


LATE_CUTOFF = datetime.strptime("09:30", "%H:%M").time()


@app.route('/manager/attendance_log')
def attendance_log():
    # How far back to build the log. The trend chart and "This month" /
    # "This week" filters all run client-side against whatever we send,
    # so 90 days gives a healthy window without over-fetching.
    days_back = int(request.args.get('days', 90))
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # ---- 1. Employee master list -------------------------------------
    # Only role='employee' — same definition your dashboard's
    # "Total Employees" stat uses. Without this filter, admin/manager
    # accounts (e.g. Fathima Zia K, Sameer K) get counted too, which
    # inflates the totals and makes "absent" look far worse than it is.
    cur.execute("""
        SELECT employee_name, emp_code, tem_per, role, date_join
        FROM employee_absences
        WHERE role = 'employee'
    """)
    employees = cur.fetchall()

    # ---- 2. Raw punches in range ---------------------------------------
    cur.execute("""
        SELECT employee_name, action_type, timestamp
        FROM attendance
        WHERE DATE(timestamp) BETWEEN %s AND %s
        ORDER BY employee_name, timestamp
    """, (start_date, end_date))
    punches = cur.fetchall()

    # ---- 3. Approved leave in range -------------------------------------
    cur.execute("""
        SELECT employee_name, leave_date, reason
        FROM leave_requests
        WHERE status = 'Approved' AND leave_date BETWEEN %s AND %s
    """, (start_date, end_date))
    approved_leaves = cur.fetchall()

    # ---- 4. Pending approvals count (for the sidebar badge) -------------
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM leave_requests
        WHERE status NOT IN ('Approved', 'Rejected')
    """)
    pending_approvals_count = cur.fetchone()['cnt']

    cur.close()
    conn.close()

    # ---- Build first-punch-in / last-punch-out per employee per day -----
    def name_key(n):
        return n.strip().lower()

    daily = defaultdict(lambda: {"clock_in": None, "clock_out": None})
    for p in punches:
        key = (name_key(p["employee_name"]), p["timestamp"].date())
        t = p["timestamp"].time()
        if p["action_type"] == "Punch In":
            if daily[key]["clock_in"] is None or t < daily[key]["clock_in"]:
                daily[key]["clock_in"] = t
        elif p["action_type"] == "Punch Out":
            if daily[key]["clock_out"] is None or t > daily[key]["clock_out"]:
                daily[key]["clock_out"] = t

    leave_lookup = {}
    for l in approved_leaves:
        leave_lookup[(name_key(l["employee_name"]), l["leave_date"])] = l["reason"]

    # ---- Assemble one record per employee per day ------------------------
    attendance_records = []
    record_id = 1
    today = date.today()

    cur_date = start_date
    while cur_date <= end_date:
        for emp in employees:
            # Skip days before this employee was actually hired.
            join_date = emp.get("date_join")
            if isinstance(join_date, str):
                # MySQL returned it as text rather than a date object —
                # parse it (adjust the format string if yours differs).
                try:
                    join_date = datetime.strptime(join_date, "%Y-%m-%d").date()
                except ValueError:
                    join_date = None
            if join_date and cur_date < join_date:
                continue

            key = (name_key(emp["employee_name"]), cur_date)
            clock_in = daily[key]["clock_in"]
            clock_out = daily[key]["clock_out"]
            leave_reason = leave_lookup.get(key)

            if leave_reason is not None:
                status = "leave"
            elif clock_in is None:
                # Don't mark today/future as absent — the day isn't over yet.
                if cur_date >= today:
                    continue
                status = "absent"
            else:
                status = "late" if clock_in > LATE_CUTOFF else "present"

            attendance_records.append({
                "id": record_id,
                "employee_name": emp["employee_name"],
                "department": emp["tem_per"] or "—",   # no real dept column — using employment type
                "date": cur_date.isoformat(),
                "clock_in": clock_in.strftime("%H:%M") if clock_in else None,
                "clock_out": clock_out.strftime("%H:%M") if clock_out else None,
                "status": status,
                "location": "—",   # not tracked in this schema
                "notes": leave_reason if leave_reason else (
                    "No punch recorded." if status == "absent" else ""
                )
            })
            record_id += 1
        cur_date += timedelta(days=1)

    return render_template(
        "attendance_log.html",
        attendance_records=attendance_records,
        pending_approvals_count=pending_approvals_count
    )

@app.route('/manager/approvals', methods=['GET'])
def manager_approvals():
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    import pymysql
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Zia@2008',  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database='absent_db',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, employee_name, leave_date, reason ,exceeds_limit FROM leave_requests "
                "WHERE status = 'Pending' ORDER BY leave_date"
            )
            pending_requests = cursor.fetchall()
    except Exception as e:
        print(f"Database Error: {e}")
        pending_requests = []
    finally:
        connection.close()

    return render_template('approvals.html', pending_requests=pending_requests)


@app.route('/manager/approvals/<int:request_id>/<action>', methods=['POST'])
def manager_approval_action(request_id, action):
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    new_status = 'Approved' if action == 'approve' else 'Rejected'

    import pymysql
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Zia@2008',  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database='absent_db',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE leave_requests SET status = %s WHERE id = %s",
                (new_status, request_id)
            )
        connection.commit()
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        connection.close()

    return redirect(url_for('manager_approvals'))


@app.route('/manager/employee_directory', methods=['GET'])
def employee_directory():
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    import pymysql
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Zia@2008',  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database='absent_db',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT emp_code, employee_name, phone_number, email_id, gender, "
                "date_join, tem_per FROM employee_absences "
                "WHERE role = 'employee' ORDER BY employee_name"
            )
            employees = cursor.fetchall()
    except Exception as e:
        print(f"Database Error: {e}")
        employees = []
    finally:
        connection.close()

    return render_template('employee_directory.html', employees=employees)


# Add these routes to app.py
import pymysql


@app.route('/manager/settings', methods=['GET'])
def manager_settings():
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Zia@2008',  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database='absent_db',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # NOTE: this grabs the first manager-role row. If you have more
            # than one manager account, this needs to match the logged-in
            # user specifically (e.g. WHERE employee_name = session['username']).
            cursor.execute("SELECT employee_name FROM employee_absences WHERE role = 'manager' LIMIT 1")
            manager = cursor.fetchone()

            cursor.execute("SELECT late_cutoff_time FROM settings WHERE id = 1")
            settings_row = cursor.fetchone()
    except Exception as e:
        print(f"Database Error: {e}")
        manager = {'employee_name': ''}
        settings_row = {'late_cutoff_time': '09:30:00'}
    finally:
        connection.close()

    return render_template(
        'manager_settings.html',
        manager_name=manager['employee_name'] if manager else '',
        late_cutoff_time=str(settings_row['late_cutoff_time']) if settings_row else '09:30:00'
    )


@app.route('/manager/settings/profile', methods=['POST'])
def manager_settings_profile():
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    new_name = request.form.get('display_name')
    new_password = request.form.get('new_password')

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Zia@2008',  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database='absent_db',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            if new_password:
                cursor.execute(
                    "UPDATE employee_absences SET employee_name = %s, password = %s WHERE role = 'manager'",
                    (new_name, new_password)
                )
            else:
                cursor.execute(
                    "UPDATE employee_absences SET employee_name = %s WHERE role = 'manager'",
                    (new_name,)
                )
        connection.commit()
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        connection.close()

    return redirect(url_for('manager_settings'))


@app.route('/manager/settings/attendance', methods=['POST'])
def manager_settings_attendance():
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    new_cutoff = request.form.get('late_cutoff_time')  # e.g. "09:30"

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Zia@2008',  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database='absent_db',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE settings SET late_cutoff_time = %s WHERE id = 1",
                (new_cutoff,)
            )
        connection.commit()
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        connection.close()

    return redirect(url_for('manager_settings'))
# =====================================================================
# TASKS FEATURE — corrected to match your actual app.py patterns
# =====================================================================
# Fixed from the last version:
#   - Auth check now matches manager_dashboard exactly (session['user_role'])
#   - DB access uses pymysql + DictCursor, same as manager_dashboard
#   - Employee names pulled from employee_absences WHERE role='employee'
#
# Fill in your actual password on the `password="..."` line in each
# route below (same one from your manager_dashboard connection block).
# =====================================================================

from flask import render_template, request, redirect, url_for, session
from datetime import date
import pymysql

# ---- Dashboard / list page -----------------------------------------
@app.route('/manager/tasks')
def manager_tasks():
    # 1. Security Check
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    filter_value = request.args.get('filter', 'all')

    # 2. Database Connection Initialization
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Zia@2008",  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database="absent_db",
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            all_tasks = cursor.fetchall()

            today = date.today()
            for task in all_tasks:
                task['is_overdue'] = bool(
                    task.get('due_date') and task['status'] != 'completed'
                    and task['due_date'] < today
                )

            if filter_value == 'pending':
                tasks = [t for t in all_tasks if t['status'] != 'completed' and not t['is_overdue']]
            elif filter_value == 'completed':
                tasks = [t for t in all_tasks if t['status'] == 'completed']
            elif filter_value == 'overdue':
                tasks = [t for t in all_tasks if t['is_overdue']]
            else:
                tasks = all_tasks

            total_tasks = len(all_tasks)
            pending_tasks_count = sum(1 for t in all_tasks if t['status'] != 'completed' and not t['is_overdue'])
            completed_tasks_count = sum(1 for t in all_tasks if t['status'] == 'completed')
            overdue_tasks_count = sum(1 for t in all_tasks if t['is_overdue'])

            # Employees for the "Assign To" dropdown
            cursor.execute("SELECT employee_name AS name FROM employee_absences WHERE role='employee'")
            employees = cursor.fetchall()

            # So the sidebar badge on the Approvals link still works on this page too
            cursor.execute("SELECT COUNT(*) AS count FROM leave_requests WHERE status='Pending'")
            pending_approvals_count = cursor.fetchone()['count']

    finally:
        connection.close()

    return render_template(
        'tasks.html',
        tasks=tasks,
        employees=employees,
        total_tasks=total_tasks,
        pending_tasks_count=pending_tasks_count,
        completed_tasks_count=completed_tasks_count,
        overdue_tasks_count=overdue_tasks_count,
        current_filter=filter_value,
        pending_approvals_count=pending_approvals_count,
    )


# ---- Create a task ---------------------------------------------------
@app.route('/manager/tasks/create', methods=['POST'])
def create_task():
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    title = request.form.get('title')
    assigned_to = request.form.get('assigned_to')
    due_date = request.form.get('due_date') or None
    description = request.form.get('description')
    assigned_by = session.get('username', 'Manager')  # adjust if your session key is named differently

    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Zia@2008",  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database="absent_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO tasks
                   (title, description, assigned_to, assigned_by, status, due_date)
                   VALUES (%s, %s, %s, %s, 'pending', %s)""",
                (title, description, assigned_to, assigned_by, due_date)
            )
        connection.commit()
    finally:
        connection.close()

    return redirect(url_for('manager_tasks'))


# ---- Mark a task complete --------------------------------------------
@app.route('/manager/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Zia@2008",  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database="absent_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = %s", (task_id,))
        connection.commit()
    finally:
        connection.close()

    return redirect(url_for('manager_tasks'))


# ---- Delete a task ----------------------------------------------------
@app.route('/manager/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    if 'user_role' not in session or session['user_role'] != 'manager':
        return "<h3>Access Denied!</h3>", 403

    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Zia@2008",  # <-- PUT YOUR LOCAL MYSQL PASSWORD HERE
        database="absent_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        connection.commit()
    finally:
        connection.close()

    return redirect(url_for('manager_tasks'))
            
if __name__ == '__main__':
    app.run(debug=True, port=5001)




