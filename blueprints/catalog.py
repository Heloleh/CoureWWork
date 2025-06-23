from flask import Blueprint, render_template, request, redirect, url_for, current_app
from bson.objectid import ObjectId

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/')
def index():
    mongo = current_app.mongo
    medicines = mongo.db.medicines.find()
    return render_template('catalog/index.html', medicines=medicines)

@catalog_bp.route('/medicine/<medicine_id>')
def medicine_detail(medicine_id):
    mongo = current_app.mongo
    medicine = mongo.db.medicines.find_one({'_id': ObjectId(medicine_id)})
    reviews = mongo.db.reviews.find({'medicine_id': medicine_id})
    return render_template('catalog/detail.html', medicine=medicine, reviews=reviews)