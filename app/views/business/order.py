from . import business_bp

@business_bp.route('/orders')
def list_orders():
    return "Order List"
