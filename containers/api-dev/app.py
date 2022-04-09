#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Flask server acting as an API for HTTP requests during development
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/Werbemittel/api/Importer', methods=["POST"])
def insert():
    """
    Route for API endpoint
    """
    received_data = request.get_json()
    print(f"received: {received_data}")

    return received_data

@app.errorhandler(404)
def page_not_found(e):
    """
    Handler for page not found 404
    """
    #pylint: disable=unused-argument
    return "Flask 404 here, but not the page you requested."


@app.errorhandler(500)
def internal_server_error(e):
    """
    Handler for internal server error 500
    """
    #pylint: disable=unused-argument,import-outside-toplevel
    import traceback
    return "500 error" + traceback.format_exc()


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
