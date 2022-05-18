from flask import jsonify, abort
from flask.views import View
from .database.models import Tracker
from .__init__ import create_app
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.route("/trackers", methods=["GET"])
def get_trackers():
    trackers = Tracker.query.all()
    data = [tracker.to_json() for tracker in trackers]
    return jsonify(data)

@app.route("/trackers/<int:isbn>", methods=["GET"])
def get_tracker(isbn):
    tracker = Tracker.query.get(isbn)
    if tracker is None:
        abort(404)
    return jsonify(tracker.to_json())