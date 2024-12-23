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
    
def addToCartPage(food_id):
    """
    添加菜品的頁面資訊
    """
    sql = "SELECT food_id, f_name, f_price FROM food WHERE food_id = %s"
    cursor.execute(sql, (food_id,))
    return cursor.fetchall()

def removeFromCart(cart_id):
    """
    从购物车中移除菜品
    """
    sql = "DELETE FROM car WHERE cart_id = %s"
    cursor.execute(sql, (cart_id,))
    conn.commit()

def getCartTotal(user_id):
    """
    計算購物車總金額
    """
    sql = """
    SELECT SUM(food.f_price * car.quantity) AS sum
    FROM car
    JOIN food ON car.food_id = food.food_id
    WHERE car.user_id = %s
    """
    cursor.execute(sql, (user_id,))
    return cursor.fetchone()

# 订单相关操作
def createOrder(data):
    """
    创建订单
    """

    # 插入订单信息
    sql_order = "INSERT INTO orders (user_id, total_price, order_date, order_status) VALUES (%s, %s, NOW(), 'pending')"
    cursor.execute(sql_order, (data['user_id'], data['total_price']))
    order_id = cursor.lastrowid
    
    sql = """
    SELECT food.food_id, car.quantity, food.f_price
    FROM car 
    JOIN food ON car.food_id = food.food_id 
    WHERE car.user_id = %s
    """
    cursor.execute(sql, (data['user_id'],))
    items = cursor.fetchall()
    
    
    # 插入订单详情
    for item in items:
        sql_details = "INSERT INTO order_details (order_id, food_id, quantity, price) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_details, (order_id, item['food_id'], item['quantity'], item['f_price']))
    
    sql_clear = "DELETE FROM car WHERE user_id = %s" #送出訂單時清空購物車
    cursor.execute(sql_clear, (data['user_id'],))
    conn.commit()

def updateOrderStatus(order_id, status):
    """
    更新订单状态
    """
    sql = "UPDATE orders SET order_status = %s WHERE order_id = %s"
    cursor.execute(sql, (status, order_id))
    conn.commit()
    
def updateDeliveryOrderStatus(order_id, status):
    """
    更新送貨订单状态
    """
    sql = "UPDATE delivery_orders SET delivery_status = %s WHERE order_id = %s"
    cursor.execute(sql, (status, order_id))
    conn.commit()
    
def getOrderList(user_id):
    """
    获取用户的订单列表，
    如果订单在 delivery_order 表中存在，返回对应的 delivery_status。
    """
    # 获取用户的订单列表
    sql_orders = """
    SELECT o.*, d.delivery_status
    FROM orders o
    LEFT JOIN delivery_orders d ON o.order_id = d.order_id
    WHERE o.user_id = %s AND o.order_status != 'completed'
    """
    cursor.execute(sql_orders, (user_id,))
    return cursor.fetchall()
    
def getOrderListDetail(order_id):
    """
    获取用户的订单詳情
    """
    sql = """
    SELECT food.f_name, order_details.quantity, order_details.price, SUM(order_details.price * order_details.quantity) AS sum
    FROM order_details 
    JOIN food ON order_details.food_id = food.food_id
    WHERE order_id = %s
    GROUP BY order_details.food_id, food.f_name, order_details.quantity, order_details.price;
    """
    cursor.execute(sql, (order_id,))
    return cursor.fetchall()

def getReviewNeed(order_id):
    """
    获取評論頁面所需資訊
    """
    sql = "SELECT order_id, total_price FROM orders WHERE order_id = %s"
    cursor.execute(sql, (order_id,))
    return cursor.fetchall()
    
def addToReview(data):
    """
    把評論加入資料庫
    """
    sql = "INSERT INTO review (user_id, order_id, review_date, grade, review) VALUES (%s, %s, NOW(), %s, %s)"
    cursor.execute(sql, (data['user_id'], data['order_id'], data['grade'], data['review']))
    conn.commit()

def getReview():
    """
    获取評論(用評分進行降序排列，次要以編號進行升序排列)
    """
    sql = """
    SELECT review.review_id, user.username, orders.total_price, review.review_date, review.grade, review.review
    FROM review 
    JOIN user ON user.id = review.user_id 
    JOIN orders ON orders.order_id = review.order_id 
    ORDER BY review.grade DESC, review.review_id ASC
    """
    cursor.execute(sql)
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

def addDeliveryOrder(order_id, delivery_user_id):
    """
    分配訂單給外送員，插入到 delivery_orders 表
    """
    sql = """
    INSERT INTO delivery_orders (order_id, delivery_user_id, delivery_status, pickup_time, delivery_time)
    VALUES (%s, %s, 'accepted', NULL, NULL)
    """
    cursor.execute(sql, (order_id, delivery_user_id))
    conn.commit()
    return cursor.lastrowid

def getOwnDeliveryOrders(delivery_user_id):
    """
    查詢當前登入外送員接的訂單
    """
    sql = "SELECT * FROM delivery_orders WHERE delivery_status = 'accepted' AND delivery_user_id = %s"
    cursor.execute(sql,(delivery_user_id,))
    return cursor.fetchall()

def getOwnDeliveryOrders_ing(delivery_user_id):
    """
    查詢當前登入外送員外送中的訂單
    """
    sql = "SELECT * FROM delivery_orders WHERE delivery_status = 'in_delivery' AND delivery_user_id = %s"
    cursor.execute(sql,(delivery_user_id,))
    return cursor.fetchall()

def getOwnDeliveryOrders_end(delivery_user_id):
    """
    查詢當前登入外送員已完成的訂單
    """
    sql = "SELECT * FROM delivery_orders WHERE delivery_status = 'completed' AND delivery_user_id = %s"
    cursor.execute(sql,(delivery_user_id,))
    return cursor.fetchall()

def update_delivery_status_and_time(delivery_id, new_status, field_to_update, time_value):
    """
    更新外送訂單的狀態和指定時間欄位。
    :param delivery_id: 外送編號
    :param new_status: 新的狀態
    :param field_to_update: 需要更新的時間欄位（例如 pickup_time 或 delivery_time）
    :param time_value: 當前時間值
    """
    sql = f"""
            UPDATE delivery_orders
            SET delivery_status = %s, {field_to_update} = %s
            WHERE delivery_id = %s
        """
    cursor.execute(sql, (new_status, time_value, delivery_id))
    conn.commit()


###備用商家，不用可刪
def getAllItemList():
    sql = "SELECT * FROM food"
    cursor.execute(sql)
    return cursor.fetchall()
    

# 关闭数据库连接（程序结束时调用）
def closeConnection():
    """
    关闭数据库连接
    """
    cursor.close()
    conn.close()
