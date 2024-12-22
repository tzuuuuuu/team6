from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import dbUtils as DB

app = Flask(__name__, static_folder='static', static_url_path='/')
app.config['SECRET_KEY'] = '123TyU%^&'

# 登入保護裝飾器
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loginID = session.get('loginID')
        if not loginID:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

# 顧客購物車頁
@app.route('/cart')
@login_required
def customer_cart():
    if session.get('role') != 'customer':
        return redirect('/')
    customer_id = session.get('user_id')  # 取得顧客 ID
    data = DB.getCart(customer_id)
    total = DB.getCartTotal(customer_id)
    Total = total['sum']
    return render_template('cart.html', data=data, Total=Total)

# 顧客將餐點加入購物車
@app.route('/add_cart/<int:food_id>', methods=['GET', 'POST'])
@login_required
def customer_add_cart(food_id):
    if session.get('role') != 'customer':
        return redirect('/')
    if request.method == 'POST':
        customer_id = session.get('user_id')  # 取得顧客 ID
        quantity = request.form['quantity']
        data = {"user_id": customer_id, "food_id": food_id, "quantity": quantity}
        DB.addToCart(data)
        return redirect(url_for('customer_select_food'))
    
    data = DB.addToCartPage(food_id)
    return render_template('add_cart.html', data=data, food_id=food_id)

# 顧客刪除購物車內的餐點
@app.route('/remove_From_Cart/<int:cart_id>')
@login_required
def customer_remove_From_Cart(cart_id):
    DB.removeFromCart(cart_id)
    return redirect(url_for('customer_cart'))

# 顧客送出訂單
@app.route('/add_order')
@login_required
def customer_add_order():
    customer_id = session.get('user_id')  # 取得顧客 ID
    data = DB.createOrder(customer_id)  # 假設 DB.createOrder 創建新訂單
    return redirect(url_for('customer_cart'))

# 接單 (外送員)
@app.route('/accept_order', methods=['POST'])
@login_required
def accept_order():
    if session.get('role') != 'delivery':
        return redirect('/')
    
    order_id = request.form.get('order_id')
    delivery_user_id = session.get('user_id')
    message = ""

    if order_id and delivery_user_id:
        DB.updateOrderStatus(order_id, 'in_delivery')
        DB.addDeliveryOrder(order_id=order_id, delivery_user_id=delivery_user_id)
        message = f"成功接單 #{order_id}"
    else:
        message = "接單失敗，請確認訂單 ID 或登入狀態"

    data = DB.getDeliveryOrderList()
    return render_template('allorders.html', message=message, data=data)

# 顯示外送員已接訂單
@app.route('/owndelivery')
@login_required
def own_delivery():
    delivery_id = session.get('user_id')
    data = DB.getOwnDeliveryOrders(delivery_id)
    order = DB.getOwnDeliveryOrders_ing(delivery_id)
    endorder = DB.getOwnDeliveryOrders_end(delivery_id)
    return render_template('owndelivery.html', data=data, order=order, endorder=endorder)

# 更新訂單狀態 (外送員)
@app.route('/update_status', methods=['POST'])
@login_required
def update_status():
    if session.get('role') != 'delivery':
        return redirect('/')

    delivery_id = request.form.get('delivery_id')
    new_status = request.form.get('new_status')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not delivery_id or not new_status:
        return redirect('/owndelivery')

    if new_status == 'in_delivery':
        DB.update_delivery_status_and_time(
            delivery_id=delivery_id,
            new_status=new_status,
            field_to_update='pickup_time',
            time_value=current_time
        )
    elif new_status == 'completed':
        DB.update_delivery_status_and_time(
            delivery_id=delivery_id,
            new_status=new_status,
            field_to_update='delivery_time',
            time_value=current_time
        )
    return redirect('/owndelivery')
