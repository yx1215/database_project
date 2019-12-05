from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required_airline_staff

from main_app.database import get_db

import random
from datetime import datetime


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
    print(request.form)
    airline_name = request.form['airline_name']
    flight_number = request.form['flight_number']
    delay_status = request.form['delay_status']
    time = request.form['depart_date_time'].split("T")
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







