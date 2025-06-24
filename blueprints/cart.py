from flask import Blueprint, session, redirect, url_for, flash, current_app, render_template
from bson.objectid import ObjectId

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add/<medicine_id>')
def add_to_cart(medicine_id):
    if 'user_id' not in session:
        flash('Please log in to add items to cart!')
        return redirect(url_for('auth.login'))
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(medicine_id)
    session.modified = True
    flash('Medicine added to cart!')
    return redirect(url_for('catalog.index'))

@cart_bp.route('/')
def view_cart():
    if 'cart' not in session:
        session['cart'] = []
    mongo = current_app.mongo
    cart_items = mongo.db.medicines.find({'_id': {'$in': [ObjectId(id) for id in session['cart']]}})
    return render_template('cart/index.html', cart_items=cart_items)

@cart_bp.route('/remove/<medicine_id>')
def remove_from_cart(medicine_id):
    if 'cart' in session and medicine_id in session['cart']:
        session['cart'].remove(medicine_id)
        session.modified = True
        flash('Medicine removed from cart!')
    else:
        flash('Item not found in cart!')
    return redirect(url_for('cart.view_cart'))
