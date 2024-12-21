#!/usr/local/bin/python
# Connect to MariaDB Platform
import mysql.connector  # 使用 mysql.connector 驱动连接 MySQL/MariaDB

# 数据库连接设置
try:
    # 连接数据库
    conn = mysql.connector.connect(
        user="root",          # 数据库用户名
        password="",          # 数据库密码
        host="localhost",     # 主机地址
        port=3306,            # 端口号
        database="fooddelivery"  # 数据库名称
    )
    # 创建 cursor，用于执行 SQL 指令，返回结果以字典格式表示
    cursor = conn.cursor(dictionary=True, buffered=True)
except mysql.connector.Error as e:
    print(e)
    print("Error connecting to DB")
    exit(1)

# 用户相关操作
def checkLogin(username, password):
    """
    验证用户登录
    """
    sql = "SELECT * FROM user WHERE username = %s AND password = %s"
    cursor.execute(sql, (username, password))
    return cursor.fetchone()

def add_user(username, password, role, contact_info):
    """
    添加新用户
    """
    sql = """
    INSERT INTO user (username, password, role, contact_info)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (username, password, role, contact_info))
    conn.commit()

def get_user(username):
    """
    获取用户信息
    """
    sql = "SELECT * FROM user WHERE username = %s"
    cursor.execute(sql, (username,))
    return cursor.fetchone()


# 菜品相关操作
def getFoodList():
    """
    获取所有菜品
    """
    sql = "SELECT * FROM food"
    cursor.execute(sql)
    return cursor.fetchall()

def addFood(data):
    """
    添加菜品
    """
    sql = "INSERT INTO food (merchant_id, f_name, f_price, f_content) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (data['merchant_id'], data['f_name'], data['f_price'], data['f_content']))
    conn.commit()

# 购物车相关操作
def getCart(user_id):
    """
    获取购物车内容
    """
    sql = """
    SELECT car.cart_id, food.f_name, food.f_price, car.quantity 
    FROM car 
    JOIN food ON car.food_id = food.food_id 
    WHERE car.user_id = %s
    """
    cursor.execute(sql, (user_id,))
    return cursor.fetchall()

def addToCart(data):
    """
    添加菜品到购物车
    """
    sql = "INSERT INTO car (user_id, food_id, quantity) VALUES (%s, %s, %s)"
    cursor.execute(sql, (data['user_id'], data['food_id'], data['quantity']))
    conn.commit()

def removeFromCart(cart_id):
    """
    从购物车中移除菜品
    """
    sql = "DELETE FROM car WHERE cart_id = %s"
    cursor.execute(sql, (cart_id,))
    conn.commit()

# 订单相关操作
def createOrder(data):
    """
    创建订单
    """
    # 插入订单信息
    sql_order = "INSERT INTO orders (user_id, total_price, order_date, order_status) VALUES (%s, %s, NOW(), 'pending')"
    cursor.execute(sql_order, (data['user_id'], data['total_price']))
    order_id = cursor.lastrowid

    # 插入订单详情
    for item in data['items']:
        sql_details = "INSERT INTO order_details (order_id, food_id, quantity, price) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_details, (order_id, item['food_id'], item['quantity'], item['price']))
    conn.commit()
    return order_id

def updateOrderStatus(order_id, status):
    """
    更新订单状态
    """
    sql = "UPDATE orders SET order_status = %s WHERE order_id = %s"
    cursor.execute(sql, (status, order_id))
    conn.commit()

def getOrderList(user_id):
    """
    获取用户的订单列表
    """
    sql = "SELECT * FROM orders WHERE user_id = %s"
    cursor.execute(sql, (user_id,))
    return cursor.fetchall()

# 商家结算相关操作
def getMerchantOrders(merchant_id):
    """
    获取商家的已完成订单数据
    """
    sql = """
    SELECT o.order_id, o.total_price, o.order_date
    FROM orders o
    JOIN food f ON f.food_id = o.order_id
    WHERE f.merchant_id = %s AND o.order_status = 'completed'
    """
    cursor.execute(sql, (merchant_id,))
    return cursor.fetchall()

# 送货小哥结算相关操作
def getDeliveryOrders(delivery_id):
    """
    获取送货小哥的配送收入和接单数据
    """
    sql = """
    SELECT d.order_id, d.delivery_time, 5 AS amount
    FROM delivery_orders d
    WHERE d.delivery_user_id = %s AND d.delivery_status = 'completed'
    """
    cursor.execute(sql, (delivery_id,))
    return cursor.fetchall()

# 顾客结算相关操作
def getCustomerOrders(customer_id):
    """
    获取顾客的订单消费记录
    """
    sql = """
    SELECT order_id, total_price, order_date, order_status
    FROM orders
    WHERE user_id = %s
    """
    cursor.execute(sql, (customer_id,))
    return cursor.fetchall()

# 结算记录操作
def recordSettlement(user_id, role, amount, transaction_type, order_id=None):
    """
    添加结算记录
    """
    sql = """
    INSERT INTO settlements (user_id, role, amount, transaction_type, order_id, settlement_date) 
    VALUES (%s, %s, %s, %s, %s, NOW())
    """
    cursor.execute(sql, (user_id, role, amount, transaction_type, order_id))
    conn.commit()

def getDeliveryOrderList():
    """
    送餐小哥可接所有訂單
    """
    sql = "SELECT * FROM orders WHERE order_status = 'pending'"
    cursor.execute(sql)
    return cursor.fetchall()

def updateOrderStatus(order_id, status):
    """
    更新訂單狀態
    """
    sql = "UPDATE orders SET order_status = %s WHERE order_id = %s"
    cursor.execute(sql, (status, order_id))
    conn.commit()

def assignDeliveryOrder(order_id, delivery_user_id):
    """
    分配訂單給外送員，插入到 delivery_orders 表
    """
    sql = """
    INSERT INTO delivery_orders (order_id, delivery_user_id, delivery_status, pickedup_time, delivery_time)
    VALUES (%s, %s, 'accepted', NULL, NULL)
    """
    cursor.execute(sql, (order_id, delivery_user_id))
    conn.commit()
    return cursor.lastrowid

def getOwnDeliveryOrders():
    """
    查詢當前登入外送員接的訂單
    """
    sql = "SELECT * FROM delivery_orders WHERE delivery_status = 'accepted'"
    cursor.execute(sql)
    return cursor.fetchall()



# 关闭数据库连接（程序结束时调用）
def closeConnection():
    """
    关闭数据库连接
    """
    cursor.close()
    conn.close()
