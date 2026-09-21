from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "premium2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.String(50))
    location = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))
    price = db.Column(db.String(20), default="Free")

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer)
    student_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    ticket_id = db.Column(db.String(20))

with app.app_context():
    db.create_all()
    if Event.query.count() == 0:
        sample = [
            Event(name="TECH FEST 2026", date="2026-10-15", location="Main Auditorium", capacity=500, description="Biggest tech fest with hackathon and AI workshop", category="Tech", price="₹299"),
            Event(name="CULTURAL NIGHT", date="2026-11-20", location="Open Theatre", capacity=1000, description="Dance, music and drama performances", category="Cultural", price="Free"),
            Event(name="STARTUP MEETUP", date="2026-09-30", location="Seminar Hall 1", capacity=150, description="Meet investors and founders", category="Workshop", price="₹199"),
            Event(name="SPORTS CHAMPIONSHIP", date="2026-10-05", location="College Ground", capacity=800, description="Cricket, football and athletics", category="Sports", price="Free"),
            Event(name="AI WORKSHOP", date="2026-10-10", location="Lab 301", capacity=60, description="Learn Python, ML and build projects", category="Tech", price="₹499"),
            Event(name="MUSIC FEST", date="2026-11-02", location="Auditorium", capacity=400, description="Live band and DJ night", category="Cultural", price="₹149"),
        ]
        db.session.add_all(sample); db.session.commit()

@app.route("/")
def home():
    q = request.args.get('search','')
    cat = request.args.get('category','All')
    events = Event.query
    if q: events = events.filter(Event.name.contains(q))
    if cat != 'All': events = events.filter_by(category=cat)
    events = events.all()
    return render_template("index.html", events=events, total_events=Event.query.count(), total_regs=Registration.query.count())

@app.route("/add_event", methods=["POST"])
def add_event():
    if "admin" not in session: return redirect("/login")
    e = Event(name=request.form["name"], date=request.form["date"], location=request.form["location"], capacity=request.form["capacity"], description=request.form["description"], category=request.form["category"], price=request.form["price"])
    db.session.add(e); db.session.commit(); return redirect("/")

@app.route("/delete/<int:id>")
def delete_event(id):
    if "admin" not in session: return redirect("/login")
    Event.query.filter_by(id=id).delete(); db.session.commit(); return redirect("/")

@app.route("/register/<int:event_id>", methods=["POST"])
def register(event_id):
    import random; ticket = f"EVT{random.randint(1000,9999)}"
    r = Registration(event_id=event_id, student_name=request.form["student_name"], email=request.form["email"], ticket_id=ticket)
    db.session.add(r); db.session.commit()
    return render_template("ticket.html", reg=r, event=Event.query.get(event_id))

@app.route("/admin")
def admin():
    if "admin" not in session: return redirect("/login")
    return render_template("admin.html", events=Event.query.all(), regs=Registration.query.all())

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form["username"]=="admin" and request.form["password"]=="admin123":
            session["admin"]=True; return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect("/")

if __name__ == "__main__": app.run(debug=True)