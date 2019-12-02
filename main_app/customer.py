from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required

from main_app.database import get_db

customer_bp = Blueprint("customer", __name__, url_prefix="/cust")


@customer_bp.route('/customer_page', methods=('POST', 'GET'))
@login_required
def search():
    if request.method == "POST":
        time = request.args["time"]
        start_time = time + " " + "00:00:00"
        end_time = time + " " + "23:59:59"
        departure_city = request.args["departure_city"]
        departure_airport = request.args["departure_airport"]
        destination_city = request.args["destination_city"]
        destination_airport = request.args["destination_airport"]
        db = get_db()
        target_flights = db.execute("SELECT * FROM Flight "
                                    "JOIN (SELECT airport_name, city as departure_city FROM Airport) A on Flight.depart_airport = A.airport_name "
                                    "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON Flight.arrive_airport=A2.airport_name "
                                    "WHERE (depart_date_time BETWEEN ? AND ?) AND depart_airport=? AND arrive_airport=? AND departure_city=? AND arrive_city=?",
                                    (start_time, end_time, departure_airport, destination_airport, departure_city,
                                     destination_city)).fetchall()
        for f in target_flights:
            print("here")
            print(f["flight_number"])
        return render_template('/customer/customer_page.html', flights=target_flights)


@customer_bp.route('/customer_page', methods=('POST', 'GET'))
@login_required
def purchase():
    if request.method == 'POST':
        db = get_db()
        target_flights = db.execute("SELECT * FROM Flight "
                                    "JOIN (SELECT airport_name, city as departure_city FROM Airport) A on Flight.depart_airport = A.airport_name "
                                    "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON Flight.arrive_airport=A2.airport_name "
                                    "WHERE depart_date_time=? AND depart_airport=? AND arrive_airport=? AND departure_city=? AND arrive_city=?",
                                    (time, departure_airport, destination_airport, departure_city, destination_city))

    return render_template('/cust/customer_page', flights=None)

