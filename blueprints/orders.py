from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app, request
from bson.objectid import ObjectId
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/create', methods=['GET', 'POST'])
def create_order():
    if 'user_id' not in session:
        flash('Please log in to place an order!')
        return redirect(url_for('auth.login'))
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!')
        return redirect(url_for('catalog.index'))
    
    mongo = current_app.mongo
    if request.method == 'POST':
        delivery_data = {
            'name': request.form['name'],
            'phone': request.form['phone'],
            'address': request.form['address'],
            'city': request.form['city'],
            'postal_code': request.form['postal_code']
        }
        order = {
            'user_id': session['user_id'],
            'items': session['cart'],
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'delivery_data': delivery_data
        }
        mongo.db.orders.insert_one(order)
        session['cart'] = []
        session.modified = True
        flash('Order placed successfully!')
        return redirect(url_for('orders.view_orders'))
    
    cart_items = list(mongo.db.medicines.find({'_id': {'$in': [ObjectId(id) for id in session['cart']]}}))
    return render_template('orders/create.html', cart_items=cart_items)

@orders_bp.route('/')
def view_orders():
    if 'user_id' not in session:
        flash('Please log in to view orders!')
        return redirect(url_for('auth.login'))
    mongo = current_app.mongo
    orders = mongo.db.orders.find({'user_id': session['user_id']})
    orders_with_items = []
    for order in orders:
        item_ids = [ObjectId(item_id) for item_id in order.get('items', [])]
        items = list(mongo.db.medicines.find({'_id': {'$in': item_ids}}))
        orders_with_items.append({
            'order': order,
            'items_list': items
        })
    return render_template('orders/index.html', orders=orders_with_items)