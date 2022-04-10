#!/usr/bin/env python
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301, USA.

import os
from flask import request
from flask import Flask
from flask import send_from_directory
from pathlib import Path
from werkzeug.serving import WSGIRequestHandler


STATIC_FILE_DIR = os.path.join(str(os.getcwd()), "Content/")
TEMPLATE_STATIC_FILE = "Client_%s/Run_%s/Page_%s/%s"

def create_app(test_config=None):
    # create and configure the app
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app = Flask(__name__, instance_relative_config=True, static_url_path='')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
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

    # a simple page that says hello
    @app.route('/page', methods=['GET'])
    def hello():
        user = request.args.get('user')
        page = request.args.get('page')
        run = request.args.get('run')
        obj = request.args.get('obj')
        
        #print(TEMPLATE_STATIC_FILE%(user, run, page, obj))
        return send_from_directory(STATIC_FILE_DIR, TEMPLATE_STATIC_FILE%(user, run, page, obj))
        #print(STATIC_FILE_DIR)
        #return 'Hello, World!'

    return app
