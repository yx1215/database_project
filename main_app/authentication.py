import functools
import random
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from main_app.database import get_db


SECRET_KEY = generate_password_hash('12345')
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        print(request.form)
        register_type = request.form["register_type"]
        db = get_db()
        error = None

        if register_type != 'booking_agent' and register_type != 'customer' and register_type != 'airline_staff':
            error = 'please choose a correct type of user to register.'
            flash(error)
            return render_template('/auth/register.html')

        password = request.form["password"]
        repeat_password = request.form["repeat_password"]

        if repeat_password != password:
            error = "two passwords are not the same."
            flash(error)
            return render_template('/auth/register.html')

        if register_type == "airline_staff":
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            email = request.form["email"]
            phone_number = request.form["phone_number"]
            date_of_birth = request.form["birthday"]
            airline_name = request.form["airline"]
            if not first_name:
                error = "first name is required."
            elif not last_name:

                error = "last name is required."
            elif not password:

                error = "password is required."
            elif not email:
                error = "email is required."
            elif not phone_number:
                error = "phone_number is required."

            elif db.execute('SELECT * FROM Airline_Staff WHERE username = ?', (email, )).fetchone() is not None:
                error = "Username {} has already registered.".format(email)

            elif db.execute('SELECT * FROM Airline WHERE airline_name = ?', (airline_name, )).fetchone() is None:
                error = "Airline {} does not exist.".format(airline_name)

            if error is None:
                db.execute('INSERT INTO Airline_Staff (username, password, first_name, last_name, date_of_birth, airline_name, phone_number) VALUES '
                           '(?, ?, ?, ?, ?, ?, ?)',
                           (email, generate_password_hash(password), first_name, last_name, date_of_birth, airline_name, phone_number)
                           )
                db.commit()
                return redirect(url_for("auth.login"))

            flash(error)

            # return render_template('auth/register.html')

        elif register_type == "customer":
            name = request.form["last_name"] + " " + request.form["first_name"]
            email = request.form["email"]
            building_name = request.form["building_name"]
            street = request.form["street"]
            city = request.form["city"]
            state = request.form["state"]
            phone_number = request.form["phone_number"]
            passport_number = request.form["passport_number"]
            passport_expiration = request.form["passport_expiration"]
            passport_country = request.form["passport_country"]
            date_of_birth = request.form["birthday"]

            if not name:
                error = "name is required."
            elif not passport_number:
                error = "passport number is required."
            elif not passport_expiration:
                error = "passport expiration is required."
            elif not password:
                error = "password is required."
            elif not passport_country:
                error = "passport country is required."
            elif not date_of_birth:
                error = "birthday is required."

            if error is None:
                db.execute('INSERT INTO Customer (cust_email, name, password, building_name, street, city, state, cust_phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUES '
                           '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           (email, name, generate_password_hash(password), building_name, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
                           )
                db.commit()

                return redirect(url_for('auth.login'))

            flash(error)

        elif register_type == "booking_agent":
            email = request.form["email"]
            booking_agent_id = random.randint(1, 10e10)
            if not email:
                error = 'email is required.'
            elif not booking_agent_id:
                error = 'booking_agent_id is required.'
            elif db.execute('SELECT * FROM Booking_Agent WHERE agent_email = ?', (email, )).fetchone() is not None:
                error = 'email {} already exists.'.format(email)

            if error is None:
                db.execute('INSERT INTO Booking_Agent (agent_email, password, booking_agent_id) VALUES '
                           '(?, ?, ?)',
                           (email, generate_password_hash(password), booking_agent_id)
                           )
                db.commit()

                return redirect(url_for('auth.login'))
            flash(error)

    return render_template('/auth/register.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        login_type = request.form['login_type']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if login_type == 'airline_staff':
            user = db.execute(
                'SELECT * FROM Airline_Staff WHERE username = ?', (email,)
            ).fetchone()
        elif login_type == 'booking_agent':
            user = db.execute(
                'SELECT * FROM Booking_Agent WHERE agent_email = ?', (email,)
            ).fetchone()
        elif login_type == 'customer':
            user = db.execute(
                'SELECT * FROM Customer WHERE cust_email = ?', (email,)
            ).fetchone()
        else:
            error = 'Unknown type of user.'
            flash(error)
            return render_template('/auth/login.html')

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['login_type'] = login_type
            if login_type == 'airline_staff':
                session['key'] = user['username']
                return render_template("user_interface.html")
            elif login_type == 'booking_agent':
                session['key'] = user['agent_email']
                return render_template("user_interface.html")
            elif login_type == 'customer':
                session['key'] = user['cust_email']
                return render_template("user_interface.html")

        flash(error)

    return render_template('/auth/login.html')


@auth_bp.route('/search_without_login', methods=('POST', 'GET'))
def search():
    if request.method == 'POST':
        time = request.args["time"].split("T")
        time = time[0] + " " + time[1] + ":00"
        departure_city = request.args["departure_city"]
        departure_airport = request.args["departure_airport"]
        destination_city = request.args["destination_city"]
        destination_airport = request.args["destination_airport"]
        db = get_db()
        target_flights = db.execute("SELECT * FROM Flight "
                                    "JOIN (SELECT airport_name, city as departure_city FROM Airport) A on Flight.depart_airport = A.airport_name "
                                    "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON Flight.arrive_airport=A2.airport_name "
                                    "WHERE depart_date_time=? AND depart_airport=? AND arrive_airport=? AND departure_city=? AND arrive_city=?",
                                    (time, departure_airport, destination_airport, departure_city, destination_city))
        return render_template('/auth/search_without_login.html', flights=target_flights)
    return render_template('/auth/search_without_login.html', flights=None)


@auth_bp.before_app_request
def load_logged_in_user():
    key = session.get('key')
    login_type = session.get('login_type')

    if key is None:
        g.user = None
        g.type = None
    else:
        if login_type == 'airline_staff':
            g.user = get_db().execute(
                'SELECT * FROM Airline_Staff WHERE username = ?', (key,)
            ).fetchone()
            g.type = 'airline_staff'
        elif login_type == 'booking_agent':
            g.user = get_db().execute(
                'SELECT * FROM Booking_Agent WHERE agent_email = ?', (key,)
            ).fetchone()
            g.type = 'booking_agent'
        else:
            g.user = get_db().execute(
                'SELECT * FROM Customer WHERE cust_email = ?', (key, )
            ).fetchone()
            g.type = 'customer'


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
