#!/usr/bin/env python
import sys
from os import path
sys.path.insert(0, path.join(path.dirname(__file__), '../src'))

from flask import Flask, render_template, url_for
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)

assets = Environment(app)
assets.register('main',
                'style1.css', 'style2.css',
                output='cached.css', filters='cssmin')

@app.route('/')
def index():
    return render_template('index.html')


app.run(debug=True)