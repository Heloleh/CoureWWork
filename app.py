import os
from flask import Flask, redirect, url_for
from flask_pymongo import PyMongo
from blueprints.auth import auth_bp
from blueprints.catalog import catalog_bp
from blueprints.cart import cart_bp
from blueprints.orders import orders_bp
from blueprints.analytics import analytics_bp
from blueprints.admin import admin_bp
from blueprints.reviews import reviews_bp

# Ініціалізація Flask додатку
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/ApTeKa"
app.config["SECRET_KEY"] = "your-secret-key"
app.config["UPLOAD_FOLDER"] = "static/uploads"  # Папка для зберігання зображень
app.config["ALLOWED_EXTENSIONS"] = {'png', 'jpg', 'jpeg', 'gif'}  # Дозволені формати файлів

# Ініціалізація MongoDB
mongo = PyMongo(app)

# Реєстрація blueprint'ів
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(catalog_bp, url_prefix="/catalog")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(analytics_bp, url_prefix="/analytics")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(reviews_bp, url_prefix="/reviews")

# Передача об'єкта mongo до blueprint'ів
app.mongo = mongo

# Головна сторінка
@app.route('/')
def index():
    return redirect(url_for('catalog.index'))

if __name__ == '__main__':
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # Створити папку для завантажень, якщо не існує
    app.run(debug=True)