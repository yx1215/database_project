from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required_customer

from main_app.database import get_db

from dateutil.relativedelta import relativedelta
from datetime import datetime

customer_bp = Blueprint("customer", __name__, url_prefix="/cust")


@customer_bp.route('/customer_page', methods=('POST', 'GET'))
@login_required_customer
def home():
    return render_template('./customer.html')


@customer_bp.route('/my_purchase', methods=('POST', 'GET'))
@login_required_customer
def my_purchase():
    from_date = request.args["from_date"]
    to_date = request.args["to_date"]
    depart_airport = request.args["depart_airport"] + "%"
    depart_city = request.args["depart_city"] + "%"
    arrive_airport = request.args["arrive_airport"] + "%"
    arrive_city = request.args["arrive_city"] + "%"
    db = get_db()
    if from_date == "":
        from_date = str(datetime.now())
    else:
        from_date = from_date + " 00:00:00"

    if to_date == "":
        to_date = '2100-01-01 00:00:00'
    else:
        to_date = to_date + " 23:59:59"
    print(from_date, to_date)
    my_ticket = db.execute('SELECT * FROM Purchase NATURAL JOIN Ticket NATURAL JOIN Flight '
               'JOIN (SELECT airport_name, city as depart_city FROM Airport) A ON depart_airport=A.airport_name '
               'JOIN (SELECT airport_name, city as arrive_city FROM Airport) A2 ON arrive_airport=A2.airport_name '
               'WHERE cust_email=? AND depart_airport LIKE ? AND depart_city LIKE ? AND arrive_airport LIKE ? AND arrive_city LIKE ?'
               'AND depart_date_time BETWEEN ? AND ?',
               (g.user['cust_email'], depart_airport, depart_city, arrive_airport, arrive_city, from_date, to_date))
    return render_template('view_purchased_ticket.html', my_purchase=my_ticket)


@customer_bp.route('/track_my_spending', methods=('GET', 'POST'))
@login_required_customer
def track_my_spending():
    from_date = request.args["from_date"]
    to_date = request.args["to_date"]
    if from_date == "" or to_date == "":
        from_date = str(datetime.now() - relativedelta(years=1))
        to_date = str(datetime.now())
    else:
        from_date = from_date + " 00:00:00"
        to_date = to_date + " 23:59:59"
    from_year = int(from_date[:4])
    from_month = int(from_date[5:7])
    to_year = int(to_date[:4])
    to_month = int(to_date[5:7])
    db = get_db()
    selected = db.execute("SELECT strftime('%Y', purchase_date_time) AS year, strftime('%m', purchase_date_time) AS month, SUM(P.sold_price) AS cost "
                          "FROM (SELECT * FROM Purchase WHERE purchase_date_time BETWEEN ? AND ?) as P "
                          "GROUP BY strftime('%Y', P.purchase_date_time), strftime('%m', P.purchase_date_time)",
                          (from_date, to_date))
    exist_cost = {}
    for r in selected:
        exist_cost[(int(r["year"]), int(r["month"]))] = int(r["cost"])
    spending = []
    index = 1
    for i in range(from_year, to_year + 1):

        if i == from_year:
            start = from_month
        else:
            start = 1
        if i == to_year:
            end = to_month
        else:
            end = 12

        for j in range(start, end + 1):
            d = {}
            print(i, j)
            d["year"] = i
            d["month"] = j
            if (i, j) in exist_cost.keys():
                d["cost"] = exist_cost[(i, j)]
            else:
                d["cost"] = 0
            d["index"] = index
            index += 1
            spending.append(d)
    print(spending)
    return render_template('view_my_spending.html', spending=spending)


@customer_bp.route('/choose_flight_to_comment', methods=('GET', 'POST'))
def choose_flight_to_comment():
    current_time = str(datetime.now())
    db = get_db()
    past_flights = db.execute("SELECT * FROM Flight WHERE depart_date_time<?", (current_time, ))
    return render_template('view_my_past_flights.html', past_flights=past_flights)


@customer_bp.route('/make_comments', methods=('GET', 'POST'))
def make_comments():
    airline_name = request.args["airline_name"]
    flight_number = request.args["flight_number"]
    depart_date_time = request.args["depart_date_time"]
    cust_email = g.user["cust_email"]
    db = get_db()
    selected_flight = db.execute("SELECT * FROM Flight "
                                 "WHERE airline_name=? AND flight_number=? AND depart_date_time=?",
                                 (airline_name, flight_number, depart_date_time)).fetchone()
    if "comments" not in request.args.keys():
        error = None
        if db.execute("SELECT * FROM Comments WHERE airline_name=? AND flight_number=?"
                      "AND depart_date_time=? AND cust_email=?",
                      (airline_name, flight_number, depart_date_time, cust_email)).fetchone():
            error = "You can only comment a flight once."
        if error is not None:
            flash(error)
            return redirect(url_for('customer.choose_flight_to_comment'))

        return render_template('make_comments.html', selected_flight=selected_flight)
    else:
        comments = request.args["comments"]
        rating = request.args["rating"]
        db.execute("INSERT INTO Comments (airline_name, flight_number, depart_date_time, cust_email, comment, rating) VALUES "
                   "(?, ?, ?, ?, ?, ?)",
                   (airline_name, flight_number, depart_date_time, cust_email, comments, rating))
        db.commit()
        print("here")
        return redirect(url_for('customer.home'))
