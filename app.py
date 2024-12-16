from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
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
        username = request.form['username']
        password = request.form['password']
        
        # 檢查用戶是否已存在
        if DB.get_user(username):
            return render_template('register.html', error="用户已存在")
        
        # 哈希密码并新增用戶
        hashed_password = generate_password_hash(password)
        DB.add_user(username, hashed_password)
        return redirect('/login')  # 註冊成功後重定向至登入頁面
    
    return render_template('register.html')

# 用戶登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('loginPage.html')
    
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
            return render_template('loginPage.html', error="用户名或密码错误")

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
    if role == 'seller':
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
    if session.get('role') != 'seller':
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
@login_required
def all_orders():
    user_id = session.get('user_id')
    if user_id:
        data = DB.getOrderList(user_id)
        return render_template('allorders.html', data=data)
    return render_template('allorders.html')
    
if __name__ == '__main__':
    app.run(debug=True)
