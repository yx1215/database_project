from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required_booking_agent

from main_app.database import get_db

import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

agent_bp = Blueprint("booking_agent", __name__, url_prefix="/booking_agent")


@agent_bp.route('/agent_page', methods=('POST', 'GET'))
@login_required_booking_agent
def home():
    return render_template('./booking_agent.html')


@agent_bp.route('/my_purchase', methods=('POST', 'GET'))
@login_required_booking_agent
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
               'WHERE booking_agent=? AND depart_airport LIKE ? AND depart_city LIKE ? AND arrive_airport LIKE ? AND arrive_city LIKE ?'
               'AND depart_date_time BETWEEN ? AND ?',
               (g.user['agent_email'], depart_airport, depart_city, arrive_airport, arrive_city, from_date, to_date))
    return render_template('view_purchased_ticket.html', my_purchase=my_ticket)


# total commission, average commission, total num of ticket
@agent_bp.route('/my_commission', methods=('POST', 'GET'))
@login_required_booking_agent
def my_commission():
    from_date = request.args["from_date"]
    to_date = request.args["to_date"]
    if from_date == "" or to_date == "":
        to_date = str(datetime.now())
        from_date = str(datetime.now() - relativedelta(days=30))
    else:
        to_date = to_date + " 23:59:59"
        from_date = from_date + " 00:00:00"
    db = get_db()
    agent_email = g.user["agent_email"]
    total_commission = db.execute("SELECT SUM(sold_price * 0.1) as total_commission FROM Purchase WHERE booking_agent=?"
                                  "AND purchase_date_time BETWEEN ? AND ?",
                                  (agent_email, from_date, to_date)).fetchone()
    average_commission = db.execute("SELECT AVG(sold_price * 0.1) as avg_commission FROM Purchase WHERE booking_agent=?"
                                    "AND purchase_date_time BETWEEN ? AND ?",
                                    (agent_email, from_date, to_date)).fetchone()
    num_of_ticket = db.execute("SELECT COUNT(*) as num FROM Purchase WHERE booking_agent=?"
                               "AND purchase_date_time BETWEEN ? AND ?",
                               (agent_email, from_date, to_date)).fetchone()

    return render_template('view_my_commission.html', total_commission=total_commission,
                           average_commission=average_commission, num_of_ticket=num_of_ticket,
                           from_date=from_date[:10], to_date=to_date[:10])


@agent_bp.route("/view_top_customers", methods=("GET", "POST"))
def view_top_customers():
    agent_email = g.user["agent_email"]
    db = get_db()
    current = str(datetime.now())
    six_month_ago = str(datetime.now() - relativedelta(months=6))
    one_year_ago = str(datetime.now() - relativedelta(years=1))

    top_by_tickets = db.execute("SELECT cust_email, COUNT(*) as count FROM Purchase WHERE booking_agent=? "
                                "AND purchase_date_time BETWEEN ? AND ?"
                                "GROUP BY cust_email ORDER BY count DESC LIMIT 5",
                                (agent_email, six_month_ago, current))
    top_by_commission = db.execute("SELECT cust_email, SUM(sold_price * 0.1) as total_commission FROM Purchase "
                                   "WHERE booking_agent=? AND purchase_date_time BETWEEN ? AND ?"
                                   "GROUP BY cust_email ORDER BY total_commission DESC LIMIT 5",
                                   (agent_email, one_year_ago, current))
    top_by_tickets_l = []
    top_by_commission_l = []

    index = 1
    for r in top_by_tickets:
        d = {}
        d["cust_email"] = r["cust_email"]
        d["count"] = r["count"]
        d["index"] = index
        top_by_tickets_l.append(d)
        index += 1

    index = 1
    for r in top_by_commission:
        d = {}
        d["cust_email"] = r["cust_email"]
        d["total_commission"] = r["total_commission"]
        d["index"] = index
        top_by_commission_l.append(d)
        index += 1

    return render_template("top_customers.html", top_by_tickets=top_by_tickets_l, top_by_commission=top_by_commission_l)
