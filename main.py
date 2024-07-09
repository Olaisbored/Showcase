import logging
import random
from flask import Flask, render_template, abort, request, redirect, url_for
from gunicorn.app.base import BaseApplication
import json

from routes import create_app
app = create_app()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load product data
with open('products.json', 'r') as f:
    products = json.load(f)

# Add ratings to products
for product in products:
    product['rating'] = round(random.uniform(1, 5), 1)
    product['reviews'] = []

@app.route('/')
def home():
    return render_template('home.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product is None:
        return render_template('404.html'), 404
    return render_template('product_detail.html', product=product)

@app.route('/add_review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product is None:
        abort(404)
    rating = int(request.form['rating'])
    review_text = request.form['review_text']
    product['reviews'].append({'rating': rating, 'text': review_text})
    product['rating'] = round(sum(r['rating'] for r in product['reviews']) / len(product['reviews']), 1)
    return redirect(url_for('product_detail', product_id=product_id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        # Apply configuration to Gunicorn
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    options = {
        "bind": "0.0.0.0:8080",
        "workers": 4,
        "loglevel": "info",
        "accesslog": "-"
    }
    StandaloneApplication(app, options).run()