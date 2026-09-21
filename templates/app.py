from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "eventify-secret-key"

DATABASE = "events.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            event_id INTEGER NOT NULL
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    if count == 0:
        events = [
            (
                "Grand Music Festival",
                "2026-09-25",
                "6:00 PM",
                "College Auditorium",
                "A live music festival featuring talented performers."
            ),
            (
                "Tech Innovation Summit",
                "2026-10-05",
                "10:00 AM",
                "Bangalore Convention Centre",
                "Explore technology, innovation and artificial intelligence."
            ),
            (
                "AI & Machine Learning Workshop",
                "2026-10-15",
                "9:00 AM",
                "Computer Lab",
                "Learn the basics of Artificial Intelligence and Machine Learning."
            )
        ]

        conn.executemany("""
            INSERT INTO events
            (name, date, time, location, description)
            VALUES (?, ?, ?, ?, ?)
        """, events)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()

    events = conn.execute("""
        SELECT * FROM events
        ORDER BY date
        LIMIT 3
    """).fetchall()

    registration_count = conn.execute(
        "SELECT COUNT(*) FROM registrations"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        events=events,
        registration_count=registration_count
    )


@app.route("/events")
def events():
    conn = get_db()

    events = conn.execute("""
        SELECT * FROM events
        ORDER BY date
    """).fetchall()

    conn.close()

    return render_template(
        "events.html",
        events=events
    )


@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):

    conn = get_db()

    event = conn.execute(
        "SELECT * FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()

    if not event:
        conn.close()
        return "Event not found", 404

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        conn.execute("""
            INSERT INTO registrations
            (name, email, phone, event_id)
            VALUES (?, ?, ?, ?)
        """, (name, email, phone, event_id))

        conn.commit()
        conn.close()

        flash("Registration successful!")
        return redirect(url_for("success"))

    conn.close()

    return render_template(
        "register.html",
        event=event
    )


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/admin")
def admin():

    conn = get_db()

    registrations = conn.execute("""
        SELECT
            registrations.id,
            registrations.name,
            registrations.email,
            registrations.phone,
            events.name AS event_name
        FROM registrations
        JOIN events
        ON registrations.event_id = events.id
        ORDER BY registrations.id DESC
    """).fetchall()

    event_count = conn.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    registration_count = conn.execute(
        "SELECT COUNT(*) FROM registrations"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        registrations=registrations,
        event_count=event_count,
        registration_count=registration_count
    )


@app.route("/admin/add-event", methods=["GET", "POST"])
def add_event():

    if request.method == "POST":

        name = request.form["name"]
        date = request.form["date"]
        time = request.form["time"]
        location = request.form["location"]
        description = request.form["description"]

        conn = get_db()

        conn.execute("""
            INSERT INTO events
            (name, date, time, location, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            date,
            time,
            location,
            description
        ))

        conn.commit()
        conn.close()

        flash("Event added successfully!")

        return redirect(url_for("events"))

    return render_template("add_event.html")


@app.route("/admin/delete-registration/<int:registration_id>")
def delete_registration(registration_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM registrations WHERE id = ?",
        (registration_id,)
    )

    conn.commit()
    conn.close()

    flash("Registration deleted successfully!")

    return redirect(url_for("admin"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)