#!/usr/local/bin/python
# Connect to MariaDB Platform
import mysql.connector #mariadb

try:
	#連線DB
	conn = mysql.connector.connect(
		user="root",
		password="",
		host="localhost",
		port=3306,
		database="test1209"
	)
	#建立執行SQL指令用之cursor, 設定傳回dictionary型態的查詢結果 [{'欄位名':值, ...}, ...]
	cursor=conn.cursor(dictionary=True,buffered=True)
except mysql.connector.Error as e: # mariadb.Error as e:
	print(e)
	print("Error connecting to DB")
	exit(1)


def addJob(data):
	sql="insert into todo (jobName,jobContent) VALUES (%s,%s)"
	cursor.execute(sql,(data['name'],data['content']))
	conn.commit()
	return
	
def deleteJob(id):
	sql=f"delete from todo where id={id}"
	cursor.execute(sql)
	conn.commit()
	return

def updateJob(data):
	sql=f"update todo set jobName=%s,jobContent=%s where id=%s"
	cursor.execute(sql,(data['name'],data['content'],data['id']))
	conn.commit()
	return
	
def getJobList():
	sql="select * from todo;"
	cursor.execute(sql)
	return cursor.fetchall()

def getJobDetail(id):
	sql=f"select * from todo where id={id};"
	cursor.execute(sql)
	return cursor.fetchone()
	
def checkLogin(id,pwd):
	#sql=f"select * from user where id='{id}' and pwd='{pwd}'" ###不要把使用者端的資料直接進sql，這時候帳號亂打，密碼打' or'1可以登入
	#print(sql)
	#cursor.execute(sql)

	sql="select * from user where id=%s and pwd=%s"
	print(sql)
	cursor.execute(sql,(id,pwd))
	return cursor.fetchone()