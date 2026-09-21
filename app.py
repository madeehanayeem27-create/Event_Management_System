from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os, uuid, qrcode

app = Flask(__name__)
app.secret_key = 'final_year_major_project'

def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, name TEXT, date TEXT, location TEXT, capacity TEXT, price TEXT, category TEXT, description TEXT, image TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS regs
                 (id INTEGER PRIMARY KEY, event_id INTEGER, name TEXT, email TEXT, ticket_id TEXT)''')
    conn.commit()
    conn.close()
init_db()
@app.route('/')
def home():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT * FROM events ORDER BY id DESC')
    events = c.fetchall()
    c.execute('SELECT COUNT(*) FROM regs')
    total = c.fetchone()[0]
    conn.close()
    return render_template('index.html', events=events, count=total)

@app.route('/register', methods=['POST'])
def register():
    event_id = request.form['event_id']
    name = request.form['name']
    email = request.form['email']
    ticket_id = str(uuid.uuid4())[:8].upper()

    # QR Code Generate
    if not os.path.exists('static/qr'): os.makedirs('static/qr')
    qr_data = f"TicketID:{ticket_id} | Event:{event_id} | User:{email}"
    img = qrcode.make(qr_data)
    img.save(f'static/qr/{ticket_id}.png')

    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('INSERT INTO regs (event_id, name, email, ticket_id) VALUES (?,?,?,?)', (event_id, name, email, ticket_id))
    conn.commit()
    conn.close()
    return render_template('ticket.html', ticket_id=ticket_id, name=name, email=email)

@app.route('/ticket/<ticket_id>')
def ticket(ticket_id):
    return render_template('ticket.html', ticket_id=ticket_id)

# ADMIN
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect('/admin')
    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if 'admin' not in session: return redirect('/admin-login')
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT * FROM events ORDER BY id DESC')
    events = c.fetchall()
    c.execute('SELECT regs.*, events.name as ename FROM regs LEFT JOIN events ON regs.event_id = events.id ORDER BY regs.id DESC')
    regs = c.fetchall()
    c.execute('SELECT COUNT(*) FROM regs')
    total = c.fetchone()[0]
    conn.close()
    return render_template('admin.html', events=events, regs=regs, total=total)

@app.route('/add-event', methods=['POST'])
def add_event():
    if 'admin' not in session: return redirect('/admin-login')
    data = (request.form['name'], request.form['date'], request.form['location'], request.form['capacity'], request.form['price'], request.form['category'], request.form['description'], request.form['image'])
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('INSERT INTO events (name, date, location, capacity, price, category, description, image) VALUES (?,?,?,?,?,?,?,?)', data)
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/delete/<int:id>')
def delete(id):
    if 'admin' not in session: return redirect('/admin-login')
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('DELETE FROM events WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)