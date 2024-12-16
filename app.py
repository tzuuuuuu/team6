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