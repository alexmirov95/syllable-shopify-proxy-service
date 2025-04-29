"""app.py

Syllable Shopify Proxy Service.

Serves as proxy layer between Syllable agents and Shopify APIs.
"""
import logging
from flask import Flask, request, jsonify

from shopify import GetOrders, GetProducts

logging.basicConfig(
    level=logging.INFO
)
app = Flask(__name__)


@app.route('/')
def health_check():
    app.logger.info('Service up.')
    return "Ok.", 200
