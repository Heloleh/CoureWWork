from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
def index():
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied!')
        return redirect(url_for('catalog.index'))
    mongo = current_app.mongo
    total_orders = mongo.db.orders.count_documents({})
    popular_medicines = mongo.db.orders.aggregate([
        {'$unwind': '$items'},
        {'$group': {'_id': '$items', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ])
    return render_template('analytics/index.html', total_orders=total_orders, popular_medicines=popular_medicines)