from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mysqldb import MySQL
from datetime import datetime
import os

app = Flask(__name__)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

# Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    task_id = request.args.get('edit')
    task_data = None
    if task_id:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = %s", [task_id])
        task_data = cur.fetchone()
        cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    cur.close()

    return render_template('index.html', task=task_data, tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form['description']
    start_date = request.form['start_date']
    start_time = request.form['start_time']
    end_date = request.form['end_date']
    end_time = request.form['end_time']
    task_id = request.form.get('task_id')

    # Validate date and time
    try:
        start_dt = datetime.strptime(start_date + ' ' + start_time, '%Y-%m-%d %H:%M')
        end_dt = datetime.strptime(end_date + ' ' + end_time, '%Y-%m-%d %H:%M')
        if end_dt < start_dt:
            flash("End date/time cannot be earlier than start date/time.")
            return redirect('/')
    except Exception as e:
        flash("Invalid date/time input.")
        return redirect('/')

    cur = mysql.connection.cursor()
    if task_id:
        cur.execute("""
            UPDATE tasks SET title=%s, description=%s, start_date=%s, start_time=%s, end_date=%s, end_time=%s
            WHERE id=%s
        """, (title, description, start_date, start_time, end_date, end_time, task_id))
    else:
        cur.execute("""
            INSERT INTO tasks (title, description, start_date, start_time, end_date, end_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, description, start_date, start_time, end_date, end_time))
    mysql.connection.commit()
    cur.close()
    return redirect('/') # Redirect back to the main page to see the updated list

@app.route('/delete/<int:task_id>')
def delete(task_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", [task_id])
    mysql.connection.commit()
    cur.close()
    return redirect('/') # Redirect back to the main page

@app.route('/toggle/<int:task_id>')
def toggle(task_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT completed FROM tasks WHERE id = %s", [task_id])
    current = cur.fetchone()
    if current is not None:
        new_status = not current[0]
        cur.execute("UPDATE tasks SET completed = %s WHERE id = %s", (new_status, task_id))
        mysql.connection.commit()
    cur.close()
    return redirect('/') # Redirect back to the main page

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
