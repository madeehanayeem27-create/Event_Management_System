from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.secret_key = "eventmanager-pro-2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.String(50))
    location = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    image = db.Column(db.String(500))

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

with app.app_context():
    try:
        db.create_all()
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'event' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('event')]
            if 'image' not in cols:
                db.drop_all()
                db.create_all()
    except:
        db.drop_all()
        db.create_all()

@app.route('/')
def home():
    events = Event.query.all()
    total_reg = Registration.query.count()
    is_admin = 'admin' in session
    return render_template('index.html', events=events, total_reg=total_reg, is_admin=is_admin)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin123':
            session['admin'] = True
            return redirect('/')
        else:
            return "Wrong password! admin / admin123 <a href='/admin-login'>Try again</a>"
    return '''
    <div style="max-width:400px;margin:80px auto;font-family:sans-serif;text-align:center;border:1px solid #ddd;padding:30px;border-radius:10px">
    <h2>Admin Login</h2>
    <form method="POST">
    <input name="username" value="admin" style="width:100%;padding:10px;margin:10px 0"><br>
    <input name="password" type="password" placeholder="admin123" style="width:100%;padding:10px;margin:10px 0"><br>
    <button style="width:100%;padding:12px;background:#6a11cb;color:white;border:none;border-radius:5px">Login</button>
    </form></div>
    '''

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

@app.route('/create', methods=['POST'])
def create_event():
    if 'admin' not in session:
        return redirect('/admin-login')
    try:
        price_text = request.form.get('price') or '0'
        price = 0
        if 'free' not in price_text.lower():
            nums = re.findall(r'\d+', price_text)
            if nums:
                price = int(nums[0])
        new_event = Event(
            name=request.form.get('name'),
            date=request.form.get('date'),
            location=request.form.get('location'),
            capacity=int(request.form.get('capacity') or 100),
            price=price,
            category=request.form.get('category') or 'Tech',
            description=request.form.get('description') or '',
            image=request.form.get('image') or 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4'
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"Error: {e}"

@app.route('/register/<int:event_id>', methods=['POST'])
def register(event_id):
    name = request.form.get('name')
    email = request.form.get('email')
    if name and email:
        reg = Registration(event_id=event_id, name=name, email=email)
        db.session.add(reg)
        db.session.commit()
    return redirect('/')

@app.route('/delete/<int:event_id>')
def delete(event_id):
    if 'admin' not in session:
        return redirect('/admin-login')
    Event.query.filter_by(id=event_id).delete()
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)