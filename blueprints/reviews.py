from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from bson.objectid import ObjectId
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/add/<medicine_id>', methods=['POST'])
def add_review(medicine_id):
    if 'user_id' not in session:
        flash('Please log in to leave a review!')
        return redirect(url_for('auth.login'))
    mongo = current_app.mongo
    mongo.db.reviews.insert_one({
        'medicine_id': medicine_id,
        'user_id': session['user_id'],
        'username': session['username'],
        'rating': int(request.form['rating']),
        'comment': request.form['comment'],
        'created_at': datetime.utcnow()
    })
    flash('Review added successfully!')
    return redirect(url_for('catalog.medicine_detail', medicine_id=medicine_id))

@reviews_bp.route('/delete/<review_id>')
def delete_review(review_id):
    if 'user_id' not in session:
        flash('Please log in!')
        return redirect(url_for('auth.login'))
    mongo = current_app.mongo
    review = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})
    if not review or (review['user_id'] != session['user_id'] and session.get('role') != 'admin'):
        flash('Access denied!')
        return redirect(url_for('catalog.index'))
    medicine_id = review['medicine_id']
    mongo.db.reviews.delete_one({'_id': ObjectId(review_id)})
    flash('Review deleted successfully!')
    return redirect(url_for('catalog.medicine_detail', medicine_id=medicine_id))