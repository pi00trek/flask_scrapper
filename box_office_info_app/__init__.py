from flask import Flask
from flask_bootstrap import Bootstrap


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_object()  # or file? #TODO: create a proper config
    app.config.from_mapping(SECRET_KEY='dev')

    bootstrap = Bootstrap(app)

    from box_office_info_app import routes

    app.register_blueprint(routes.bp)

    return app


