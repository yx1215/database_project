from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from main_app.authentication import login_required_booking_agent

from main_app.database import get_db

import random

agent_bp = Blueprint("booking_agent", __name__, url_prefix="/booking_agent")


@agent_bp.route('/agent_page', methods=('POST', 'GET'))
@login_required_booking_agent
def home():
    return render_template('./booking_agent.html')