from . import business_bp
from flask import render_template

@business_bp.route('/customers')
def list_customers():
    return render_template('business/customer_list.html')

@business_bp.route('/customers/new')
def new_customer():
    return render_template('business/customer_form.html')
