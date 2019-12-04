from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required_customer

from main_app.database import get_db

import random
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
