from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import dbUtils as DB

# 建立 Flask 應用
app = Flask(__name__, static_folder='static', static_url_path='/')
app.config['SECRET_KEY'] = '123TyU%^&'  # 設定 secret_key，用於 session 加密

# 登入保護裝飾器
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loginID = session.get('loginID')  # ← 注意這裡檢查的是 loginID
        if not loginID:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

# 使用者註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        contact_number = request.form.get('contact_number')  # 必填
        role = request.form.get('role')                     # 必填

        # 驗證是否填寫所有欄位
        if not username or not password or not contact_number or not role:
            return render_template('register.html', error="所有字段均為必填項")

        # 檢查使用者是否已存在
        if DB.get_user(username):
            return render_template('register.html', error="使用者已存在")

        # 哈希密碼後新增使用者
        hashed_password = generate_password_hash(password)
        DB.add_user(username, hashed_password, role, contact_number)

        return redirect('/login')  # 註冊成功後跳轉至登入頁面

    return render_template('register.html')

# 使用者登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':  # 返回登入頁面 (靜態檔案)
        return redirect(url_for('static', filename='loginPage.html'))

    # 處理 POST 請求
    username = request.form['username']
    password = request.form['password']
    
    user = DB.get_user(username)
    print("從資料庫取得的使用者資訊:", user)  # 調試

    if user and check_password_hash(user['password'], password):
        # ↓↓↓ 在這裡多加一行 session['loginID']，讓 login_required 能檢查到 ↓↓↓
        session['username'] = user['username']
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['loginID'] = user['id']  # ← 新增這行

        print("登入成功，session 資料:", session)  # 調試
        return redirect('/')  # 登入成功後導回首頁
    else:
        flash("使用者名稱或密碼錯誤")
        return redirect(url_for('static', filename='loginPage.html'))

# 使用者登出
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/login')

# 首頁，依照角色跳轉
@app.route('/')
@login_required
def home():
    role = session.get('role')
    print("當前使用者角色:", role)  # 調試
    if role == 'merchant':
        return redirect('/seller/settlement')   # 商家結算頁
    elif role == 'delivery':
        return redirect('/allorders')          # 外送員所有訂單頁
    elif role == 'customer':
        return redirect('/customer')           # 顧客主頁面
    else:
        # 如果沒有正確的角色，清除 session 並返回登入頁
        session.clear()
        return redirect('/login')

# 商家結算頁
@app.route('/seller/settlement')
@login_required
def merchant_settlement():
    if session.get('role') != 'merchant':
        return redirect('/')
    merchant_id = session.get('user_id')  # 取得商家 ID
    data = DB.getMerchantOrders(merchant_id)
    total_income = sum(order['total_price'] for order in data)
    return render_template('seller_settlement.html',
                           orders=data,
                           total_income=total_income,
                           merchant_name=session['username'])

# 外送員結算頁
@app.route('/delivery/settlement')
@login_required
def delivery_settlement():
    if session.get('role') != 'delivery':
        return redirect('/')
    delivery_id = session.get('user_id')  # 取得外送員 ID
    data = DB.getDeliveryOrders(delivery_id)
    total_income = sum(order['amount'] for order in data)
    total_orders = len(data)
    return render_template('delivery_settlement.html',
                           deliveries=data,
                           total_income=total_income,
                           total_orders=total_orders,
                           delivery_name=session['username'])

# 顧客結算頁
@app.route('/customer/settlement')
@login_required
def customer_settlement():
    if session.get('role') != 'customer':
        return redirect('/')
    customer_id = session.get('user_id')  # 取得顧客 ID
    data = DB.getCustomerOrders(customer_id)
    total_expense = sum(order['total_price'] for order in data)
    return render_template('customer_settlement.html',
                           orders=data,
                           total_expense=total_expense,
                           customer_name=session['username'])

# 查看所有訂單 (外送員)
@app.route('/allorders')
@login_required
def all_orders():
    if session.get('role') != 'delivery':
        return redirect('/')
    data = DB.getDeliveryOrderList()
    print("所有訂單資料:", data)  # 調試
    return render_template('allorders.html', data=data)

# 顧客主頁
@app.route('/customer')
@login_required
def customer():
    if session.get('role') != 'customer':
        return redirect('/')
    return render_template('customer.html')

# 顧客選擇餐點頁
@app.route('/select_food')
@login_required
def customer_select_food():
    if session.get('role') != 'customer':
        return redirect('/')
    data = DB.getFoodList()
    return render_template('select_food.html', data=data)

# 顧客購物車頁
@app.route('/cart')
@login_required
def customer_cart():
    if session.get('role') != 'customer':
        return redirect('/')
    customer_id = session.get('user_id')
    data = DB.getCart(customer_id)
    return render_template('cart.html', data=data)

# 顧客將餐點加入購物車
@app.route('/add_cart/<int:food_id>', methods=['GET', 'POST'])
@login_required
def customer_add_cart(food_id):
    if session.get('role') != 'customer':
        return redirect('/')
    if request.method == 'POST':
        customer_id = session.get('user_id')
        quantity = request.form['quantity']
        data = {"user_id": customer_id, "food_id": food_id, "quantity": quantity}
        DB.addToCart(data)
        return redirect(url_for('customer_select_food'))
    
    data = DB.addToCartPage(food_id)
    return render_template('add_cart.html', data=data, food_id=food_id)

if __name__ == '__main__':
    app.run(debug=True)
