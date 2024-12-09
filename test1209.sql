-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 09, 2024 at 06:07 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- 设置字符集和排序规则
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- 
-- 数据库：`fooddelivery`
-- 
CREATE DATABASE IF NOT EXISTS `fooddelivery` CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `fooddelivery`;

-- --------------------------------------------------------

-- 
-- 表结构：`user`
-- 
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,          -- 用户ID，自增主键
  `username` varchar(50) NOT NULL,               -- 用户名
  `password` varchar(255) NOT NULL,              -- 密码
  `role` enum('merchant', 'customer', 'delivery') NOT NULL, -- 用户角色
  `contact_info` varchar(100),                   -- 联系方式
  PRIMARY KEY (`id`)                             -- 设置主键
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

-- 
-- 表结构：`food`
-- 
CREATE TABLE `food` (
  `food_id` int(11) NOT NULL AUTO_INCREMENT,     -- 菜品ID，自增主键
  `merchant_id` int(11) NOT NULL,                -- 商家ID，外键
  `f_name` varchar(100) NOT NULL,                -- 菜品名称
  `f_price` decimal(10, 2) NOT NULL,             -- 菜品价格
  `f_content` text,                              -- 菜品描述
  PRIMARY KEY (`food_id`),                       -- 设置主键
  FOREIGN KEY (`merchant_id`) REFERENCES `user`(`id`) -- 外键关联商家
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

-- 
-- 表结构：`car`
-- 
CREATE TABLE `car` (
  `cart_id` int(11) NOT NULL AUTO_INCREMENT,     -- 购物车ID，自增主键
  `user_id` int(11) NOT NULL,                    -- 用户ID，外键
  `food_id` int(11) NOT NULL,                    -- 菜品ID，外键
  `quantity` int(11) NOT NULL,                   -- 数量
  PRIMARY KEY (`cart_id`),                       -- 设置主键
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`), -- 外键关联用户
  FOREIGN KEY (`food_id`) REFERENCES `food`(`food_id`) -- 外键关联菜品
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

-- 
-- 表结构：`orders`
-- 
CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL AUTO_INCREMENT,    -- 订单ID，自增主键
  `user_id` int(11) NOT NULL,                    -- 用户ID，外键
  `total_price` decimal(10, 2) NOT NULL,         -- 总金额
  `order_date` datetime NOT NULL,                -- 下单时间
  `order_status` enum('pending', 'completed', 'in_delivery') DEFAULT 'pending', -- 订单状态
  PRIMARY KEY (`order_id`),                      -- 设置主键
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) -- 外键关联用户
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

-- 
-- 表结构：`order_details`
-- 
CREATE TABLE `order_details` (
  `detail_id` int(11) NOT NULL AUTO_INCREMENT,   -- 订单详情ID，自增主键
  `order_id` int(11) NOT NULL,                   -- 订单ID，外键
  `food_id` int(11) NOT NULL,                    -- 菜品ID，外键
  `quantity` int(11) NOT NULL,                   -- 数量
  `price` decimal(10, 2) NOT NULL,               -- 菜品单价
  PRIMARY KEY (`detail_id`),                     -- 设置主键
  FOREIGN KEY (`order_id`) REFERENCES `orders`(`order_id`), -- 外键关联订单
  FOREIGN KEY (`food_id`) REFERENCES `food`(`food_id`) -- 外键关联菜品
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

-- 
-- 表结构：`feedback`
-- 
CREATE TABLE `feedback` (
  `feedback_id` int(11) NOT NULL AUTO_INCREMENT, -- 评价ID，自增主键
  `food_id` int(11) NOT NULL,                    -- 菜品ID，外键
  `user_id` int(11) NOT NULL,                    -- 用户ID，外键
  `rating` int(11) NOT NULL,                     -- 评分（1-5星）
  `comments` text,                               -- 评价内容
  `feedback_date` datetime NOT NULL,             -- 评价时间
  PRIMARY KEY (`feedback_id`),                   -- 设置主键
  FOREIGN KEY (`food_id`) REFERENCES `food`(`food_id`), -- 外键关联菜品
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) -- 外键关联用户
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

-- 
-- 表结构：`payments`
-- 
CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL AUTO_INCREMENT,  -- 结算记录ID，自增主键
  `user_id` int(11) NOT NULL,                    -- 用户ID，外键
  `amount` decimal(10, 2) NOT NULL,              -- 金额
  `payment_date` datetime NOT NULL,              -- 结算时间
  `payment_type` enum('merchant_income', 'delivery_income', 'platform_fee') NOT NULL, -- 结算类型
  PRIMARY KEY (`payment_id`),                    -- 设置主键
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) -- 外键关联用户
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- 
-- 提交事务
-- 
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
