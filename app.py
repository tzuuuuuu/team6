from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import dbUtils as DB

# 创建 Flask 应用
app = Flask(__name__, static_folder='static', static_url_path='/')
app.config['SECRET_KEY'] = '123TyU%^&'  # 设置 secret_key，用于 session 加密

# 定义登录保护装饰器
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loginID = session.get('loginID')
        if not loginID:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

# 用戶註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        contact_number = request.form.get('contact_number')  # 必填字段
        role = request.form.get('role')  # 必填字段

        # 验证是否填写所有字段
        if not username or not password or not contact_number or not role:
            return render_template('register.html', error="所有字段均为必填项")

        # 检查用户是否已存在
        if DB.get_user(username):
            return render_template('register.html', error="用户已存在")

        # 哈希密码并新增用户
        hashed_password = generate_password_hash(password)

        DB.add_user(username, hashed_password, role, contact_number)

        return redirect('/login')  # 注册成功后跳转至登录页面

    return render_template('register.html')


# 用戶登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return redirect(url_for('static', filename='loginPage.html'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = DB.get_user(username)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['user_id'] = user['id']
            session['role'] = user['role']  # 将角色保存到 session
            return redirect('/')
        else:
            return redirect(url_for('static', filename='loginPage.html') + '?error=用户名或密码错误')

# 注销功能
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/login')

# 首页
@app.route('/')
@login_required
def home():
    role = session.get('role')
    if role == 'merchant':
        return redirect('/seller/settlement')
    elif role == 'delivery':
        return redirect('/delivery/settlement')
    elif role == 'customer':
        return redirect('/customer/settlement')
    return "欢迎来到首页，请选择角色页面！"

# 商家结算页面
@app.route('/seller/settlement')
@login_required
def merchant_settlement():
    if session.get('role') != 'merchant':
        return redirect('/')
    merchant_id = session.get('user_id')  # 获取商家ID
    data = DB.getMerchantOrders(merchant_id)  # 获取商家订单数据
    total_income = sum(order['total_price'] for order in data)
    return render_template('seller_settlement.html', orders=data, total_income=total_income, merchant_name="商家名称")

# 送货小哥结算页面
@app.route('/delivery/settlement')
@login_required
def delivery_settlement():
    if session.get('role') != 'delivery':
        return redirect('/')
    delivery_id = session.get('user_id')  # 获取送货小哥ID
    data = DB.getDeliveryOrders(delivery_id)  # 获取送货小哥的配送订单数据
    total_income = sum(order['amount'] for order in data)
    total_orders = len(data)
    return render_template('delivery_settlement.html', deliveries=data, total_income=total_income, total_orders=total_orders, delivery_name="送货小哥")

# 顾客结算页面
@app.route('/customer/settlement')
@login_required
def customer_settlement():
    if session.get('role') != 'customer':
        return redirect('/')
    customer_id = session.get('user_id')  # 获取顾客ID
    data = DB.getCustomerOrders(customer_id)  # 获取顾客订单数据
    total_expense = sum(order['total_price'] for order in data)
    return render_template('customer_settlement.html', orders=data, total_expense=total_expense, customer_name="顾客名称")

# 查看所有订单
@app.route('/allorders')
#@login_required
def all_orders():
    data = DB.getDeliveryOrderList()
    return render_template('allorders.html', data=data)
    
# 顧客主介面
@app.route('/customer')
#@login_required
def customer():
    return render_template('customer.html')
    
# 顧客選擇菜色
@app.route('/select_food')
#@login_required
def customer_select_food():
    data = DB.getFoodList()
    return render_template('select_food.html', data=data)
    
# 顧客購物車
@app.route('/cart')
#@login_required
def customer_cart():
    #customer_id = session.get('user_id')  # 获取顾客ID
    #data = DB.getCart(customer_id)
    data = DB.getCart('223456')#我不會用登入，所以先暫時這樣
    total = DB.getCartTotal('223456')#我不會用登入，所以先暫時這樣
    Total = total['sum']
    return render_template('cart.html', data=data,Total=Total)
    
# 顧客增加餐點到購物車
@app.route('/add_cart/<int:food_id>', methods=['GET', 'POST'])
#@login_required
def customer_add_cart(food_id):
    if request.method == 'POST':
        #user_id = session.get('user_id')  # 获取顾客ID
        user_id='223456'#我不會用登入，所以先暫時這樣
        quantity = request.form['quantity']
        data = {"user_id": user_id, "food_id": food_id, "quantity": quantity}
        DB.addToCart(data)
        return redirect(url_for('customer_select_food'))
    
    data = DB.addToCartPage(food_id)
    return render_template('add_cart.html', data=data, food_id=food_id)
    
# 顧客刪除購物車內的餐點
@app.route('/remove_From_Cart/<int:cart_id>')
#@login_required
def customer_remove_From_Cart(cart_id):
    DB.removeFromCart(cart_id)
    return redirect(url_for('customer_cart'))
    
    
# 顧客送出訂單
@app.route('/add_order')
#@login_required
def customer_add_order():
    #user_id = session.get('user_id')  # 获取顾客ID
    user_id='223456'#我不會用登入，所以先暫時這樣
    
    return render_template('add_cart.html', data=data, food_id=food_id)
    
@app.route('/accept_order', methods=['POST'])
#@login_required
def accept_order():
    # 確認當前使用者角色為外送員
    #if session.get('role') != 'delivery':
        #return redirect('/')

    order_id = request.form.get('order_id')  # 從表單取得訂單 ID
    delivery_user_id = session.get('user_id')  # 取得目前登入外送員的 ID
    message = ""  # 用於提示訊息
    
    if order_id and delivery_user_id:
        # 更新訂單狀態為 "in_delivery"
        DB.updateOrderStatus(order_id, 'in_delivery')

        # 新增至 delivery_orders
        DB.addDeliveryOrder(order_id=order_id, delivery_user_id=delivery_user_id)

        message = f"成功接單 #{order_id}"
    else:
        message = "接單失敗，請確認訂單 ID 或登入狀態"

    # 重新加載所有可接的訂單列表
    data = DB.getDeliveryOrderList()
    return render_template('allorders.html', message=message, data=data)

@app.route('/owndelivery')
#@login_required
def own_delivery():
    """
    顯示當前登入用戶接的訂單
    """
    #user_id = session.get('user_id')  # 獲取目前登入的用戶 ID
    data = DB.getOwnDeliveryOrders()
    order=DB.getOwnDeliveryOrders_ing()
    endorder=DB.getOwnDeliveryOrders_end()  # 從資料庫中獲取接單的訂單
    return render_template('owndelivery.html', data=data,order=order,endorder=endorder)

@app.route('/update_status', methods=['POST'])
#@login_required
def update_status():
    # 確保只有配送人員可以訪問此路由
    if session.get('role') != 'delivery':
        return redirect('/')

    # 接收表單提交的數據
    delivery_id = request.form.get('delivery_id')
    new_status = request.form.get('new_status')

    # 檢查是否有必要的參數
    if not delivery_id or not new_status:
        return redirect('/owndelivery')  # 返回外送清單頁面

    # 獲取當前時間
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 根據狀態執行更新
    if new_status == 'in_delivery':
        # 更新狀態為 "in_delivery" 並設置取貨時間
        DB.update_delivery_status_and_time(
            delivery_id=delivery_id,
            new_status=new_status,
            field_to_update='pickup_time',
            time_value=current_time
        )
        message = f"外送訂單 #{delivery_id} 狀態更新為 'in_delivery'"
    elif new_status == 'completed':
        # 更新狀態為 "completed" 並設置外送時間
        DB.update_delivery_status_and_time(
            delivery_id=delivery_id,
            new_status=new_status,
            field_to_update='delivery_time',
            time_value=current_time
        )
        message = f"外送訂單 #{delivery_id} 狀態更新為 'completed'"
    else:
        message = "狀態更新失敗，無效的請求"

    # 您可以選擇將 message 顯示在前端（這裡只是打印，具體看需求）
    print(message)

    # 返回外送清單頁面
    # 重新載入已接訂單頁面
    return redirect('/owndelivery',message=message)


    
if __name__ == '__main__':
    app.run(debug=True)
