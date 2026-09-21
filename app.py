from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.String(50))
    location = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    description = db.Column(db.String(200))

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer)
    student_name = db.Column(db.String(100))
    email = db.Column(db.String(100))

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    q = request.args.get('search')
    events = Event.query.filter(Event.name.contains(q)).all() if q else Event.query.all()
    return render_template("index.html", events=events, total_events=Event.query.count(), total_regs=Registration.query.count())

@app.route("/add_event", methods=["POST"])
def add_event():
    e = Event(name=request.form["name"], date=request.form["date"], location=request.form["location"], capacity=request.form["capacity"], description=request.form["description"])
    db.session.add(e); db.session.commit(); return redirect("/")

@app.route("/delete/<int:id>")
def delete_event(id):
    db.session.delete(Event.query.get(id)); db.session.commit(); return redirect("/")

@app.route("/register/<int:event_id>", methods=["POST"])
def register(event_id):
    r = Registration(event_id=event_id, student_name=request.form["student_name"], email=request.form["email"])
    db.session.add(r); db.session.commit(); return redirect("/")

@app.route("/admin")
def admin():
    return render_template("admin.html", events=Event.query.all(), regs=Registration.query.all())

if __name__ == "__main__":
    app.run(debug=True)