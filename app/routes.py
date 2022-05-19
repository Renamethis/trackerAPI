from flask import jsonify, abort, request
from flask.views import View
from .database.models import Tracker
from .__init__ import create_app
from . import db
import os
from .API.Server import Server

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.route("/trackers", methods=["GET"])
def get_trackers():
    trackers = Tracker.query.all()
    data = [tracker.to_json() for tracker in trackers]
    return jsonify(data)

@app.route("/trackers/<string:isbn>", methods=["GET"])
def get_tracker(isbn):
    tracker = Tracker.query.get(isbn)
    if tracker is None:
        abort(404)
    return jsonify(tracker.to_json())

@app.route("/trackers/<string:isbn>", methods=["DELETE"])
def delete_tracker(isbn):
    book = Tracker.query.get(isbn)
    if book is None:
        abort(404)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'result': True})

@app.route('/trackers', methods=['POST'])
def create_tracker():
    if not request.json:
        abort(400)
    tracker = Tracker(
        room=request.json.get('room'),
        ip=request.json.get('ip'),
        port=request.json.get('port')
    )
    db.session.add(tracker)
    db.session.commit()
    return jsonify(tracker.to_json()), 201

@app.route('/trackers/<string:isbn>', methods=['PUT'])
def update_tracker(isbn):
    if not request.json:
        abort(400)
    tracker = Tracker.query.get(isbn)
    if tracker is None:
        abort(404)
    tracker.room = request.json.get('room', tracker.room)
    tracker.ip = request.json.get('ip', tracker.ip)
    tracker.port = request.json.get('port', tracker.port)
    db.session.commit()
    Tracker.query.all()
    return jsonify(tracker.to_json())

app.add_url_rule('/api/', view_func=Server.as_view("server"), methods = ['POST'])