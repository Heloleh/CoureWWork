from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@admin_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in!')
        return redirect(url_for('auth.login'))
    mongo = current_app.mongo
    if session.get('role') == 'admin':
        medicines = mongo.db.medicines.find()
    else:
        medicines = mongo.db.medicines.find({
            '$or': [
                {'created_by': session['user_id']},
                {'created_by': {'$exists': False}}
            ]
        })
    return render_template('admin/dashboard.html', medicines=medicines)

@admin_bp.route('/medicines/add', methods=['GET', 'POST'])
def add_medicine():
    if 'user_id' not in session:
        flash('Please log in!')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_url = f"/{file_path}"
        else:
            flash('Invalid file format! Use PNG, JPG, JPEG, or GIF.')
            return redirect(url_for('admin.add_medicine'))
        mongo = current_app.mongo
        mongo.db.medicines.insert_one({
            'name': name,
            'description': description,
            'price': price,
            'image': image_url,
            'created_by': session['user_id']
        })
        flash('Medicine added successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_medicine.html')

@admin_bp.route('/medicines/edit/<medicine_id>', methods=['GET', 'POST'])
def edit_medicine(medicine_id):
    if 'user_id' not in session:
        flash('Please log in!')
        return redirect(url_for('auth.login'))
    mongo = current_app.mongo
    medicine = mongo.db.medicines.find_one({'_id': ObjectId(medicine_id)})
    if not medicine or (medicine.get('created_by') != session['user_id'] and session.get('role') != 'admin'):
        flash('Access denied!')
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        update_data = {
            'name': name,
            'description': description,
            'price': price
        }
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                update_data['image'] = f"/{file_path}"
            else:
                flash('Invalid file format! Use PNG, JPG, JPEG, or GIF.')
                return redirect(url_for('admin.edit_medicine', medicine_id=medicine_id))
        mongo.db.medicines.update_one(
            {'_id': ObjectId(medicine_id)},
            {'$set': update_data}
        )
        flash('Medicine updated successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_medicine.html', medicine=medicine)

@admin_bp.route('/medicines/delete/<medicine_id>')
def delete_medicine(medicine_id):
    if 'user_id' not in session:
        flash('Please log in!')
        return redirect(url_for('auth.login'))
    mongo = current_app.mongo
    medicine = mongo.db.medicines.find_one({'_id': ObjectId(medicine_id)})
    if not medicine or (medicine.get('created_by') != session['user_id'] and session.get('role') != 'admin'):
        flash('Access denied!')
        return redirect(url_for('admin.dashboard'))
    mongo.db.medicines.delete_one({'_id': ObjectId(medicine_id)})
    flash('Medicine deleted successfully!')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/orders')
def manage_orders():
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied!')
        return redirect(url_for('catalog.index'))
    mongo = current_app.mongo
    orders = mongo.db.orders.find()
    orders_with_items = []
    for order in orders:
        item_ids = [ObjectId(item_id) for item_id in order.get('items', [])]
        items = list(mongo.db.medicines.find({'_id': {'$in': item_ids}}))
        orders_with_items.append({
            'order': order,
            'items_list': items  # Використовуємо items_list замість items
        })
    return render_template('admin/orders.html', orders=orders_with_items)

@admin_bp.route('/orders/update/<order_id>', methods=['POST'])
def update_order(order_id):
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied!')
        return redirect(url_for('catalog.index'))
    mongo = current_app.mongo
    mongo.db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'status': request.form['status']}}
    )
    flash('Order status updated!')
    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/orders/delete/<order_id>')
def delete_order(order_id):
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied!')
        return redirect(url_for('catalog.index'))
    mongo = current_app.mongo
    mongo.db.orders.delete_one({'_id': ObjectId(order_id)})
    flash('Order deleted successfully!')
    return redirect(url_for('admin.manage_orders'))