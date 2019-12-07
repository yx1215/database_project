from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required_airline_staff

from main_app.database import get_db

import random
from datetime import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta

staff_bp = Blueprint("airline_staff", __name__, url_prefix="/airline_staff")


@staff_bp.route('/staff_page', methods=('POST', 'GET'))
@login_required_airline_staff
def home():
    return render_template('airline_staff.html')


@staff_bp.route('/add_airplane', methods=('POST', 'GET'))
@login_required_airline_staff
def add_airplane():
    print("CALLED")
    print(list(request.args.keys()))
    print(list(request.args.values()))
    airline_name = request.args['airline_name']
    plane_id = request.args['plane_id']
    seat_amount = request.args['seat_amount']
    print(airline_name, plane_id, seat_amount)
    db = get_db()
    error = None
    message = None
    # result = db.execute("select * from Airplane")
    # print(result)
    if not plane_id:
        error = "Plane ID is required"
    elif not seat_amount:
        error = "Seat amount is required"
    elif db.execute('SELECT * FROM Airplane WHERE plane_id = ?', (plane_id, )).fetchone() is not None:
        error = "The plane has been added"
    else:
        message = "You have successfully added the airplane"
    if not error:
        db.execute("INSERT INTO Airplane(airline_name, plane_id, seat_amount) VALUES (?,?,?)", (airline_name, plane_id, seat_amount))
        db.commit()
    if error:
        flash(error, 'add_airplane')
    if message and not error:
        my_airplane = db.execute("select * from Airplane where airline_name=?", (airline_name,))
        return render_template('view_airplanes.html', my_airplane=my_airplane)

    return render_template('airline_staff.html')


@staff_bp.route('/update_status', methods=('POST', 'GET'))
@login_required_airline_staff
def update_status():
    print(dict(request.form))
    airline_name = request.form['airline_name_status']
    flight_number = request.form['flight_number_status']
    delay_status = request.form['delay_status']
    time = request.form['depart_date_time_status'].split("T")
    depart_date_time = time[0] + " " + time[1] + ":00"
    print(depart_date_time)
    db = get_db()
    if not flight_number:
        message = "Flight number is required"
    elif not delay_status:
        message = "Delay Status is required"
    elif not depart_date_time:
        message = "Departure time is required"
    elif db.execute('SELECT * FROM Flight WHERE airline_name=? and flight_number=? and depart_date_time=?',
                    (airline_name, flight_number, depart_date_time,)).fetchone() is None:
        message = "The flight is not found"
    elif db.execute('SELECT delay_status FROM Flight WHERE airline_name=? and flight_number=? and depart_date_time=?',
                    (airline_name, flight_number, depart_date_time,)).fetchone()[0] == delay_status:
        message = "Nothing is changed"
    else:
        message = "You have successfully changed the status"
        db.execute("UPDATE Flight SET delay_status=? where airline_name=? and flight_number=? and depart_date_time=?",
                   (delay_status, airline_name, flight_number, depart_date_time,))
        db.commit()

    flash('Update Status Result: ' + message)

    return render_template('airline_staff.html')


@staff_bp.route('/check_status', methods=('POST', 'GET'))
@login_required_airline_staff
def check_status():
    print(request.form)
    airline_name = request.form['airline_name']
    flight_number = request.form['flight_number']
    time = request.form['depart_date_time'].split("T")
    depart_date_time = time[0] + " " + time[1] + ":00"
    print(depart_date_time)
    db = get_db()
    status = None
    if not flight_number:
        message = "Flight number is required"
    elif not depart_date_time:
        message = "Departure time is required"
    elif db.execute('SELECT * FROM Flight WHERE airline_name=? and flight_number=? and depart_date_time=?',
                    (airline_name, flight_number, depart_date_time,)).fetchone() is None:
        message = "The flight is not found"
    else:
        message = "Successfully get the status"
    if message == "Successfully get the status":
        status = db.execute(
            'SELECT delay_status FROM Flight WHERE airline_name=? and flight_number=? and depart_date_time=?',
            (airline_name, flight_number, depart_date_time,)).fetchone()[0]
        print(status)

    flash('Check Status Result: ' + message)

    return render_template('airline_staff.html', value=status)


@staff_bp.route('/add_airport', methods=('POST', 'GET'))
@login_required_airline_staff
def add_airport():
    print("CALLED")
    airport_name = request.form['airport_name']
    city = request.form['city']
    db = get_db()
    if db.execute('SELECT * FROM Airport WHERE airport_name=? ', (airport_name,)).fetchone() is not None:
        error = "The airport exists"
    else:
        error = "You have successfully added the flight"
    if error == "You have successfully added the flight":
        db.execute("INSERT INTO "
                   "Airport(airport_name, city)"
                   "VALUES (?,?)",
                   (airport_name, city))
        db.commit()
    flash("Add Airport Status: " + error)
    return render_template('airline_staff.html')


@staff_bp.route('/view_flights', methods=('POST', 'GET'))
@login_required_airline_staff
def view_flights():
    print(list(request.args.keys()))
    from_date = request.args["from_date"]
    to_date = request.args["to_date"]
    depart_airport = request.args["depart_airport"] + "%"
    depart_city = request.args["depart_city"] + "%"
    arrive_airport = request.args["arrive_airport"] + "%"
    arrive_city = request.args["arrive_city"] + "%"
    airline_name = request.args['airline_name']

    db = get_db()
    if from_date == "" or to_date == "":
        from_date = str(datetime.now())
        to_date = str(datetime.now() + relativedelta(days=30))
        # return render_template('view_future_flights.html', my_flight=my_flight)
    if from_date > to_date:
        flash("Wrong dates")
    print(from_date, to_date)
    my_flight = db.execute("select * from Flight JOIN "
                           "(SELECT airport_name, city AS depart_city FROM Airport) A "
                           "ON depart_airport=A.airport_name "
                           "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 "
                           "ON arrive_airport=A2.airport_name where airline_name=? and depart_airport LIKE ? "
                           "AND depart_city LIKE ? AND arrive_airport LIKE ? AND arrive_city LIKE ? "
                           "AND depart_date_time between ? and  ?",
                           (airline_name, depart_airport, depart_city, arrive_airport, arrive_city, from_date, to_date))
    return render_template('view_future_flights.html', my_flight=my_flight)


@staff_bp.route('/add_flight', methods=('POST', 'GET'))
@login_required_airline_staff
def add_flight():
    print("CALLED")
    airline_name = request.form['airline_name_flight']
    plane_id = request.form['plane_id_flight']
    flight_number = request.form['flight_number_flight']
    d_time = request.form['depart_date_time_flight'].split("T")
    a_time = request.form['arrive_date_time_flight'].split("T")
    depart_date_time = d_time[0] + " " + d_time[1] + ":00"
    arrive_date_time = a_time[0] + " " + a_time[1] + ":00"
    depart_airport = request.form['departure_airport_flight']
    arrive_airport = request.form['arrive_airport_flight']
    base_price = request.form['base_price_flight']
    flight_status = request.form['flight_status_flight']
    delay_status = request.form['delay_status_flight']
    db = get_db()
    if not airline_name:
        error = "Airline name is required"
    elif not plane_id:
        error = "Plane ID is required"
    elif not flight_number:
        error = "Flight number is required"
    elif not d_time:
        error = "Departure time is required"
    elif not a_time:
        error = "Arrive time is required"
    elif not depart_airport:
        error = "Departure airport is required"
    elif not arrive_airport:
        error = "Arrive airport is required"
    elif not base_price:
        error = "Base price is required"
    elif not flight_status:
        error = "Flight status is required"
    elif not delay_status:
        error = "Delay status is required"
    elif db.execute('SELECT * FROM Flight WHERE flight_number=? and airline_name=? and depart_date_time=?',
                    (flight_number, airline_name, depart_date_time)).fetchone() is not None:
        error = "The flight exists"
    elif db.execute('select * from Airplane where airline_name=? and  plane_id=?',
                    (airline_name, plane_id)).fetchone() is None:
        error = "The airplane does not exist"
    elif db.execute('select * from Airport where airport_name=?', (depart_airport,)).fetchone() is not None:
        error = "The departure airport does not exist"
    elif db.execute('select * from Airport where airport_name=?', (arrive_airport,)).fetchone() is not None:
        error = "The arrive airport does not exist"
    else:
        error = "You have successfully added the flight"
    if error == "You have successfully added the flight":
        db.execute("INSERT INTO "
                   "Flight(plane_id, flight_number, airline_name, depart_date_time, arrive_date_time,"
                   " depart_airport, arrive_airport, base_price, flight_status, delay_status)"
                   "VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (plane_id, flight_number, airline_name, depart_date_time, arrive_date_time,
                    depart_airport, arrive_airport, base_price, flight_status, delay_status))
        db.commit()
        flash("Successfully added a flight")
    return render_template('airline_staff.html')






