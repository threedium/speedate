#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

import os
import uuid
from config import app_config
from flask import (Flask, jsonify)

def create_app(config_name):
    errordata = {"data": False}
    if os.getenv('FLASK_CONFIG') == "production":
        app = Flask(__name__)
        app.config.update(
            SECRET_KEY=os.getenv('SECRET_KEY'),
            # SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI')
        )

    else:
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_object(app_config[config_name])
        app.config.from_pyfile('config.py')

    from .speedate import speed as speed_blueprint
    app.register_blueprint(speed_blueprint)

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"data": False, "error": "forbidden from accessing data", "code": 403}), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({"data": False, "error": "page link not found", "code": 404}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"data": False, "error": "internal server error", "code": 500}), 500

    return app
    