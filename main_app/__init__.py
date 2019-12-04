import os
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'main_app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/welcome')
    def welcome():
        return "Welcome to our EHR system."

    from . import database
    database.init_app(app)

    from . import authentication
    app.register_blueprint(authentication.auth_bp)

    from . import search_and_purchase
    app.register_blueprint(search_and_purchase.search_bp)

    from . import customer
    app.register_blueprint(customer.customer_bp)

    from . import booking_agent
    app.register_blueprint(booking_agent.agent_bp)

    from . import airline_staff
    app.register_blueprint(airline_staff.staff_bp)

    return app
