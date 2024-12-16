from flask import Flask, render_template, request, session, redirect
import json
from functools import wraps
#from dbUtils import getList
import dbUtils as DB

# creates a Flask application, specify a static folder on /
app = Flask(__name__, static_folder='static',static_url_path='/')
#set a secret key to hash cookies
app.config['SECRET_KEY'] = '123TyU%^&'

#define a function wrapper to check login session
def login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		loginID = session.get('loginID')
		if not loginID:
			return redirect('/loginPage.html')
		return f(*args, **kwargs)
	return wrapper



#handles login request
@app.route('/login', methods=['POST'])
def login():
	form =request.form
	id = form['id']
	pwd =form['pwd']
	userData=DB.checkLogin(id,pwd)
	if userData:
		session['loginID']=userData['id']
		return redirect("/")
	else:
		session['loginID']=0
		return redirect("/loginPage.html")



@app.route('/allorders')
def allOrders():
    user_id = session.get('user_id')  # 假設 user_id 存在於 session 中
    if user_id:
        data = DB.getOrderList(user_id)
        return render_template('allorders.html', data=data)
    else:
        return render_template('allorders.html')
	
# 商家结算页面
@app.route('/seller/settlement')
@login_required
def merchant_settlement():
    if session.get('role') != 'merchant':
        return redirect('/')
    merchant_id = session.get('loginID')  # 获取商家ID
    data = DB.getMerchantOrders(merchant_id)  # 获取商家订单数据
    total_income = sum(order['total_price'] for order in data)
    return render_template('seller_settlement.html', orders=data, total_income=total_income, merchant_name="商家名称")


# 送货小哥结算页面
@app.route('/delivery/settlement')
@login_required
def delivery_settlement():
    if session.get('role') != 'delivery':
        return redirect('/')
    delivery_id = session.get('loginID')  # 获取送货小哥ID
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
    customer_id = session.get('loginID')  # 获取顾客ID
    data = DB.getCustomerOrders(customer_id)  # 获取顾客订单数据
    total_expense = sum(order['total_price'] for order in data)
    return render_template('customer_settlement.html', orders=data, total_expense=total_expense, customer_name="顾客名称")

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/loginPage.html')
