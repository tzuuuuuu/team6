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

@app.route("/")
#check login with decorator function
@login_required
def home():
	result=DB.getJobList()
	dat={
		"data":result,
		"userID":session.get('loginID')
	}
	return render_template('todolist.html', data=dat)

@app.route("/showJob",methods=['GET'])
@login_required
def showJob():
	id=request.args['id']
	#id=int(request.args['id'])
	dat=DB.getJobDetail(id)
	html = f"""
				id:{dat['id']}<br/>
				Name:{dat['jobName']}<br/>
				Content:{dat['jobContent']}<br/>
				<a href="/">back</a>
			"""
	return html

@app.route("/editForm",methods=['GET'])
def showEditForm():
	id=request.args['id']
	#id=int(request.args['id'])
	dat=DB.getJobDetail(id)
	return render_template('editform.html', data=dat)

@app.route("/saveJob",methods=['POST'])
#使用server side render: template 樣板
def saveJob():
	form =request.form
	dat={
		"id":form['id'],
		"name": form['name'],
		"content": form['content']
	}	
	DB.updateJob(dat)
	return redirect("/")


@app.route('/addJob', methods=['POST'])
def addJob():
	form =request.form
	dat={
		"name": form['name'],
		"content": form['content']
	}
	
	DB.addJob(dat)
	return redirect("/")


@app.route("/delJob",methods=['GET'])
@login_required
def deleteJob():
	id=request.args['id']
	#id=int(request.args['id'])
	DB.deleteJob(id)
	return redirect("/")



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
