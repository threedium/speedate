#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function)

from flask import (Blueprint, request, jsonify)

from . import (login)

speed = Blueprint('speed', __name__)


@speed.route('/speedate', methods=['POST', 'GET'])
def speedate_home():
    data = request.args.to_dict()
    data['server'] = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if request.method == 'POST':
        try:
            data = {"data": True}
        except Exception as e:
            data = {"data": False, "error": str(e)}

    # return render_template('speedate/index.html')
    return jsonify(data)