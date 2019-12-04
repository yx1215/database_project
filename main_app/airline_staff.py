from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required_airline_staff

from main_app.database import get_db

import random

staff_bp = Blueprint("airline_staff", __name__, url_prefix="/staff")


@staff_bp.route('/staff_page', methods=('POST', 'GET'))
@login_required_airline_staff
def home():
    return render_template('airline_staff.html')