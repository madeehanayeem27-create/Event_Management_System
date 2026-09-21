import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = 'event-management-secret-12345' # Ye line bahut zaruri hai

DATABASE = 'events.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS events 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, location TEXT, description TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS registrations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER, name TEXT, email TEXT)''')
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    init_db()
    db = get_db()
    events = db.execute('SELECT * FROM events ORDER BY id DESC').fetchall()
    return render_template('index.html', events=events)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    init_db()
    if request.method == 'POST':
        # Tumhara Admin Password
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Wrong Password! Try admin / admin123"
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    db = get_db()
    events = db.execute('SELECT * FROM events ORDER BY id DESC').fetchall()
    return render_template('admin.html', events=events)

@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        db = get_db()
        db.execute('INSERT INTO events (name, date, location, description) VALUES (?, ?, ?, ?)',
                   (request.form['name'], request.form['date'], request.form['location'], request.form['description']))
        db.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_event.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)