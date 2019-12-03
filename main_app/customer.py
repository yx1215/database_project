from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required_customer

from main_app.database import get_db

import random

customer_bp = Blueprint("customer", __name__, url_prefix="/cust")


@customer_bp.route('/customer_page', methods=('POST', 'GET'))
@login_required_customer
def home():
    return render_template('/customer.html')


@customer_bp.route('/purchase', methods=('POST', 'GET'))
@login_required_customer
def purchase():
    if request.method == 'POST':
        flight_number = request.args["flight_number"]
        airline_name = request.args["airline_name"]
        depart_date_time = request.args["depart_date_time"]
        db = get_db()
        purchased_flight = db.execute('SELECT * FROM Flight WHERE flight_number=? AND airline_name=? AND depart_date_time=?',
                   (flight_number, airline_name, depart_date_time)).fetchone()
        ticket_id = random.randint(1, 1e7)
        print(ticket_id)
    return render_template('./auth/purchase_interface.html')

