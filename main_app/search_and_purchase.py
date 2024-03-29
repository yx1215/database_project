from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required

from main_app.database import get_db

import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

search_bp = Blueprint("search_purchase", __name__, url_prefix="/search_purchase")


@search_bp.route('/search', methods=('POST', 'GET'))
def search():
    return render_template('./auth/search_for_flights.html')


@search_bp.route('/show_result', methods=('POST', ))
def show_result():
    if request.method == "POST":
        search_type = request.args["search_type"]
        time = request.args["departure_date"]
        departure_date = request.args["departure_date"] + "%"
        arrive_date = request.args["arrive_date"] + "%"
        cur = str(datetime.now())
        db = get_db()
        if not time:
            from_day = datetime.now()
            to_day = str(datetime.now() + relativedelta(days=+7))

        else:
            time = datetime.strptime(time, '%Y-%m-%d')
            to_day = str(time + relativedelta(days=+7))
            from_day = str(time)
        from_day = str(from_day)
        if search_type == "one_way":
            departure_city = request.args["departure_city"] + "%"
            departure_airport = request.args["departure_airport"] + "%"
            destination_city = request.args["destination_city"] + "%"
            destination_airport = request.args["destination_airport"] + "%"

            target_flights = db.execute("SELECT * FROM Flight "
                                        "JOIN (SELECT airport_name, city as departure_city FROM Airport) A on"
                                        " Flight.depart_airport = A.airport_name "
                                        "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON"
                                        " Flight.arrive_airport=A2.airport_name "
                                        "WHERE (depart_date_time LIKE ?) AND depart_airport LIKE ? "
                                        "AND arrive_airport LIKE ? AND departure_city LIKE ? AND arrive_city LIKE ?",
                                        "AND depart_date_time>=?",
                                        (departure_date, departure_airport, destination_airport, departure_city,
                                         destination_city, cur)).fetchall()
            cheap_flight = db.execute("SELECT * FROM Flight "
                                      "JOIN (SELECT airport_name, city as departure_city FROM Airport) A on "
                                      "Flight.depart_airport = A.airport_name "
                                      "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON "
                                      "Flight.arrive_airport=A2.airport_name "
                                      "WHERE depart_date_time between ? and ?"
                                      "AND arrive_airport LIKE ? AND departure_city LIKE ? AND arrive_city LIKE ?"
                                      "AND base_price = (select min(base_price) from Flight JOIN "
                                      "(SELECT airport_name, city as departure_city FROM Airport) A on "
                                      "Flight.depart_airport = A.airport_name "
                                      "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON "
                                      "Flight.arrive_airport=A2.airport_name "
                                      "group by flight_number, A.airport_name, A.departure_city)",
                                      (from_day, to_day, destination_airport, departure_city, destination_city)).fetchall()
            print(not target_flights)
            return render_template('./auth/search_result_one_way.html',
                                   flights=target_flights, cheap_flight=cheap_flight)

        elif search_type == "two_way":
            print("two_way")
            departure_city = request.args["departure_city"] + "%"
            departure_airport = request.args["departure_airport"] + "%"
            destination_city = request.args["destination_city"] + "%"
            destination_airport = request.args["destination_airport"] + "%"

            departure_flights = db.execute("SELECT * FROM Flight "
                                        "JOIN (SELECT airport_name, city as departure_city FROM Airport) A on Flight.depart_airport = A.airport_name "
                                        "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON Flight.arrive_airport=A2.airport_name "
                                        "WHERE (depart_date_time LIKE ?) AND depart_airport LIKE ? "
                                           "AND arrive_airport LIKE ? AND departure_city LIKE ? AND arrive_city LIKE ?"
                                           "AND depart_date_time>=?",
                                        (departure_date, departure_airport,
                                         destination_airport, departure_city, destination_city, cur)).fetchall()
            arrive_flights = db.execute("SELECT * FROM Flight "
                                        "JOIN (SELECT airport_name, city as departure_city FROM Airport) A on Flight.depart_airport = A.airport_name "
                                        "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON Flight.arrive_airport=A2.airport_name "
                                        "WHERE (depart_date_time LIKE ?) AND depart_airport LIKE ? "
                                        "AND arrive_airport LIKE ? AND departure_city LIKE ? AND arrive_city LIKE ?"
                                        "AND depart_date_time>=?",
                                           (arrive_date, destination_airport,
                                            departure_airport, destination_city, departure_city, cur)).fetchall()
            return render_template('./auth/search_result_two_way.html', departure_flights=departure_flights, arrive_flights=arrive_flights)

        elif search_type == "by_airline":
            airline_name = request.args["airline_name"] + "%"
            flight_number = request.args["flight_number"] + "%"
            target_flights = db.execute("SELECT * FROM Flight "
                                        "JOIN (SELECT airport_name, city as departure_city FROM Airport) A on Flight.depart_airport = A.airport_name "
                                        "JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON Flight.arrive_airport=A2.airport_name "
                                        "WHERE depart_date_time LIKE ? AND arrive_date_time LIKE ? AND airline_name LIKE ? AND flight_number LIKE ?",
                                        (departure_date, arrive_date, airline_name, flight_number)).fetchall()
            return render_template("./auth/search_result_by_airline.html", flights=target_flights)


@search_bp.route('/purchase', methods=('POST', 'GET'))
@login_required
def purchase():
    flight_number = request.args["flight_number"]
    airline_name = request.args["airline_name"]
    depart_date_time = request.args["depart_date_time"]
    db = get_db()
    selected_flight = db.execute(
        'SELECT * FROM Flight JOIN Airplane A on Flight.airline_name = A.airline_name and Flight.plane_id = A.plane_id'
        ' WHERE flight_number=? AND A.airline_name=? AND depart_date_time=?',
        (flight_number, airline_name, depart_date_time)).fetchone()
    sold_seats = db.execute(
        'SELECT count(*) AS C FROM Ticket WHERE airline_name=? AND flight_number=? AND depart_date_time=?',
        (selected_flight['airline_name'], selected_flight['flight_number'],
         selected_flight['depart_date_time'])).fetchone()
    print(sold_seats["C"])
    percent = sold_seats['C'] / selected_flight['seat_amount']
    error = None
    if percent < 0.7:
        price = selected_flight["base_price"]
    elif 0.7 <= percent < 1:
        price = selected_flight["base_price"] * 1.2
    else:
        error = "No enough space, please choose another flight."
    if error is not None:
        flash(error)
        return redirect(url_for('search_purchase.search'))
    if request.method == 'GET':

        return render_template('./auth/purchase_interface.html', selected_flight=selected_flight, price=price)

    if request.method == "POST":
        error = None
        card_type = request.form["card_type"]
        card_number = request.form["card_number"]
        name_on_card = request.form["name_on_card"]
        expire_date = request.form["expire_date"]
        ticket_id = random.randint(1, 1e7)
        cust_email = g.user["cust_email"] if g.type == "customer" else request.form["cust_email"]
        if not db.execute("SELECT * FROM Customer WHERE cust_email=?", (cust_email, )).fetchone():
            error = "Customer does not exist."
        if error:
            print("error:", error)
            flash(error)
            return render_template('./auth/purchase_interface.html', selected_flight=selected_flight, price=price)
        if g.type != "booking_agent":
            booking_agent = None
        else:
            booking_agent = g.user["agent_email"]
        db.execute('INSERT INTO Ticket (ticket_id, airline_name, flight_number, depart_date_time, arrive_date_time) VALUES '
                   '(?, ?, ?, ?, ?)', (ticket_id, airline_name, flight_number, depart_date_time, selected_flight['arrive_date_time']))
        db.execute('INSERT INTO Purchase (ticket_id, cust_email, booking_agent, sold_price, card_type, card_number, name_on_card, expire_date) VALUES '
                   '(?, ?, ?, ?, ?, ?, ?, ?)',
                   (ticket_id, cust_email, booking_agent, price, card_type, card_number, name_on_card, expire_date))
        db.commit()
        print("here")
        return redirect(url_for('search_purchase.search'))
